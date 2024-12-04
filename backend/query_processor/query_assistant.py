import requests
from bs4 import BeautifulSoup

def normalize_query(query):
    query = query.lower()
    query = query.split(' ')
    return '-'.join(query)

brand_dict = {'Eucerin': '1945', 'Vichy': '205', 'La Roche-Posay': '203', 'Cocoon': '203797', "L'Oreal": '210', 'Curél': '209249', 'Acnes': '208868', 'Senka': '2972', 'Hada Labo': '2670', 'Garnier': '2295', 'Naris Cosmetics': '6963', 'Milaganics': '8732', 'Elixir': '223403', 'Caryophy': '211570', 'Avène': '199', 'Bioré': '4435', 'OXY': '208912', 'Emmié by Happy Skin': '214357', 'SVR': '135774', 'Bioderma': '1383', 'Nivea': '1946', 'JMsolution': '213079', 'Bio-essence': '2418', 'Sexylook': '202915', 'Simple': '2117', 'Selsun': '2681', 'Olay': '1878', 'Some By Mi': '210183', 'B.O.M': '209713', 'Foodaholic': '211461', 'Neutrogena': '1419', 'Vacosi': '1912', "Angel's Liquid": '211116', 'Banobagi': '217935', 'BNBG': '2386', 'Evoluderm': '206', 'Avander': '211012', 'Derladie': '212591', 'P/S': '214363', 'X-Men': '218687', 'Vaseline': '1399', 'Bông Bạch Tuyết': '223467', "Pond's": '2008', 'Klairs': '207676', '50 Megumi': '215887', 'Grace And Glow': '222126', 'CeraVe': '1990', 'Tsubaki': '210396', 'Balance Active Formula': '211995', 'Maybelline': '213', 'dProgram': '214661', 'D-na': '216263', 'Skin1004': '8277', 'Naruko': '203860', 'MAYAN': '2042', 'Listerine': '154176', 'Purederm': '1893', 'Bye Bye Blemish': '2037', 'Obagi': '205792', 'Melano CC': '208945', 'Freeplus': '215308', 'Sensodyne': '216717', 'Martiderm': '217741', 'Teana': '221262', 'Torriden': '222238', 'MEISHOKU': '4564', 'Dermal': '8496', "Paula's Choice": '1588', 'Timeless': '1941', 'LipIce': '208558', "TIA'M": '211120', 'australis': '211543', 'Clear': '212719', '16plain': '220501', 'Colorkey': '222280', 'Decumar': '225194', 'Isis Pharma': '3632', 'Mediheal': '4778', 'A-Derma': '6494', 'Cléo': '8151', 'Derma Angel': '185593', 'Head & Shoulders': '1929', 'Nature Republic': '208', 'Gamma Chemicals': '216557', 'The Lab': '218013', 'oh!oh!': '218649', 'Pekah': '218685', 'Swiss Image': '218923', 'Topicrem': '218971', 'Nguyên Xuân': '221512', 'WonJin': '222240', 'DrCeutics': '224022', 'Lanbena': '225782', 'Lebelage': '4810', 'Dove': '5386', 'Pelican': '5494', 'Silkygirl': '7093', 'By Wishtrend': '1381', 'innisfree': '1398', 'Diana': '168141', 'Pantene': '2007', 'Forencos': '206751', 'Blossomy': '210536', 'Bio-Oil': '211058', 'Hatomugi': '211574', 'Girlz Only': '211967', 'Nucos': '214311', 'Cetaphil': '215', 'Colgate': '215631', 'Neogen Dermalogy': '216161', 'Cosrx': '216737', 'Fixderma': '217981', 'Deou': '218075', 'S.O.N': '219283', 'Nerman': '219309', 'Skintific': '221028', 'Mincer Pharma': '222777', 'Beplain': '223998', "Kiehl's": '2696', 'Double Rich': '4406', 'DHC': '4566', 'Hazeline': '5359', 'TRESemmé': '5362', 'Sunplay': '7071', 'REBIRTH': '1397', 'St.Ives': '1424', 'Clean & Clear': '1989', 'Suri': '207586', 'Ducray': '208328', 'SEBAMED': '2087', 'Closeup': '214371', 'Sur.Medic+': '214833', 'Dr.Pepti': '218263', 'Vegick': '218399', 'Labiotte': '224746', 'Diane': '225778', 'Crest': '2426', 'Ciracle': '2430', 'UNO': '28758', 'Care:Nel': '3600', "It'S SKIN": '4049', 'Dental Clinic 2080': '4446', 'GoodnDoc': '4554', 'Dr.G': '5395', 'EtiaXil': '5815', 'Kosé': '6598', 'Rainbow L’affair': '7950', 'Eveline': '8589', 'Febreze': '167640', 'Pure Smile': '175309', 'Purité By Prôvence': '1913', 'Kotex': '19641', 'Byphasse': '1965', 'Gillette': '2002', 'Laneige': '204', 'Cathy Doll': '204265', 'Pharmekal': '2083', 'Happy Event': '209039', "I'm from": '209964', 'Huxley': '210860', 'Kumano': '211282', 'Eucryl': '211955', 'YOKO': '2134', 'BareSoul': '213541', 'Avatar': '214033', 'Biochem': '214039', '9Wishes': '214601', 'Floxia': '214903', 'Organic Shop': '215314', 'May Island': '215521', "L'Oreal Professionnel": '215731', 'Dongsung': '216027', 'Embryolisse': '216261', 'Welcos': '216353', 'Chifure': '216647', 'Aquafresh': '216719', 'SkinCeuticals': '217461', 'Beldora 299': '217735', 'Dr.ForHair': '217737', 'Altruist': '218241', 'Kissme': '218279', 'Fressi Care': '218425', 'Scarz': '218779', 'Boom De Ah Dah': '219021', 'Senz': '219651', 'Espoir': '219721', 'SHC': '220397', 'Perioe': '220707', 'Alfe': '221682', 'Guard Halo': '221760', 'Perfect Diary': '221788', 'Himalaya Pink Salt': '221944', 'EcoWipes': '222216', 'Bring Green': '222250', 'Cỏ Mềm': '222467', 'Catrice': '222857', 'Faroson': '223371', 'Neoaqua': '225534', 'Jomi': '2275', 'URIAGE': '2382', 'Coast': '2424', 'Arumtown': '2431', 'Batiste': '2806', 'Menard': '3729', 'Astalift': '3944', 'SHOWER MATE': '4450', 'PURITA': '4556', 'Dermatix': '4926', 'On: The Body': '5803', 'Rosette': '6674', 'Deep Fresh': '6789', 'Corine de Farme': '8346', 'YC': '8786'}

