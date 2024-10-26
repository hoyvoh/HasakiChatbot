import requests
import json
from os import getenv
import sys
import time
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from prompt import AwanAPI
from dotenv import load_dotenv
load_dotenv()


MODEL_NAME = getenv('MODEL_NAME_MINI')
AWANLLM_API_KEY = getenv('AWANLLM_API_KEY')
miniAwan = AwanAPI(model_name=MODEL_NAME)
print(MODEL_NAME)

def get_decision(query):
    guide = '''
    Phân tích yêu cầu người dùng theo nhu cầu sau và trả kết quả tương ứng như mô tả. Không thêm bớt hay tự chế ra kết quả.
    thay thế cụm có dấu <>, không kèm dấu này, thông tin không biết điền token[0]
    (1) Nếu người dùng nhắc đến việc tìm hiểu một sản phẩm rất cụ thể, hãy trả lời với cú pháp: 1,<tên sản phẩm>
    (2) Nếu người dùng nhắc đến việc so sánh hai sản phẩm rất cụ thể, hãy trả lời với cú pháp: 2,<thông tin sản phẩm 1>,<thông tin sản phẩm 2>
    (3) Nếu người dùng nhắc đến việc tìm sản phẩm theo yêu cầu:
        hãy trả về theo cú pháp: 3,<loại sản phẩm>,price:<price>,<rating>,<thông tin khuyến mãi>,<thông tin khác>
    (4) Nếu người dùng cần hỗ trợ về các chính sách mua hàng, giao hàng, đổi trả, hỗ trợ kỹ thuật, hãy trả lời với cú pháp: 4,<query>
    (5) Nếu người dùng cung cấp một số tiền và cần hỗ trợ mua hàng dựa trên số tiền hiện có, hãy trả lời với cú pháp: 5,<budget>,<thông tin sản phẩm>
    Nếu yêu cầu không cụ thể, trả lại theo cú pháp: 3,<loại sản phẩm>,<thông tin khác>
    '''
    response = miniAwan.get_response(guide, query)
    return response.get('choices')[0]['message']['content']


if __name__ == '__main__':
    print(get_decision('Son kem lỳ BBIA màu đỏ boss hay Innisfree?')) # 
    
