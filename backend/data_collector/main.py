import requests
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm
import regex as re
from json.decoder import JSONDecodeError
from dotenv import load_dotenv
load_dotenv()
import os

def get_categories():
    url = 'https://hasaki.vn/'
    
    response = requests.get(url)
    bs = BeautifulSoup(response.text)
    
    categories_list = BeautifulSoup(str(bs.find_all('div', {"id": "box_danhmuc"}))).find_all('li')
    
    categories = []
    for cat in tqdm.tqdm(list(categories_list)):
        bs = BeautifulSoup(str(cat))
        link = bs.find('a', href=True)['href']
        img = bs.find('img')['data-src']
        cat = bs.find('a', {'class':'text_dmuc'}).get_text()
        cate = {
            'link':link,
            'img':img,
            'cat':cat
        }
        categories.append(cate)

    pd.DataFrame(categories).to_csv('categories.csv', encoding='utf8', index=False)
    return categories

def get_product_pages(categories):
    product_pages = []
    for url in tqdm.tqdm(pd.DataFrame(categories)['link'].tolist()):
        page = {
            'p':1
        }
        for p in range(5):
            page['p']=1+p
            response = requests.get(url, params=page)
            product_pages.append(response.text) 
    
    product_links = []

    for page in tqdm.tqdm(product_pages):
        bs = BeautifulSoup(page)
        if not page:
            continue
        try:
            product_frame = bs.find_all('div', {'class':'item_sp_hasaki width_common relative'})        
            for frame in tqdm.tqdm(product_frame):
                fbs = BeautifulSoup(str(frame))
                plink = fbs.find('a', {'class':'block_info_item_sp width_common card-body'}, href=True)['href']
                pname = fbs.find('a', {'class':'block_info_item_sp width_common card-body'}, href=True)['data-name']
                pid = fbs.find('a', {'class':'block_info_item_sp width_common card-body'}, href=True)['data-id']
                element = fbs.find('a', {'class': 'block_info_item_sp width_common card-body'}, href=True)
                
                pcat = element.get('data-category-name', pname) 

                product = {
                    'pid':pid,
                    'pname':pname,
                    'plink':plink,
                    'pcat':pcat
                }
                product_links.append(product)
            #print(pd.DataFrame(product_links))

        except TypeError as e:
            print(e)
        except KeyError as e:
            print(e)

    pd.DataFrame(product_links).to_csv('product_links.csv') 
    for plink in tqdm.tqdm(product_links):
        url = plink['plink']
        response = requests.get(url)
        if not response.text:
            print('empty result for', plink)
            continue

        plink['page'] = response.text
    pd.DataFrame(product_links).to_csv('product_pages.csv', encoding='utf8')  
    return pd.DataFrame(product_links)

def get_comments (product_links):
    comments = []
    for _, product in tqdm(product_links.iterrows()):
        url = product['plink']
        pid = product['pid']
        pname = product['pname']
        
        for os in range(0, 5): 
            params = {
                'api': 'product.getRatingMore',
                'id': url.split('-')[-1].split('.')[0],
                'offset': os,
                'sort': 'buy'
            }
            
            response = requests.get(url='https://hasaki.vn/ajax', params=params)
            response.encoding = 'utf-8'
            try:
                if response.status_code == 200 and 'data' in response.json():
                    html_content = response.json()['data']['html']
                    bs = BeautifulSoup(html_content, 'html.parser')
        
                    # Find all comment items
                    comment_items = bs.find_all('div', class_='item_comment')
                    for item in comment_items:
                        name = item.find('strong', class_='txt_color_1').get_text(strip=True)
                        time = item.find('div', class_='timer_comment').get_text(strip=True)
                        description = item.find('div', class_='txt_999').get_text(strip=True)
                        comment = item.find('div', class_='content_comment').get_text(strip=True)
        
                        image_tags = item.find_all('img')
                        image_links = [img['src'] for img in image_tags] if image_tags else []
        
                        # Append the collected data
                        comments.append({
                            'Name': name,
                            'Time': time,
                            'Description': description,
                            'Comment': comment,
                            'Images': image_links
                        })
            except JSONDecodeError as e:
                print(e)

    comments_df = pd.DataFrame(comments)
    comments_df.to_csv('comments.csv', encoding='utf8')

