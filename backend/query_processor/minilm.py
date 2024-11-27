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

    (4) Nếu người dùng cần hỗ trợ hãy trả lời với cú pháp: {'signal':4,'query':'<loại vấn đề cần hỗ trợ>'}.
    Trong đó loại <loại vấn đề cần hỗ trợ> bắt buộc phải thuộc 1 trong 26 vấn đề dưới đây:
        1. 'Tài khoản',
        2. 'Đặt hàng trực tuyến',
        3. 'Quy cách đóng gói sản phẩm',
        4. 'Vận chuyển 2H',
        5. 'Phí vận chuyển',
        6. 'Đổi trả và hoàn tiền',
        7. 'Dịch vụ Spa',
        8. 'Tuyển dụng',
        9. 'Hướng dẫn đăng ký thành viên Hasaki.',
        10. 'Có cần đặt lịch trước khi đến spa?',
        11. 'Tại sao không thể đăng nhập vào tài khoản?',
        12. 'Cách đặt dịch vụ.',
        13. 'Sử dụng chung tài khoản với người khác có được không?',
        14. 'Khám da tại spa Hasaki có tốn phí không?',
        15. 'Giới thiệu về Hasaki',
        16. 'Khách hàng thân thiết',
        17. 'Hướng dẫn đổi quà',
        18. 'Hướng dẫn mua hàng',
        19. 'Hướng dẫn đặt hàng 2H',
        20. 'Hướng dẫn thanh toán trực tuyến',
        21. 'Thẻ quà tặng Got It',
        22. 'Phiếu mua hàng',
        23. 'Chính sách vận chuyển giao nhận',
        24. 'Điều khoản sử dụng',
        25. 'Chính sách bảo mật',
        26. 'Hướng dẫn tải và sử dụng App Hasaki'
    Hãy đọc thật kỹ câu hỏi của khách hàng và lựa chọn đúng vấn đề cần hỗ trợ của khách hàng. Phải phân tích kỹ.
    
    (5) Nếu người dùng có ngân sách và cần hỗ trợ mua hàng, trả lời: {'signal':5,'budget':'<ngân sách>','product_term':'<danh sách sản phẩm>'}.
    - Ngân sách: Số hoặc chuỗi có thể chuyển thành int.
    - Product term: Các danh mục sản phẩm (tối đa 3 danh mục).

    Nếu yêu cầu không cụ thể, trả lại theo số (3).
    '''

    json_response = client.get_json_from_prompt(user_message=query, prompt=guide)
    return json_response

if __name__ == '__main__':
    print(get_decision('Tôi nên mua sản phẩm nào: kem chống nắng lapoche, kem chống nắng hada, kem chống nắng sunplay, kem đánh răng')) 
    
