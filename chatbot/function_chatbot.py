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
        #chatbot_clf_path = os.path.join(settings.MEDIA_ROOT, 'chatbot', 'topic_clf_RF.pkl')

        #self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_df=0.3)
        #self.classifier = pickle.load(open(chatbot_clf_path, 'rb'))
        self.qa_index = np.array(ChatbotQA_ch.objects.values_list('id'))
        self.questions = np.array(ChatbotQA_ch.objects.values_list('chatbot_question'))
        self.category_id = np.array(ChatbotQA_ch.objects.values_list('chatbot_category_id'))
        self.all_terms = []
        
        # transform to tfidf
        self.questions_tfidf = self.tfidf(self.jiebacut_all(self.questions))

    # transform raw text into TFIDF
    # sentences: numpy 2-D array
    
    def jiebacut_all(self,item):
        terms = [t for t in jieba.cut(item, cut_all=True)]
        self.all_terms.extend(terms)
        return terms
    
    def tfidf(self,terms):
        # 建立termindex: 將all_terms取出不重複的詞彙，並轉換型別為list(避免順序亂掉)
        termindex = list(set(self.all_terms))
        Doc_Length = len(self.questions)  ## 計算出共有幾篇文章
        Idf_vector = []  ## 初始化IDF向量
        for term in termindex:  ## 對index中的詞彙跑回圈
            num_of_doc_contains_term = 0  ## 計算有機篇文章出現過這個詞彙
            for terms in self.jiebacut_all(self.questions):
                if term in terms:
                    num_of_doc_contains_term += 1
            idf = np.log(Doc_Length/num_of_doc_contains_term)  ## 計算該詞彙的IDF值
            Idf_vector.append(idf)
        # 建立一條與termsindex等長、但值全部為零的向量(hint:dtype=np.float32)
        vector = np.zeros_like(termindex, dtype=np.float32)
        for term, count in Counter(terms).items():
            # 計算vector上每一個字的tf值
            try:
                vector[termindex.index(term)] = count
            except ValueError:
                count = 0
        # 計算tfidf，element-wise的將vector與Idf_vector相乘
        vector = vector * Idf_vector
        return vector
    
    def reply(self, user_msg):
        PK_question = self.questions.reshape(-1, 1)
        y_category = self.category_id.reshape(-1, 1)
        user_msg_processed = self.data_process(np.array([user_msg]).reshape(-1, 1))
        print(user_msg_processed)

        user_msg_vectorized = self.tfidf(self.jiebacut_all(user_msg_processed))
        #user_msg_pred = self.classifier.predict(user_msg_vectorized)

        #search_index = self.category_id == user_msg_pred
        #search_questions = self.questions_tfidf[np.ravel(search_index)]
        #search_qa_index = self.qa_index[search_index]

        similarity = cosine_similarity(self.questions_tfidf, user_msg_vectorized)
        reply_index = PK_question[np.argmax(similarity)]
        
        
        if y_category[np.argmax(similarity)].tolist()[0] == 18:
            print('跳轉到編輯功能')
        else:
            reply = ChatbotQA_ch.objects.values_list('chatbot_answer').get(id=reply_index)
            return reply
        
        #reply = ChatbotQA.objects.values_list('chatbot_answer').get(id=reply_index)
        #return reply


