import pandas as pd
from transformers import AutoTokenizer, AutoModel
import torch
from pinecone import Pinecone, ServerlessSpec
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv

load_dotenv()

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
TOKENIZER_MODEL= os.getenv('TOKENIZER_MODEL')
tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_MODEL)
model = AutoModel.from_pretrained(TOKENIZER_MODEL)

class PineConeDB():
    def __init__(self, api_key=PINECONE_API_KEY):
        self.pc = Pinecone(api_key=api_key)
   
    def create_index(self, index_name, dimension):
        if index_name not in self.pc.list_indexes():
            self.pc.create_index(
                name=index_name,
                dimension=dimension,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                ),
                deletion_protection="disabled"
                )
        return self.pc.Index(index_name)
    
    def query_index_name_to_id(self, query,indexname='hasaki-index', namespace='product-pname-namespace', topk=3):
        index = self.pc.Index(indexname)
        embeddings = create_vector_emb(query)
        query_response = index.query(
            vector=embeddings,
            top_k=topk,            
            namespace=namespace,        
            include_values=True  
        )
        product_ids = [match['id'] for match in query_response['matches']]
        print("Retrieved product IDs:", product_ids)
        return product_ids

def create_vector_emb(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
    outputs = model(**inputs)
    embedding = outputs.last_hidden_state.mean(dim=1).squeeze().tolist()  # Take mean of the last hidden state
    return embedding


if __name__ == '__main__':
    query = 'Sữa_rửa_mặt sáng_da mờ_sẹo'
    index_name = 'product-pname-index'
    pc = PineConeDB(api_key=PINECONE_API_KEY)

    print(pc.query_index_name_to_id(indexname=index_name, query=query, topk=10))
 