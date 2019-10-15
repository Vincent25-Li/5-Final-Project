import os
import pickle
import re

import pandas as pd
import numpy as np

import jieba
jieba.set_dictionary('dict.txt')

from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity

from app_tripblog.models import ChatbotQA_ch
from django.conf import settings


class ChatbotObject():
    def __init__ (self):

        self.qa_index = np.array(ChatbotQA_ch.objects.values_list('id'))
        self.questions = pd.DataFrame(ChatbotQA_ch.objects.all().values())
        self.category_id = np.array(ChatbotQA_ch.objects.values_list('chatbot_category_id'))
        self.all_terms = []
        self.questions['chatbot_question'] = self.questions['chatbot_question'].apply(self.jiebacut_all)
        
        # 建立termindex: 將all_terms取出不重複的詞彙，並轉換型別為list(避免順序亂掉)
        self.termindex = list(set(self.all_terms))
        self.Idf_vector = [] ## 初始化IDF向量
        self.idf()
        
        self.questions['vector'] = self.questions['chatbot_question'].apply(self.tfidf)
        
        
        # print(len(self.Idf_vector))
        # print(len(self.termindex))
        # print(self.termindex[:10])
        # print(self.Idf_vector[:10])
        
            
    def jiebacut_all(self,item):
        terms = [t for t in jieba.cut(item, cut_all=True)]
        self.all_terms.extend(terms)
        return terms
    
    def idf(self):
        Doc_Length = len(self.questions)  ## 計算出共有幾篇文章
        # 建立一條與termsindex等長、但值全部為零的向量(hint:dtype=np.float32)
        for term in self.termindex:  ## 對index中的詞彙跑回圈
            num_of_doc_contains_term = 0  ## 計算有機篇文章出現過這個詞彙
            for terms in self.questions['chatbot_question']:
                if term in terms:
                    num_of_doc_contains_term += 1
            idf = np.log(Doc_Length/num_of_doc_contains_term)  ## 計算該詞彙的IDF值
            self.Idf_vector.append(idf)
        
        
    
    def tfidf(self,terms):
        vector = np.zeros_like(self.termindex, dtype=np.float32)
        for term, count in Counter(terms).items():
            # 計算vector上每一個字的tf值
            try:
                vector[self.termindex.index(term)] = count
            except ValueError:
                count = 0
        # 計算tfidf，element-wise的將vector與Idf_vector相乘
        vector = vector * self.Idf_vector
        return vector
    
    def reply(self, user_msg):
        pattern = r"[x][;]\'\>(.*)\<\/[s]"
        x = re.search(pattern, user_msg)
        user_msg_str = x.group(1)
        
        PK_question = self.qa_index.reshape(-1, 1)
        y_category = self.category_id.reshape(-1, 1)
        x_train = self.questions['vector'].to_numpy()
        x_train = np.vstack(x_train)
        user_msg_processed = self.jiebacut_all(user_msg_str)
        user_msg_vectorized = self.tfidf(user_msg_processed)
        user_vectorize_reshape = user_msg_vectorized.reshape(1, -1)

        similarity = cosine_similarity(x_train, user_vectorize_reshape)
        reply_index = PK_question[np.argmax(similarity)]
        
        print(reply_index)
        
        if y_category[np.argmax(similarity)].tolist()[0] == 2:
            print('跳轉到編輯功能')
        else:
            reply = ChatbotQA_ch.objects.values_list('chatbot_answer').get(id=reply_index)
            return reply
        
        #reply = ChatbotQA.objects.values_list('chatbot_answer').get(id=reply_index)
        #return reply