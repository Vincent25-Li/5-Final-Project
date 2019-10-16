import os
import pickle
import re
import json

import pandas as pd
import numpy as np
import jieba
from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity
from scipy import sparse
from keras.preprocessing.sequence import pad_sequences
from keras.models import load_model
import tensorflow as tf

from app_tripblog.models import ChatbotQA_ch
from django.conf import settings

dict_path = os.path.join(settings.MEDIA_ROOT, 'models_weights', 'chatbot', 'dict.txt')
jieba.set_dictionary(dict_path)

tf.reset_default_graph()

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
        
        '''load parameters and model for NER'''
        self.word2idx = self.read_json(os.path.join(settings.MEDIA_ROOT, 'models_weights', 'chatbot', 'dict_trip.json'))
        self.idx2word = {i: w for w, i in self.word2idx.items()}
        self.tag2idx = self.read_json(os.path.join(settings.MEDIA_ROOT, 'models_weights', 'chatbot', 'tag_trip.json'))
        self.idx2tag = {i: t for t, i in self.tag2idx.items()}
        self.embeddings = sparse.load_npz(os.path.join(settings.MEDIA_ROOT, 'models_weights', 'chatbot', 'embeddings.npz'))

        self.ner_graph = tf.Graph()
        with self.ner_graph.as_default():
            self.ner_session = tf.Session()
            with self.ner_session.as_default():
                self.ner_model = load_model(os.path.join(settings.MEDIA_ROOT, 'models_weights', 'chatbot', 'ner_w_embedding.h5'))
        # self.ner_graph = tf.compat.v1.get_default_graph()
        
            
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

    def read_json(self, path):
        with open(path) as f:
            file = json.load(f)
        return file

    
    def get_index(self, user_msg):
        # pattern = r"[x][;]\'\>(.*)\<\/[s]"
        # x = re.search(pattern, user_msg)
        # user_msg_str = x.group(1)
        
        PK_question = self.qa_index.reshape(-1, 1)
        y_category = self.category_id.reshape(-1, 1)
        x_train = self.questions['vector'].to_numpy()
        x_train = np.vstack(x_train)
        user_msg_processed = self.jiebacut_all(user_msg)
        user_msg_vectorized = self.tfidf(user_msg_processed)
        user_vectorize_reshape = user_msg_vectorized.reshape(1, -1)

        similarity = cosine_similarity(x_train, user_vectorize_reshape)
        reply_index = PK_question[np.argmax(similarity)]
        return reply_index
    
    def chat_reply(self, reply_index):
        reply = ChatbotQA_ch.objects.values_list('chatbot_answer').get(id=reply_index)
        return reply

    def ner(self, user_msg):
        with self.ner_graph.as_default():
            with self.ner_session.as_default():
                max_len = 10
                user_msg_cut = list(jieba.cut(user_msg))
                X_msg = [self.word2idx[word] if word in self.word2idx else self.word2idx['UNK'] for word in user_msg_cut]
                X_msg_pad = pad_sequences(maxlen=max_len, sequences=[X_msg], padding='post', value=self.word2idx['ENDPAD'])
                X_msg_embed = np.array(self.embeddings[X_msg_pad[0]].toarray())[np.newaxis]
                X_msg_pad_text = [self.idx2word[idx] for idx in X_msg_pad[0]]
                y_msg_pred = self.ner_model.predict(X_msg_embed)
                y_msg_pred = np.argmax(y_msg_pred, axis=-1)[0]
                y_msg_tag = [self.idx2tag[pred] for pred in y_msg_pred]
                print(f'{X_msg_pad_text}\n{y_msg_tag}')
                return y_msg_tag

        