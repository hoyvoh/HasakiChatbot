import requests
import json
from os import getenv
import sys
import time
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from prompt import AwanAPI, OpenAIClient
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL")
client = OpenAIClient()
print("MiniLM decide flow:", MODEL)

def get_decision(query):
    guide = guide = '''
    Phân tích yêu cầu người dùng theo các mục dưới đây và trả kết quả tương ứng theo định dạng JSON. Không thay đổi kết quả.

    (0) Nếu người dùng hỏi một câu chào hỏi bình thường, trả lại: {'signal':0, 'query':'<câu hỏi>'}.

    (1) Nếu người dùng hỏi về sản phẩm có tên cụ thể, trả lời: {'signal':1,'product_term':'<tên sản phẩm>', 'brand':'<Nhãn hiệu>', 'origin':'xuất xứ', 'sort':'<sort argument>'}.
        Với sort argument như sau:
        - 'price_desc' nếu sản phẩm mắc nhất
        - 'price_asc' nếu sản phẩm rẻ nhất
        - 'topsale' nếu sản phẩm hot nhất
        - 'position' nếu sản phẩm mới nhất

    (2) Nếu người dùng so sánh nhiều sản phẩm, trả lời: {'signal':2,'product_term_1':'<sản phẩm 1>', 'product_term_2':'<sản phẩm 2>', ..., 'product_term_n':'<sản phẩm n>'}.
    - Cung cấp đầy đủ tên sản phẩm như: 'sửa rửa mặt cerave', 'sửa rửa mặt svr'.

    (3) Nếu người dùng tìm sản phẩm theo yêu cầu, trả lời: {'signal':3,'product_term':'<sản phẩm>', 'product_ingredients':'<thành phần>', 'price':'<giá>', 'operator_price':'<operator>', 'rating':'<rating>', 'operator_rating':'<operator>', 'brand':'<Nhãn hiệu>', 'origin':'xuất xứ', 'sort':'<sort argument>', 'others':'<thông tin khác>'}.
    - Operator: $gte, $lte cho giá hoặc rating
    - Giá: Chuyển thành số (ví dụ, 10k thành 10000)

    (4) Nếu người dùng cần hỗ trợ hãy trả lời với cú pháp: {'signal':4,'query':'<loại vấn đề cần hỗ trợ>'}. Trong đó loại <loại vấn đề cần hỗ trợ> phải thuộc 1 trong các vấn đề sau: "Tài khoản, Đặt hàng trực tuyến, Quy cách đóng gói sản phẩm, Vận chuyển 2H, Phí vận chuyển, Đổi trả và hoàn tiền, Dịch vụ Spa, Tuyển dụng, Hướng dẫn đăng ký thành viên Hasaki, Có cần đặt lịch trước khi đến spa, Tại sao không thể đăng nhập vào tài khoản, Cách đặt dịch vụ, Sử dụng chung tài khoản với người khác có được không, Khám da tại spa Hasaki có tốn phí không, Giới thiệu về Hasaki, Khách hàng thân thiết, Hướng dẫn đổi quà, Hướng dẫn mua hàng, Hướng dẫn đặt hàng 2H, Hướng dẫn thanh toán trực tuyến, Thẻ quà tặng Got It, Phiếu mua hàng, Chính sách vận chuyển giao nhận, Điều khoản sử dụng, Chính sách bảo mật, Hướng dẫn tải và sử dụng App Hasaki", hãy đọc thật kỹ và lựa chọn đúng vấn đề cần hỗ trợ của khách hàng.
    
    (5) Nếu người dùng có ngân sách và cần hỗ trợ mua hàng, trả lời: {'signal':5,'budget':'<ngân sách>','product_term':'<danh sách sản phẩm>'}.
    - Ngân sách: Số hoặc chuỗi có thể chuyển thành int.
    - Product term: Các danh mục sản phẩm (tối đa 3 danh mục).

    Nếu yêu cầu không cụ thể, trả lại theo số (3).
    '''

    json_response = client.get_json_from_prompt(user_message=query, prompt=guide)
    return json_response

if __name__ == '__main__':
    print(get_decision('Tôi nên mua sản phẩm nào: kem chống nắng lapoche, kem chống nắng hada, kem chống nắng sunplay, kem đánh răng')) 
    
