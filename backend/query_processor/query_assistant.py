import requests
from bs4 import BeautifulSoup

def normalize_query(query):
    query = query.lower()
    query = query.split(' ')
    return '-'.join(query)

def query_assistant(query, 
                    url='https://hasaki.vn/catalogsearch/result/', 
                    params={
                        'q': 'son-mau-do'
                    }, 
                    top_k = 5):
    query = normalize_query(query)  
    params['q'] = query 

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Error fetching data: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    items = soup.find_all('div', class_='item_list_cate', limit=top_k)
    product_details = []

    for item in items:
        a_tag = item.find('a', class_='v3_thumb_common_sp')

        if a_tag:
            product = {
                'url': a_tag.get('href'),
                'name': a_tag.get('data-name'),
                'price': a_tag.get('data-price'),
                'brand': a_tag.get('data-brand'),
                'category': a_tag.get('data-category-name'),
                'variant': a_tag.get('data-variant'),
            }
            product_details.append(product)
    document = []
    for product in product_details:
        document.append(f"Sản phẩm: {product['name']}")
        document.append(f"Giá: {product['price']}")
        document.append(f"Hãng: {product['brand']}")
        document.append(f"Phân loại: {product['category']}")
        document.append(f"Mẫu: {product['variant']}")
        document.append(f"Link: {product['url']}")
        document.append("-" * 40)
    document = '\n'.join(document)
    return document

# query = 'Ngừa mụn sạch sâu xóa nhòa vết nám'
# products = query_assistant(query, top_k=8)

# print(products)