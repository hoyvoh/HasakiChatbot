import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv

load_dotenv()

# from .minilm import get_decision
from . import minilm
from prompt import PROMPT_TEMPLATE, AwanAPI
from itertools import combinations
import regex as re
import string
from pyvi import ViTokenizer

LARGE_MODEL = os.getenv('MODEL_NAME_LARGE')
awan = AwanAPI(model_name=LARGE_MODEL)
print('using', LARGE_MODEL)

def extract_products_to_natural_language(data):
    if not isinstance(data, dict) or 'products' not in data or not isinstance(data['products'], list):
        return "No valid product structure found."
    products = data['products']
    natural_language_output = []
    for product in products:
        pname = product.get('pname', 'Unknown Product')
        price = product.get('price', 0)
        plink = product.get('plink', '')
        price_formatted = f"{price:,} VND"
        product_description = (
            f"Product Name: {pname}, "
            f"Price: {price_formatted}, "
            f"Link: {plink}"
        )
        natural_language_output.append(product_description)
    return "\n".join(natural_language_output)

def extract_support_to_natural_language(data):
    natural_language_output = []
    for info in data:
        support_des = (
            f"Information to find answer to help: {info['content']}, "
            f"Give user link the most suitable: {info['link']}, "
        )

        natural_language_output.append(support_des)
    return "\n".join(natural_language_output)

# Determine tolerable solution
def suggest_based_on_budget(data, tolerance=0.1, top_n=3):
    budget = data["budget"]
    products = data["products"]

    # Calculate budget range
    lower_bound = budget * (1 - tolerance)
    upper_bound = budget * (1 + tolerance)

    all_solutions = []
    for r in range(1, len(products) + 1):
        all_solutions.extend(combinations(products, r))
    legit_solutions = [
        combo for combo in all_solutions
        if lower_bound <= sum(product["price"] for product in combo) <= upper_bound
    ]
    ranked_solutions = sorted(
        legit_solutions,
        key=lambda plan: (
            abs(budget - sum(product["price"] for product in plan)),  
            -sum(product["price"] for product in plan),              
            -len(plan)                                             
        )
    )

    top_solutions = [
        {
            "products": plan, 
            "total_cost": sum(product["price"] for product in plan)
        }
        for plan in ranked_solutions[:top_n]
    ]
    
    return top_solutions


def switch(signal, message, pc, mongo):
    metadata = {}
    print('signal:', signal)
    if signal == 0:
        return ''
    elif signal == 1:
        product = str(message['product_term'])
        product = ViTokenizer.tokenize(product)

        # query embedding in Product Index (Title +  ID) => top 1 product id
        pids = pc.query_index_name_to_id(query=product)
        # query ID in product collection => metadata
        metadata = mongo.query_relevant_products_within_budget(product_ids=pids, budget=0)

    elif signal == 2:
        product1 = ViTokenizer.tokenize(str(message['product_term_1']))
        product2 = ViTokenizer.tokenize(str(message['product_term_2']))

        pids = pc.query_index_name_to_id(query=product1)
        pid2 = pc.query_index_name_to_id(query=product2)
        for i in range(len(pid2)):
            pids.append(pid2[i])
        print(pids)
        metadata = mongo.query_pids(pids)
        

    elif signal == 4:
        query = ViTokenizer.tokenize(str(message['query']))
        metadata = pc.query_support_metadata(query)
        
        return extract_support_to_natural_language(metadata)

    elif signal == 5:
        '''
        (5) Nếu người dùng cung cấp một số tiền và cần hỗ trợ mua hàng dựa trên số tiền hiện có, hãy trả lời với cú pháp: 
        {'signal':'5','budget':'<budget>','product_term':'<Danh sách các term về sản phẩm>'}; 
        chú ý, budget phải là một con số hoặc một string có thể chuyển thành int một cách trực tiếp.
        product term ở đây là một danh sách các sản phẩm gồm sản phẩm đầu là sản phẩm chính và các sản phẩm sau là 
        sản phẩm mà người dùng có thể cũng mua chung
        '''
        budget = int(message['budget'])
        product_terms = ViTokenizer.tokenize(message['product_term']).split(',')
        namespace = 'product-desc-namespace'
        product_ids = []

        for product_term in product_terms:
            pids = pc.query_index_name_to_id(namespace=namespace, query=product_term, topk=10)
            product_ids.extend(pids)
        
        product_ids = list(set(product_ids))
        metadata = mongo.query_relevant_products_within_budget(product_ids=product_ids, budget=budget)
        metadata["budget"] = budget
        solutions = suggest_based_on_budget(metadata, tolerance=0.2)
        document = []
        document.append("\nHãy gợi ý cho khách hàng các cách lựa chọn sau:\n")
        for idx, plan in enumerate(solutions, 1):
            document.append(f"Combo {idx}:\n")
            for product in plan["products"]:
                document.append(
                    f"  - Sản phẩm: {product['pname']}\n"
                    f"    link: {product['plink']}\n"
                    f"    Giá: {product['price']}\n"
                )
            document.append(f"Tổng tiền: {plan['total_cost']}\n")
            document.append("-" * 40 + "\n")
        # debugging
        document = '\n'.join(document)
        print(document)
        return document

    else: # signal == 3
        if "product_term" in message:
            product = str(message['product_term'])
            tokenized_product = ViTokenizer.tokenize(product)
            
            # query embedding in Product Index (Title +  ID) => top 1 product id
            pid_list_by_pname = pc.query_index_name_to_id(query=tokenized_product, namespace='product-pname-namespace', topk=5)
            
            pid_list_by_desc = pc.query_index_name_to_id(query=tokenized_product, namespace='product-desc-namespace', topk=5)
            print("top 10 pid: ", pid_list_by_pname + pid_list_by_desc)
            
            # query ID in product collection => metadata
            metadata = mongo.query_pids_with_filter(pid_list_by_pname + pid_list_by_desc, message, 'product_data')

    metadata = extract_products_to_natural_language(metadata)
    return metadata

def get_document(query, pc, mongo):
    decided_json = minilm.get_decision(query)
    signal = int(decided_json['signal'])
    message = decided_json
    document = switch(signal, message, pc, mongo)
    return document

def generate_answer(query, awan, pc, mongo):
    document = get_document(query, pc, mongo)
    print("doc: ", document)
    guide = PROMPT_TEMPLATE.format(document)

    
    chat_response = awan.get_response(guide,query)
    answer = chat_response.get('choices')[0]['message']['content']

    return answer

if __name__ == '__main__':
    #print(generate_answer('Dầu gội đầu thảo dược Thái Dương nay có khuyến mãi gì không?', awan))
    print(generate_answer('Hôm trước mua dầu gội bên Hasaki mà chất lượng kém quá, muốn trả hàng mà làm nọ làm kia. Làm sao để gửi báo cáo?', awan))
