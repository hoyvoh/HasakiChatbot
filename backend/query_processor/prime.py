import sys
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

def switch(signal, message, pc, mongo):
    metadata = {}
    print('signal:', signal)
    if signal == 0:
        return ''
    elif signal == 1:
        # flow 1
        # handle message in structure
        product = str(message['product_term'])
        product = ViTokenizer.tokenize(product)

        # embed product term PhoBERT
        index_name = 'product-pname-index'

        # query embedding in Product Index (Title +  ID) => top 1 product id
        pid = pc.query_index_name_to_id(indexname=index_name, query=product)

        # query ID in product collection => metadata
        metadata = mongo.query_pid(pid)

    elif signal == 2:
        pass
    elif signal == 4:
        pass
    elif signal == 5:
        pass
    else: # signal == 3
        pass
    return metadata


def get_document(query, pc, mongo):
    decided_json = get_decision(query)
    signal = int(decided_json['signal'])
    message = decided_json
    document = switch(signal, message, pc, mongo)
    return document

def generate_answer(query, awan, pc, mongo):
    document = get_document(query, pc, mongo)
    guide = PROMPT_TEMPLATE.format(document)
    chat_response = awan.get_response(guide,query)
    answer = chat_response.get('choices')[0]['message']['content']

    return answer

if __name__ == '__main__':
    #print(generate_answer('Dầu gội đầu thảo dược Thái Dương nay có khuyến mãi gì không?', awan))
    print(generate_answer('Hôm trước mua dầu gội bên Hasaki mà chất lượng kém quá, muốn trả hàng mà làm nọ làm kia. Làm sao để gửi báo cáo?', awan))
