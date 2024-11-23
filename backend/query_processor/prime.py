import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv

load_dotenv()

from .minilm import get_decision
# from . import minilm
from prompt import PROMPT_TEMPLATE, AwanAPI, OpenAIClient
from database import PineConeDB, MongoDB, get_pids_from_pc_response, get_similar_metrics
from itertools import combinations
from pyvi import ViTokenizer
from .query_assistant import query_assistant

LARGE_MODEL = os.getenv('MODEL_NAME_LARGE')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')

awan = AwanAPI(model_name=LARGE_MODEL)
openai = OpenAIClient()
pc = PineConeDB()
mongo = MongoDB()

def extract_products_to_natural_language(data):
    if not isinstance(data, dict) or 'products' not in data or not isinstance(data['products'], list):
        return "No valid product structure found."
    products = data['products']
    natural_language_output = []
    for product in products:
        pname = product.get('pname', 'Unknown Product')
        price = product.get('price', 0)
        plink = product.get('plink', '')
        p_cmt_neg = product.get('cmt_summary_NEG','')
        p_cmt_pos = product.get('cmt_summary_POS','')
        p_cmt_neu = product.get('cmt_summary_NEU','')
        price_formatted = f"{price:,} VND"
        product_description = (
            f"Product Name: {pname}, "
            f"Price: {price_formatted}, "
            f"Link: {plink}, "
            f"Positive reviews: {p_cmt_pos}, "
            f"Negative reviews: {p_cmt_neg}, "
            f"Neutral reviews: {p_cmt_neu}."
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
        res = pc.query_index_name_to_id(query=product)
        pids = get_pids_from_pc_response(res)
        
        score = get_similar_metrics(product, res)
        print(score)
        # query ID in product collection => metadata
        metadata = mongo.query_relevant_products_within_budget(product_ids=pids, budget=0)

    elif signal == 2:
        '''product1 = ViTokenizer.tokenize(str(message['product_term_1']))
        product2 = ViTokenizer.tokenize(str(message['product_term_2']))

        res1 = pc.query_index_name_to_id(query=product1)
        pids = get_pids_from_pc_response(res1)
        
        res2 = pc.query_index_name_to_id(query=product2)
        pid2 = get_pids_from_pc_response(res2)
        
        for i in range(len(pid2)):
            pids.append(pid2[i])
        print(pids)
        metadata = mongo.query_pids(pids)'''
        docs = ""
        for key, value in message.items():
            if key.startswith('product_term_'):
                product = ViTokenizer.tokenize(str(value))
                response = pc.query_index_name_to_id(query=product)
                pids = get_pids_from_pc_response(response)
                metadata = mongo.query_pids(pids)

                docs += f"Thông tin về {value}:\n {"\n\nvà ".join(metadata)}"
        
        return docs


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
            res1 = pc.query_index_name_to_id(namespace=namespace, query=product_term, topk=5)
            pids = get_pids_from_pc_response(res1)
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
            res_by_pname = pc.query_index_name_to_id(query=tokenized_product, namespace='product-pname-namespace', topk=5)
            pid_list_by_pname = get_pids_from_pc_response(res_by_pname)
            
            
            res_by_desc = pc.query_index_name_to_id(query=tokenized_product, namespace='product-desc-namespace', topk=5)
            pid_list_by_desc = get_pids_from_pc_response(res_by_desc)
            print("top 10 pid: ", pid_list_by_pname + pid_list_by_desc)
            
            # query ID in product collection => metadata
            metadata = mongo.query_pids_with_filter(pid_list_by_pname + pid_list_by_desc, message, 'product_data')

    metadata = extract_products_to_natural_language(metadata)
    return metadata

def get_document(query, pc, mongo):
    decided_json = get_decision(query)
    print("decided json:", decided_json)
    signal = int(decided_json['signal'])
    message = decided_json
    document = switch(signal, message, pc, mongo)
    additional = query_assistant(query=query, top_k=3)
    document = additional+ '\n' +str(document)
    return document

def generate_answer(query, client, pc, mongo):
    document = get_document(query, pc, mongo)
    print("Doc: ", document)
    guide = PROMPT_TEMPLATE.format(document)

    chat_response = client.get_response(prompt = guide, user_message = query)
    return chat_response


if __name__ == '__main__':
    #print(generate_answer('Dầu gội đầu thảo dược Thái Dương nay có khuyến mãi gì không?', awan))
    # print(generate_answer('Son dưỡng 3CE khác gì son dưỡng vaseline', openai, pc, mongo))
    # print(generate_answer('với 500k, gợi ý tôi mua gì cho 20.11', openai, pc, mongo))
    print(generate_answer('Son Bóng Maybelline 15', openai, pc, mongo))
