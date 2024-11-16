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
    thay thế cụm có dấu <>, không kèm dấu này, câu trả lời theo dạng json format.
    (0) Nếu người dùng chỉ hỏi một câu chào hỏi lịch sự bình thường, hãy trả lại với cú pháp: {'signal':'0', 'query':'<câu hỏi>'}
    (1) Nếu người dùng nhắc đến việc tìm hiểu một sản phẩm rất cụ thể, hãy trả lời với cú pháp: {'signal':'1','product_term':'<tên sản phẩm>'}
    (2) Nếu người dùng nhắc đến việc so sánh hai sản phẩm rất cụ thể, hãy trả lời với cú pháp: {'signal':'2','product_term_1'='<thông tin sản phẩm 1>','product_term_2'='<thông tin sản phẩm 2>'}
    (3) Nếu người dùng nhắc đến việc tìm sản phẩm theo yêu cầu:
        hãy trả về các thuộc tính có trong cú pháp sau (nếu có), trong đó signal và product_term là bắt buộc: {'signal':'3','product_term':'<thông tin sản phẩm>', 'product_ingredients': '<thành phần sản phẩm>','price':'<price>', 'operator_price':'<operator>', 'rating':'<rating>', 'operator_rating':'<operator>', 'others':'<thông tin khác>'}
        Lưu ý <operator> sẽ là các operator trong mongodb như '$gte', '$lte' khi câu hỏi liên quan đến giá lớn hơn, bé hơn bao nhiêu đó. Hoặc rating cao hơn hay thấp hơn bao nhiêu đó.
        Và <price> phải được chuyển về theo dạng ví dụ 10k là 10000.
    (4) Nếu người dùng cần hỗ trợ về các chính sách mua hàng, giao hàng, đổi trả, hỗ trợ kỹ thuật, hãy trả lời với cú pháp: {'signal':'4','query':'<query>'}
    (5) Nếu người dùng cung cấp một số tiền và cần hỗ trợ mua hàng dựa trên số tiền hiện có, hãy trả lời với cú pháp: 
    {'signal':'5','budget':'<budget>','product_term':'<Danh sách các term về sản phẩm>'}; 
    chú ý, budget phải là một con số hoặc một string có thể chuyển thành int một cách trực tiếp.
    product term ở đây là một danh sách các sản phẩm gồm sản phẩm đầu là sản phẩm chính và các sản phẩm sau là sản phẩm mà người dùng có thể cũng mua chung được cách nhau bởi dấu phẩy
    
    Nếu yêu cầu không cụ thể về sản phẩm nào, trả lại theo cú pháp: {'signal':'3','product_term':'<mô tả sản phẩm>','others':'<thông tin khác>'}

    '''
    response = miniAwan.get_response(guide, query, mode="text")
    content = response.get('choices')[0]['message']['content']
    
    json_response=json.loads(content.replace("'", '"'))
    return json_response

if __name__ == '__main__':
    print(get_decision('Son kem lỳ BBIA màu đỏ boss hay son bóng Innisfree?')) 
    