def query_assistant(query, brand=None, origin=None, sort=None,
                    url='https://hasaki.vn/catalogsearch/result/', 
                    params={
                        'q': 'son-mau-do', 
                        'filter_brand':None
                    }, 
                    top_k = 5):
    query = normalize_query(query)  
    params['q'] = query 
    
    origin_dict =  {
    'Pháp':200,
    'Mỹ':214,
    'Nhật Bản':12342,
    'Hàn Quốc':209,
    'Việt Nam':10743,
    'Đức':1968,
    'Anh':2770
    }

    if origin:
        try:
            origin_key = origin_dict[origin]
            params['filter_origin']=origin_key
        except KeyError as e:
            print('origin not matched', e)

    if brand:
        try:
            brand_key = brand_dict[brand]
            params['filter_brand']=brand_key
        except KeyError as e:
            print('brand not matched', e)
    
    if sort:
        params['sort']=sort

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Error fetching data: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    items = soup.find_all('div', class_='item_list_cate', limit=top_k)   
    
    product_details = []

    for item in items:
        a_tag = item.find('a', class_='v3_thumb_common_sp')

        discount_item = item.find('span', class_='discount_percent2_deal')
        discount_percent = discount_item.text.strip() if discount_item else ""

        original_item = item.find('span', class_='item_giacu')
        original_price = original_item.text.strip() if original_item else ""

        if a_tag:
            product = {
                'url': a_tag.get('href'),
                'name': a_tag.get('data-name'),
                'price': a_tag.get('data-price'),
                'discount': discount_percent,
                'oprice': original_price,
                'brand': a_tag.get('data-brand'),
                'category': a_tag.get('data-category-name'),
                'variant': a_tag.get('data-variant'),
            }
            product_details.append(product)
    document = []
    for product in product_details:
        document.append(f"Sản phẩm: {product['name']}")
        document.append(f"Giá đang bán: {product['price']}")
        document.append(f"Phần trăm giảm giá: {product['discount']}")
        document.append(f"Giá gốc: {product['oprice']}")
        document.append(f"Hãng: {product['brand']}")
        document.append(f"Phân loại: {product['category']}")
        document.append(f"Mẫu: {product['variant']}")
        document.append(f"Link: {product['url']}\n")
    document = '\n'.join(document)
    return document


if __name__ == '__main__':
    query = 'sữa rửa mặt'
    products = query_assistant(query, top_k=8)

    print(products)