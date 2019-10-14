import os
import pickle
import re

import numpy as np
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics.pairwise import cosine_similarity

from app_tripblog.models import ChatbotQA
from django.conf import settings

class ChatbotObject():
    def __init__ (self):
        chatbot_clf_path = os.path.join(settings.MEDIA_ROOT, 'chatbot', 'topic_clf_RF.pkl')

        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_df=0.3)
        self.classifier = pickle.load(open(chatbot_clf_path, 'rb'))
        self.qa_index = np.array(ChatbotQA.objects.values_list('id'))
        self.questions = np.array(ChatbotQA.objects.values_list('chatbot_question'))
        self.category_id = np.array(ChatbotQA.objects.values_list('chatbot_category_id'))

        # transform to tfidf
        self.questions_tfidf = self.vectorizer.fit_transform(self.data_process(self.questions))

    # transform raw text into TFIDF
    # sentences: numpy 2-D array
    def data_process(self, sentences):
        sentences_wo_div = np.array(list(map(
            lambda x: [re.sub('<[^>]*>', '', x[0])], sentences 
        ))) # remove div tag

        sentences_wo_p = np.array(list(map(
            lambda x: [re.sub('[^\w\s]', '', x[0])], sentences_wo_div
        ))) # remove punctuations
        
        sentences_split = np.array(list(map(
            lambda x: x[0].split(), sentences_wo_p
        ))) # split sentence into words
        
        st = PorterStemmer()
        words_stemmed = np.array(list(map(
            lambda x: [st.stem(word.lower()) for word in x], sentences_split
        ))) # stemming of word
        sentences_processed = np.array(list(map(
            lambda x: ' '.join(x), words_stemmed
        )))
        return sentences_processed

    def reply(self, user_msg):
        user_msg_processed = self.data_process(np.array([user_msg]).reshape(-1, 1))
        print(user_msg)

        user_msg_vectorized = self.vectorizer.transform(user_msg_processed)
        user_msg_pred = self.classifier.predict(user_msg_vectorized)

        search_index = self.category_id == user_msg_pred
        search_questions = self.questions_tfidf[np.ravel(search_index)]
        search_qa_index = self.qa_index[search_index]

        similarity = cosine_similarity(search_questions, user_msg_vectorized)
        reply_index = search_qa_index[np.argmax(similarity)]
        reply = ChatbotQA.objects.values_list('chatbot_answer').get(id=reply_index)
        return reply


