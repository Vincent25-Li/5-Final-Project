import re
from collections import Counter

import pandas as pd
import numpy as np
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
# TfidfVectorizer is equivalent to CountVectorizer followed by TfidfTransformer.
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics.pairwise import cosine_similarity
import sqlalchemy as db

def db_connection():
    engine = db.create_engine('mysql+pymysql://root:root@localhost:3306/chatbot_english')
    conn = engine.connect()
    metadata = db.MetaData()
    return engine, conn, metadata

def get_table_content(table_name, engine, conn, metadata):
    table = db.Table(table_name , metadata, autoload=True, autoload_with=engine)
    table_content = conn.execute(table.select()).fetchall()
    return table, table_content

def count_category(df, column):
    category_number = len(df[column].unique())
    category_count = Counter(df[column]).most_common()
    for category, count in category_count:
        print(f'{category:14}: {count:3}')

def df2numpy(df, column):
    return df[column].to_numpy().reshape(-1, 1)

# transform raw text into TFIDF
# sentences: numpy 2-D array
def data_process(sentences):

    sentences_wo_p = np.array(list(map(
        lambda x: [re.sub('[^\w\s]', '', x[0])], sentences 
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

def prediction_accuracy(classifier, x_test, y_test):
    y_pred = classifier.predict(x_test)
    accuracy = sum(y_pred == np.ravel(y_test))/len(y_pred)
    print(f'Accuracy: {accuracy}')

def chatbot(user_text, vectorizer, classifier, PK, x, y, df):
    user_text_processed = data_process(np.array([user_text]).reshape(-1, 1))

    user_text_vectorized = vectorizer.transform(user_text_processed)
    user_text_pred = classifier.predict(user_text_vectorized)

    search_idx = y == user_text_pred
    search_question = x[np.ravel(search_idx)]
    search_PK_qa_pairs = PK[search_idx]

    similarity = cosine_similarity(search_question, user_text_vectorized)
    PK = search_PK_qa_pairs[np.argmax(similarity)]
    reply = df.loc[PK, 'answer']
    return reply


def main():

    engine, conn, metadata = db_connection()

    # load sql data in table 'table_category' and 'table_qa_pairs'
    table_category, category = get_table_content('table_category', engine, conn, metadata)
    table_qa_pairs, qa_pairs = get_table_content('table_qa_pairs', engine, conn, metadata)

    # load data in dataframe
    df_qa_pairs = pd.DataFrame(qa_pairs)
    df_qa_pairs.columns = table_qa_pairs.columns.keys()
    category_dict = {i:category for (i, category) in category}
    df_qa_pairs['category'] = df_qa_pairs['FK_category'].map(category_dict)
    

    # count_category(df_qa_pairs, column='category') # count each category numbers


    PK_question = df2numpy(df_qa_pairs, 'PK_qa_pairs') # get index of question
    x_question = df2numpy(df_qa_pairs, 'question') # training data x
    y_category = df2numpy(df_qa_pairs, 'FK_category') # training data y

    x_question_processed = data_process(x_question)

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_df=0.3)
    x = vectorizer.fit_transform(x_question_processed)
    y = y_category

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.1, random_state=0, stratify=y)
    x.shape

    clf = RandomForestClassifier(random_state=0)
    clf.fit(x_train, np.ravel(y_train))
    
    # prediction_accuracy(clf, x_test, y_test) # predict the model accuracy

    user_input = input('Hi how may I help you: ')
    reply = chatbot(user_input, vectorizer, clf, PK_question, x, y, df_qa_pairs)
    print(reply)

if __name__ == '__main__':
    main()
