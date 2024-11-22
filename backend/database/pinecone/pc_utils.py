import time
import pandas as pd
from transformers import AutoTokenizer, AutoModel
import os
import sys
import unicodedata
import regex as re
from sklearn.metrics import mean_absolute_error, root_mean_squared_error
from pyvi import ViTokenizer
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from dotenv import load_dotenv
from prompt import openai_api

load_dotenv()
from prompt import openai_api

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
TOKENIZER_MODEL= os.getenv('TOKENIZER_MODEL')

openai_client = openai_api.OpenAIClient()

tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_MODEL)
model = AutoModel.from_pretrained(TOKENIZER_MODEL)

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

def create_vector_emb(text):
    if text != '':
        cleaned_text = clean_text(text)
        # inputs = tokenizer(cleaned_text, return_tensors="pt", truncation=True, max_length=128)
        # outputs = model(**inputs)
        # embedding = outputs.last_hidden_state.mean(dim=1).squeeze().tolist()  # Take mean of the last hidden state
        embedding = openai_client.get_embeddings(cleaned_text)
        return embedding
    

# Define the decorator
def time_it_ms(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()  # Start timing
        result = func(*args, **kwargs)  # Execute the function
        end_time = time.time()  # End timing
        execution_time_ms = (end_time - start_time) * 1000  # Convert to milliseconds
        print(f"{func.__name__} executed in {execution_time_ms:.2f} ms")
        return result 
    return wrapper  

@time_it_ms
def get_pids_from_pc_response(query_response):
    pids = [int(match['id']) for match in query_response['matches']]
    return pids

@time_it_ms
def get_similar_metrics(query, query_response):
    embeddings = create_vector_emb(query)
    pid_score_pair = []
    for match in query_response['matches']:
        pid_score_pair.append({'pid': match['id'], 
                            'cosine': match['score'],
                            'MAE': round(mean_absolute_error(embeddings, match['values']), 3), 
                            'RMSE': round(root_mean_squared_error(embeddings, match['values']), 3)})
    
    return pid_score_pair    

if __name__ == '__main__':
    query = 'Sữa_rửa_mặt sáng_da mờ_sẹo'
    
    print(create_vector_emb(query))