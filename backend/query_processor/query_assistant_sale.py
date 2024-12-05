import requests
from bs4 import BeautifulSoup

def query_assistant_sale(url='https://hasaki.vn/deals-dang-dien-ra.html'):

    #params = {}

    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error fetching data: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    items = soup.find_all('div', class_='item_deal', limit=10)
    
    product_list = []
    for item in items:
        name = item.find('div', class_='vn_names').text.strip()
    
        # Lấy thương hiệu
        brand = item.find('div', class_="width_common txt_color_1 space_bottom_3").text.strip()
        
        # Lấy giá bán
        current_price = item.find('strong', class_='item_giamoi').text.strip()
        
        # Lấy phần trăm giảm giá
        discount_percent = item.find('span', class_='discount_percent2_deal').text.strip()
        
        # Lấy giá bán trước giảm giá
        original_price = item.find('span', class_='item_giacu').text.strip()

        # Lấy link
        link = item.find('a', class_="v3_thumb_common_sp").get('href')
        
        # Lưu vào danh sách
        product_list.append({
            'pname': name,
            'brand': brand,
            'price': current_price,
            'discount': discount_percent,
            'oprice': original_price,
            'link' : link
        })
    
    document = "\nThông tin các sản phẩm hiện đang có khuyến mãi shock:\n\n"
    for product in product_list:
        document += (f"Sản phẩm: {product.get('pname')} của thương hiệu {product.get('brand')}\n"
                     f"Giá bán khuyến mãi: {product.get('price')}, được giảm {product.get('discount')} từ giá gốc {product.get('oprice')}\n"
                     f"Link sản phẩm: {product.get('link')}\n\n")
    
    return document

if __name__ == '__main__':
    query_assistant_sale()
