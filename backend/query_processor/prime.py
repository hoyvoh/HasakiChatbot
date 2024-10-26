'''
This module handles basic flow from user
'''
import sys
import time
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv
load_dotenv()
from .minilm import get_decision
from prompt import PROMPT_TEMPLATE, AwanAPI
import regex as re
import string
from pyvi import ViTokenizer

LARGE_MODEL = os.getenv('MODEL_NAME_LARGE')
awan = AwanAPI(model_name=LARGE_MODEL)
print('using', LARGE_MODEL)

def switch(signal, message):
    metadata = {}
    print(signal)
    if signal == 1:
        # flow 1
        # handle message in structure
        product = re.sub(rf'[{string.punctuation}\n\t]','',message.strip().lower())
        product = ViTokenizer.tokenize(product)
        print(product)

        # embed product term PhoBERT

        # query embedding in Product Index (Title +  ID) => top 1 product id

        # query ID in product collection => metadata

        # sample metadata
        metadata = {
            'pname':product
        }

    elif signal == 2:
        pass
    elif signal == 4:
        pass
    elif signal == 5:
        pass
    else: # signal == 3
        pass
    return metadata

    

def get_document(query):
    # Call MiniLM for classification
    decided_string = get_decision(query)
    print(decided_string)
    
    # analyze str => flow to go
    signal = decided_string.split(',')[0]
    message = decided_string.split(',')[:-1]
    
    document = switch(signal, message)
    print(document)
    
    return document

def generate_answer(query, awan):
    document = get_document(query)

    # call prompt here to get answer
    guide = PROMPT_TEMPLATE.format(document)
    chat_response = awan.get_response(guide,query)
    answer = chat_response.get('choices')[0]['message']['content']

    return answer

if __name__ == '__main__':
    print(generate_answer('Dầu gội đầu thảo dược Thái Dương nay có khuyến mãi gì không?', awan))