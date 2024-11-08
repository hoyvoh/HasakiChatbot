import pandas as pd
from transformers import AutoTokenizer, AutoModel
from pinecone import Pinecone, ServerlessSpec
import os
import sys
import unicodedata
import regex as re
from pyvi import ViTokenizer
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

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
    cleaned_text = clean_text(text)
    inputs = tokenizer(cleaned_text, return_tensors="pt", truncation=True, max_length=128)
    outputs = model(**inputs)
    embedding = outputs.last_hidden_state.mean(dim=1).squeeze().tolist()  # Take mean of the last hidden state
    return embedding

stop_words = []
with open (os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')),'stopwords.txt'), 'r', encoding='utf8') as f:
    stop_words.extend(f.read().split('\n'))

# Text cleaning function
def clean_text(text):
    # Convert to lowercase
    text = text.lower() 
    
    # Normalize Unicode characters
    text = unicodedata.normalize('NFKC', text)
    
    # Remove characters and numbers
    text = re.sub(r'[^a-zA-ZÀ-ỹ ]+', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # tokenized_sentence = word_tokenize(text, format='text').split()  # List of words
    tokenized_sentence = ViTokenizer.tokenize(text)
   
    cleaned_sentence = ' '.join(word for word in tokenized_sentence.split() if word not in stop_words)
    text = ' '.join(word for word in text.split() if word not in stop_words)  # Remove stopwords
    return cleaned_sentence 

if __name__ == '__main__':
    query = 'Sữa_rửa_mặt sáng_da mờ_sẹo'
    index_name = 'product-pname-index'
    pc = PineConeDB(api_key=PINECONE_API_KEY)
    

    print(pc.query_index_name_to_id(indexname=index_name, query=query, topk=10))
 