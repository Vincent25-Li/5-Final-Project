import os

import yaml
import pandas as pd
import numpy as np
from app_tripblog.models import ChatbotCategory, ChatbotQA


# parse and load yaml file
def load_corpus(file_path):
    with open(file_path, 'r') as file:
        corpus = yaml.safe_load(file)
    return corpus

def category_writein(corpus):
    print(f"Write in category: {corpus['categories']}")
    category = ChatbotCategory(chatbot_category=corpus['categories'][0])
    category.save()
    return category

def QA_writein(corpus, category):
    for conversation in corpus['conversations']:
        conversation_count = len(conversation)
        for i in range(conversation_count-1):
            qa = ChatbotQA(
                chatbot_category=category,
                chatbot_question=conversation[i],
                chatbot_answer=conversation[i+1]
            )
            qa.save()
    print('Write in sucessfully')

def main(file_path):

    corpus = load_corpus(file_path)

    category = category_writein(corpus)

    QA_writein(corpus, category)



if __name__ == '__main__':

    base_directory = '../chatbot/data/english'
    file_list = os.listdir(base_directory)
    for file in file_list:
        path = os.path.join(base_directory, file)
        main(path)