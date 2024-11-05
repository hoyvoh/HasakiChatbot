import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv

load_dotenv()

# from .minilm import get_decision
from . import minilm
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
        product = str(message['product_term'])
        product = ViTokenizer.tokenize(product)

        # query embedding in Product Index (Title +  ID) => top 1 product id
        pid = pc.query_index_name_to_id(query=product)
        # query ID in product collection => metadata
        metadata = mongo.query_pid(pid)

    elif signal == 2:
        pass
    elif signal == 4:
        pass
    elif signal == 5:
        '''
        (5) Nếu người dùng cung cấp một số tiền và cần hỗ trợ mua hàng dựa trên số tiền hiện có, hãy trả lời với cú pháp: 
        {'signal':'5','budget':'<budget>','product_term':'<Danh sách các term về sản phẩm>'}; 
        chú ý, budget phải là một con số hoặc một string có thể chuyển thành int một cách trực tiếp.
        product term ở đây là một danh sách các sản phẩm gồm sản phẩm đầu là sản phẩm chính và các sản phẩm sau là 
        sản phẩm mà người dùng có thể cũng mua chung
        '''
        budget = message['budget']
        product_terms = ViTokenizer.tokenize(message['product_term']).split(',')
        namespace = 'product-desc-namespace'
        product_ids = []

        for product_term in product_terms:
            pids = pc.query_index_name_to_id(namespace=namespace, query=product_term, topk=10)
            product_ids.extend(pids)
        
        product_ids = list(set(product_ids))
        metadata = mongo.query_relevant_products_within_budget(product_ids=product_ids, budget=budget)

    else: # signal == 3
        metadata = {
            'product':message['product_term']
        }
    return metadata


def get_document(query, pc, mongo):
    decided_json = minilm.get_decision(query)
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
