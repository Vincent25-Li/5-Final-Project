import os

import yaml
import pandas as pd
import numpy as np
import sqlalchemy as db



# parse and load yaml file
def load_corpus(file_path):
    with open(file_path, 'r') as file:
        corpus = yaml.safe_load(file)
    return corpus

def category_writein(corpus):
    try:
        query = db.insert(table_category).values(category=corpus['categories'][0])
        proxy = connection.execute(query)
        if proxy.rowcount == 1:
            print(f"Write in category: {corpus['categories']}")
    except:
        print('error!')

def QA_writein(corpus):
    category = corpus['categories'][0]
    query = db.select([table_category.columns.PK_category]).where(table_category.columns.category==category)
    PK_category = connection.execute(query).fetchall()[0][0]
    
    for conversation in corpus['conversations']:
        conversation_count = len(conversation)
        for i in range(conversation_count-1):
            query = db.insert(table_qa_pairs).values(FK_category=PK_category, question=conversation[i], answer=conversation[i+1])
            proxy = connection.execute(query)

    print('Write in sucessfully')

def main(file_path):

    corpus = load_corpus(file_path)

    category_writein(corpus)

    QA_writein(corpus)



if __name__ == '__main__':
    languages = ['english', 'chinese']
    for language in languages:
        # create database engine
        engine = db.create_engine(f'mysql+pymysql://root:root@localhost:3306/chatbot_{language}') # connect string: mysql+pymysql://<username>:<password>@<host>/<dbname>[?<options>]

        # establish connection
        connection = engine.connect()

        # get metabase
        metadata = db.MetaData()

        # get Table 'class'
        table_category = db.Table('table_category', metadata, autoload=True, autoload_with=engine)
        table_qa_pairs = db.Table('table_qa_pairs', metadata, autoload=True, autoload_with=engine)


        base_directory = f'./{language}'
        file_list = os.listdir(base_directory)
        for file in file_list:
            path = os.path.join(base_directory, file)
            
            main(path)