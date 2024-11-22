
import os
from pymongo import MongoClient, UpdateOne
import pandas as pd
from tqdm import tqdm
from itertools import combinations

USER = os.getenv('USERNAME')
PASS = os.getenv('PASSWORD')
URL = os.getenv('CLUSTER_URL')

class MongoDB():
    def __init__(self, username=USER, password=PASS, cluster_url=URL):
        
        self.username = username
        self.connection_str = f"mongodb+srv://{username}:{password}@{cluster_url}/test?retryWrites=true&w=majority".format(username, password, cluster_url)
        self.dbname='hasaki_data_v2'
        self.client = MongoClient(self.connection_str)
       
    
    def collection(self, collection_name):
        self.db = self.client[self.dbname]
        return self.db[collection_name]
    
    def upsert_data(self, data_df, collection, unique_field, upsert_fields=None, mode="row"):
        """
        Generic function to upsert data into a MongoDB collection.
        
        Args:
            data_df (DataFrame): The DataFrame containing data to be upserted.
            collection: The MongoDB collection object.
            unique_field (str): The unique field to identify documents.
            upsert_fields (list or str): Specific fields to upsert (optional). 
                                        If None, upserts the entire row as a dictionary.
            mode (str): "field" to upsert specific fields, "row" to upsert entire rows (default).
        """
        operations = []

        for _, row in data_df.iterrows():
            # Build the filter query
            filter_query = {unique_field: row[unique_field] if isinstance(row[unique_field], int) else int(row[unique_field])}

            # Build the update operation
            if mode == "field" and upsert_fields:
                # Upsert specific fields
                update_query = {"$set": {field: row[field] for field in upsert_fields}}
            else:
                # Upsert the entire row as a dictionary
                update_query = {"$set": row.to_dict()}

            # Add the operation to the list
            operations.append(UpdateOne(filter_query, update_query, upsert=True))

        # Perform the bulk write
        if operations:
            result = collection.bulk_write(operations)
            print(f"Upserted {result.upserted_count} documents.")
            print(f"Matched {result.matched_count} documents.")

    def query_pid(self, pid, collection_name='product_data'):
        col = self.collection(collection_name=collection_name)
        
        try:
            # Query the document using the pid
            product_ids = list(map(int, product_ids))
            result = col.find_one({"pid": int(pid)})

            if result is not None:
                # print("Document found:", result)
                return result  # Return the found document
            else:
                print("No document found with the given PID.")
                return None  # Return None if no document was found
        except Exception as e:
            print(f"Error querying PID: {e}")
            return None
        
    def query_pids(self, product_ids):
        col = self.collection(collection_name='product_data')
        
        try:
            product_ids = list(map(int, product_ids))
            fields_to_return = {'pname':1, 'price':1, 'plink':1, 'desc':1, 'ingredients':1, 'rating':1, 'count_NEG':1,'count_NEU':1, 'count_POS':1}
            
            results = col.find({"pid": {"$in": product_ids}}, fields_to_return)
            products = list(results)

            if not products:
                print("No relevant products found for given IDs.")
                return {"products": []}
            else:
                metadata = []
                for product_in4 in products:
                    
                    if product_in4['count_POS'] > max(product_in4['count_NEG'], product_in4['count_NEU']):
                        feedback = "Tốt"
                    elif product_in4['count_NEG'] > max(product_in4['count_POS'], product_in4['count_NEU']):
                        feedback = "xấu"
                    elif product_in4['count_NEU'] > max(product_in4['count_POS'], product_in4['count_NEG']):
                        feedback = "bình thường"
                    else:
                        feedback = "không rõ"

                    doc = f"""
                    Tên sản phẩm: {product_in4['pname']}
                    Giá: {product_in4['price']}
                    Link: {product_in4['plink']}
                    Mô tả: {product_in4['desc']}
                    Thành phần: {product_in4['ingredients']}
                    Điểm rating: {product_in4['rating']}
                    Đánh giá của khách hàng phần lớn là: {feedback}"""
                    
                    metadata.append(doc)
                return metadata
            

        except Exception as e:
            print(f"Error querying products: {e}")
            return {"products": []}
    
    def query_relevant_products_within_budget(self, product_ids, budget, collection_name='product_data'):
        col = self.collection(collection_name=collection_name)
        
        try:
            # Convert product_ids to integers to match the MongoDB `pid` field
            product_ids = list(map(int, product_ids))
            fields_to_return = {'pname':1, 'plink':1, 'price':1,'desc':1, 'rating':1, 'cmt_summary_NEG': 1, 'cmt_summary_NEU': 1, 'cmt_summary_POS':1}
            
            # Step 1: Fetch relevant products by product_ids
            results = col.find({"pid": {"$in": product_ids}}, fields_to_return)
            products = list(results)

            if not products:
                print("No relevant products found for given IDs.")
                return {"products": [], "combos": []}
            result = {
                "products": products
            }
            return result

        except Exception as e:
            print(f"Error querying products within budget: {e}")
            return {"products": []}

    def query_pids_with_filter(self, pid_list, message, collection_name='product_data'):
        col = self.collection(collection_name=collection_name)
        fields_to_return = {'pname':1, 'plink':1, 'price':1, 'rating':1, 'cmt_summary_NEG': 1, 'cmt_summary_NEU': 1, 'cmt_summary_POS':1}
        result = []
        try:
            pid_list = list(map(int, pid_list))
            if 'operator_price' in message and 'price' in message:
                
                # Query the document using the pid
                results = col.find(
                                { 
                                    'pid': { '$in': pid_list },
                                    'price': { message['operator_price']: int(message['price'])}  
                                },
                                fields_to_return)
            else: 
                # Query the document using the pid
                results = col.find(
                                { 
                                    'pid': { '$in': pid_list }},
                                fields_to_return)
            products = list(results)
            
            if not products:
                print("No relevant products found for given IDs.")
                return {"products": []}
            
            result = {
                "products": products
            }
            return result
        except Exception as e:
            print(f"Error querying PID: {e}")
            return {"products": []}