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
    Trong đó loại <loại vấn đề cần hỗ trợ> bắt buộc phải thuộc 1 trong 37 vấn đề hoặc câu hỏi sau: ['Đăng ký thành viên Hasaki như thế nào?', 'Tại sao tôi không thể đăng nhập vào tài khoản của tôi?', 'Tôi muốn thay đổi thông tin tài khoản thành viên như thế nào?', 'Tôi có thể sử dụng chung tài khoản với người khác được không? ', 'Đăng ký thành viên tại Hasaki.vn sẽ giúp ích gì cho tôi?', 'Hasaki có chương trình ưu đãi nào hấp dẫn dành cho khách hàng thân thiết?', 'Tôi có thể đặt hàng qua điện thoại được không?', 'Có giới hạn về số lượng sản phẩm khi đặt hàng không?', 'Tôi muốn kiểm tra lại đơn hàng đã mua?', 'Tôi muốn thay đổi hoặc hủy bỏ đơn hàng đã mua thì sao?', 'Quy cách đóng gói sản phẩm', 'Giờ làm việc của Hasaki Clinic?', 'Có cần đặt lịch trước khi đến Hasaki Clinic không?', 'Đặt mua phiếu dịch vụ như thế nào?', 'Khám da tại Hasaki Clinic có tốn phí không?', 'Những chi nhánh nào của Hasaki Clinic có bác sĩ da liễu?', 'Hasaki Clinic có chương trình gì hàng tháng?', 'Các dịch vụ thư giãn có dành cho nam không?', 'Mua dịch vụ rồi có hoàn trả được hay không?', 'Tôi cần tư vấn về dịch vụ spa và phòng khám?', 'Tôi có thể sang nhượng dịch vụ cho người khác không?', 'Vận chuyển 2H', 'Phí vận chuyển', 'Đổi trả và hoàn tiền', 'Tuyển dụng', 'Giới thiệu về Hasaki', 'Khách hàng thân thiết', 'Hướng dẫn đổi quà', 'Hướng dẫn đặt hàng', 'Hướng dẫn đặt hàng 2H', 'Hướng dẫn thanh toán trực tuyến', 'Thẻ quà tặng Got It', 'Phiếu mua hàng', 'Chính sách vận chuyển giao nhận', 'Điều khoản sử dụng', 'Chính sách bảo mật', 'Hướng dẫn tải và sử dụng App Hasaki']

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
    
