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
    guide = '''
    Phân tích yêu cầu người dùng theo nhu cầu sau và trả kết quả tương ứng như mô tả. Không thêm bớt hay tự chế ra kết quả.
    thay thế cụm có dấu <>, không kèm dấu này, câu trả lời theo dạng json format.
    (0) Nếu người dùng chỉ hỏi một câu chào hỏi lịch sự bình thường, hãy trả lại với cú pháp: {'signal':0, 'query':'<câu hỏi>'}
    (1) Nếu người dùng nhắc đến việc tìm hiểu một sản phẩm rất cụ thể, hãy trả lời với cú pháp: {'signal':1,'product_term':'<tên sản phẩm>'}
    (2) Nếu người dùng nhắc đến việc so sánh giữa nhiều sản phẩm hoặc để trả lời câu hỏi của người dùng phải so sánh giữa nhiều sản phẩm, hãy trả lời với cú pháp: {'signal':2,'product_term_1'='<thông tin sản phẩm 1>','product_term_2'='<thông tin sản phẩm 2>',..., 'product_term_n'='thông tin sản phẩm n'}. Lưu ý: trong product_term phải cho tôi biết rõ ràng đó là gì ví dụ: Khi tôi nhập câu hỏi so sánh sửa rửa mặt cerave và svr thì product_term_1 là sửa rửa mặt cerave và product_term_2 là sửa rửa mặt svr.
    (3) Nếu người dùng nhắc đến việc tìm sản phẩm theo yêu cầu:
        hãy trả về các thuộc tính có trong cú pháp sau (nếu có), trong đó signal và product_term là bắt buộc: {'signal':3,'product_term':'<thông tin sản phẩm>', 'product_ingredients': '<thành phần sản phẩm>','price':'<price>', 'operator_price':'<operator>', 'rating':'<rating>', 'operator_rating':'<operator>', 'others':'<thông tin khác>'}
        Lưu ý <operator> sẽ là các operator trong mongodb như '$gte', '$lte' khi câu hỏi liên quan đến giá lớn hơn, bé hơn bao nhiêu đó. Hoặc rating cao hơn hay thấp hơn bao nhiêu đó.
        Và <price> phải được chuyển về theo dạng ví dụ 10k là 10000.
    (4) Nếu người dùng cần hỗ trợ về các chính sách mua hàng, giao hàng, đổi trả, hỗ trợ kỹ thuật, hãy trả lời với cú pháp: {'signal':4,'query':'<query>'}
    (5) Nếu người dùng cung cấp một số tiền và cần hỗ trợ mua hàng dựa trên số tiền hiện có, hãy trả lời với cú pháp: 
    {'signal':5,'budget':'<budget>','product_term':'<Danh sách các term về sản phẩm>'}; 
    chú ý, budget phải là một con số hoặc một string có thể chuyển thành int một cách trực tiếp.
    product term ở đây là một danh sách các danh mục liên quan đến mỹ phẩm, trang điểm, dầu gội, chăm sóc da, tóc... và được cách nhau bởi dấu phẩy, dao động từ 3 đến 5 danh mục.
    Nếu yêu cầu không cụ thể về sản phẩm nào, trả lại theo cú pháp: {'signal':3, 'product_term':'<mô tả sản phẩm>','others':'<thông tin khác>'}

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
    
