import requests
import json
from os import getenv
import sys
import time
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from prompt import OpenAIClient
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL")
client = OpenAIClient()
print("MiniLM decide flow:", MODEL)

def get_decision(query):
    guide = '''
    Phân tích yêu cầu người dùng theo nhu cầu sau và trả kết quả tương ứng như mô tả. Không thêm bớt hay tự chế ra kết quả.
    thay thế cụm có dấu <>, không kèm dấu này, câu trả lời theo dạng json format.
    
    (0) Nếu người dùng hỏi một câu chào hỏi bình thường, trả lại: {'signal':0, 'query':'<câu hỏi>'}.

    (1) Nếu người dùng hỏi về sản phẩm có tên cụ thể, trả lời: {'signal':1,'product_term':'<tên sản phẩm>', 'brand':'<Nhãn hiệu>', 'origin':'xuất xứ', 'sort':'<sort argument>'}.
        Với sort argument như sau:
        - 'price_desc' nếu sản phẩm mắc nhất
        - 'price_asc' nếu sản phẩm rẻ nhất
        - 'topsale' nếu sản phẩm hot nhất
        - 'position' nếu sản phẩm mới nhất

    (2) Nếu người dùng so sánh nhiều sản phẩm, trả lời: {'signal':2,'product_term_1':'<sản phẩm 1>', 'product_term_2':'<sản phẩm 2>', ..., 'product_term_n':'<sản phẩm n>'}.
    - Cung cấp đầy đủ tên sản phẩm như: 'sửa rửa mặt cerave', 'sửa rửa mặt svr'.

    (3) Nếu người dùng nhắc đến việc tìm sản phẩm theo yêu cầu:
        hãy trả về các thuộc tính có trong cú pháp sau (nếu có), trong đó signal và product_term là bắt buộc: {'signal':3,'product_term':'<thông tin sản phẩm>', 'product_ingredients': '<thành phần sản phẩm>','price':'<price>', 'operator_price':'<operator>', 'rating':'<rating>', 'operator_rating':'<operator>', 'others':'<thông tin khác>'}
        Lưu ý <operator> sẽ là các operator trong mongodb như '$gte', '$lte' khi câu hỏi liên quan đến giá lớn hơn, bé hơn bao nhiêu đó. Hoặc rating cao hơn hay thấp hơn bao nhiêu đó.
        Và <price> phải được chuyển về theo dạng ví dụ 10k là 10000.
        Nếu không có yêu cầu về thuộc tính nào thì đừng trả thuộc tính đó lại.

    (4) Nếu người dùng cần hỗ trợ hãy trả lời với cú pháp: {'signal':4,'query':<query>}.

    Hãy đọc thật kỹ câu hỏi của khách hàng và lựa chọn đúng vấn đề cần hỗ trợ của khách hàng. Phải phân tích kỹ.
    
    (5) Nếu người dùng có ngân sách và cần hỗ trợ mua hàng, trả lời: {'signal':5,'budget':'<ngân sách>','product_term':'<danh sách sản phẩm>'}.
    - Ngân sách: Số hoặc chuỗi chuyển thành int.
    - Product term: Các danh mục sản phẩm đều phải liên quan mỹ phẩm (từ 3 đến 5 danh mục).

    Nếu yêu cầu không cụ thể, trả lại theo số (3).
    '''

    json_response = client.get_json_from_prompt(user_message=query, prompt=guide)
    return json_response

if __name__ == '__main__':
    print(get_decision('Tôi nên mua sản phẩm nào: kem chống nắng lapoche, kem chống nắng hada, kem chống nắng sunplay, kem đánh răng')) 
    
