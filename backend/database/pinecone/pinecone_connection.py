import pandas as pd
from transformers import AutoTokenizer, AutoModel
from pinecone import Pinecone, ServerlessSpec
import os
import re
import unicodedata
import pandas as pd
from pyvi import ViTokenizer
# Load stopwords from text file
stop_words = pd.read_csv('../../../data/vietnamese-stopwords-dash.txt', header=None)

TOKENIZER_MODEL = os.getenv('TOKENIZER_MODEL')
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
   
    cleaned_sentence = ' '.join(word for word in tokenized_sentence.split() if word not in stop_words[0].tolist())
    text = ' '.join(word for word in text.split() if word not in stop_words)  # Remove stopwords
    return cleaned_sentence 
        
    
    def query_index_name_to_id(self, indexname, query):
        index = self.pc.Index(indexname)
        embeddings = create_vector_emb(query)
        query_response = index.query(
            vector=embeddings,
            top_k=1,            
            namespace="",        
            include_values=True  
        )

        return query_response['matches'][0]['id']


def create_vector_emb(text):
    cleaned_text = clean_text(text)
    inputs = tokenizer(cleaned_text, return_tensors="pt", truncation=True, max_length=128)
    outputs = model(**inputs)
    embedding = outputs.last_hidden_state.mean(dim=1).squeeze().tolist()  # Take mean of the last hidden state
    return embedding


if __name__ == '__main__':
    query = 'Sữa_rửa_mặt sáng_da mờ_sẹo'
    index_name = 'product-pname-index'
    pc = PineConeDB(api_key=PINECONE_API_KEY)

    print(pc.query_index_name_to_id(indexname=index_name, query=query))
 