def get_product_data(product_links):
    product_data = []
    brand_data = []

    for _, product in tqdm.tqdm(product_links.iterrows()):
        bs = BeautifulSoup(str(product['page']), 'html.parser')
        price_tag = bs.find('span', {'class': 'txt_price', 'id': 'product-final_price'})
        price = price_tag.get_text(strip=True) if price_tag else 'N/A'
        price_ext_tag = bs.find('div', {'class': 'hasaki-price-info'})
        price_extended = ' '.join(price_ext_tag.stripped_strings) if price_ext_tag else 'N/A'
        combo_tag = bs.find('div', {'class': 'product-add-form'})
        combo = '\n'.join([el for el in combo_tag.stripped_strings]) if combo_tag else 'N/A'
        delivery_tag = bs.find('div', {'id': 'box_giaohang', 'class': 'width_common product_right_box'})
        delivery = '\n'.join([el for el in delivery_tag.stripped_strings if el.lower() != 'xem thêm']) if delivery_tag else 'N/A'

        meta_tag = bs.find('table', {'class': 'tb_info_sanpham'})
        if meta_tag:
            lines = re.sub(r'\n{2,}', '\n', meta_tag.get_text(strip=True)).split('\n')
            metas = '\n'.join([f"{lines[i]}: {lines[i + 1]}" if i + 1 < len(lines) else lines[i] for i in range(0, len(lines), 2)])
        else:
            metas = 'N/A'

        ingredients_tag = bs.find('div', {'id': 'box_thanhphanchinh'})
        ingredients = ingredients_tag.get_text(strip=True) if ingredients_tag else 'N/A'

        usage_tag = bs.find('div', {'id': 'box_huongdansudung'})
        usage = usage_tag.get_text(strip=True) if usage_tag else 'N/A'

        brand_tag = bs.find('a', {'class': 'title-brand txt_color_1'})
        brand = brand_tag.get_text(strip=True) if brand_tag else 'N/A'

        brand_link_tag = bs.find('a', {'class': 'title-brand txt_color_1'}, href=True)
        brand_link = brand_link_tag['href'] if brand_link_tag else 'N/A'

        about_tag = bs.find('div', {'class': 'product-brand'})
        about = re.sub(r'\s+', ' ', about_tag.get_text(strip=True)) if about_tag else 'N/A'

        img_div_tag = bs.find('div', {'id': 'box_thongtinsanpham'})
        img = [item['src'] for item in img_div_tag.find_all('img')] if img_div_tag else []

        desc_div_tag = img_div_tag 
        desc = re.sub(r'\s+', ' ', desc_div_tag.get_text(strip=True)) if desc_div_tag else 'N/A'

        line = {
            'pid': product['pid'],
            'plink': product['plink'],
            'pname': product['pname'],
            'pcat': product['pcat'],
            'price': price,
            'price_extended': price_extended,
            'combo': combo,
            'delivery': delivery,
            'meta': metas,
            'ingredients': ingredients,
            'usage': usage,
            'img': img,
            'desc': desc,
            'about': about
        }


        bline = {
            'brand': brand,
            'brand_link': brand_link
        }

        product_data.append(line)
        brand_data.append(bline)

    pd.DataFrame(product_data).to_csv('product_data.csv', encoding='utf8')
    pd.DataFrame(brand_data).to_csv('brand_data.csv', encoding='utf8')

def get_campaign():
    url = 'https://hasaki.vn/campaign/wow'
    response = requests.get(url)

    campaigns = []

    if response.text:
        bs = BeautifulSoup(response.text)
        frames = bs.find_all('div', {'class': 'list_khuyenmai width_common'})
        fbs = BeautifulSoup(str(frames))
        imgs = fbs.find_all('img', src=True)
        links = fbs.find_all('a', href=True)
        labels = fbs.find_all('strong', {'class':'txt_color_2'})
        for img, link, lab in zip(imgs, links, labels):
            print(re.sub(r'[\n]', '', str(lab.contents[0])).strip())
            campaigns.append({
                'label':re.sub(r'[\n]', '', str(lab.contents[0])).strip(),
                'link': link['href'],
                'img': img['data-src']
            })
    pd.DataFrame(campaigns).to_csv('campaigns.csv', encoding='utf8')

def get_supports():
    url = 'https://hotro.hasaki.vn'
    response = requests.get(url)
    supports = []

    if response.text:
        bs = BeautifulSoup(response.text)
        sloganlogo = bs.find_all('div', {'class':'item_slogan_logo'})
        itemch = bs.find_all('div', {'class':'item_cau_hoi'})
        itemmenu = bs.find_all('div', {'class':'item_main_menu'})
        
        for frame in tqdm.tqdm(sloganlogo):
            fbs = BeautifulSoup(str(frame))
            lab = fbs.find('div', {'class':'text_logo'})
            link = fbs.find('a', href=True)['href']
            query = f'{url}{link}'
            if 'https' in link.split(':'):
                query = link
            content = requests.get(query)
            content = re.sub(r'\s+', ' ', str(BeautifulSoup(content.text, 'html.parser').get_text())).strip()
            supports.append({
                'title':lab,
                'link': query,
                'content':content
            })
        for frame in tqdm.tqdm(itemch):
            fbs = BeautifulSoup(str(frame))
            lab = fbs.find('a').get_text()
            link = fbs.find('a', href=True)['href']
            query = f'{url}{link}'
            if 'https' in link.split(':'):
                query = link
            content = requests.get(query)
            content = re.sub(r'\s+', ' ', str(BeautifulSoup(content.text, 'html.parser').get_text())).strip()
            supports.append({
                'title':lab,
                'link': query,
                'content':content
            })
        for frame in tqdm.tqdm(itemmenu):
            fbs = BeautifulSoup(str(frame))
            lab = fbs.find('a').get_text()
            link = fbs.find('a', href=True)['href']
            query = f'{url}{link}'
            if 'https' in link.split(':'):
                query = link
            content = requests.get(query)
            content = re.sub(r'\s+', ' ', str(BeautifulSoup(content.text, 'html.parser').get_text())).strip()
            supports.append({
                'title':lab,
                'link': query,
                'content':content
            })

    pd.DataFrame(supports).to_csv('supports.csv', encoding='utf8')

def update_dataset():
    categories = get_categories()
    product_links = get_product_pages(categories)
    get_campaign()
    get_supports()
    get_product_data(product_links)
    get_comments(product_links)
    print('Update Completed')    

if __name__ == '__main__':
    update_dataset()
