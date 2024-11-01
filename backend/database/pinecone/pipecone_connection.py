import pandas as pd
from transformers import AutoTokenizer, AutoModel
import torch
from pinecone import Pinecone, ServerlessSpec
import os
TOKENIZER_MODEL = os.getenv('TOKENIZER_MODEL')
tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_MODEL)
model = AutoModel.from_pretrained(TOKENIZER_MODEL)

class PineConeDB():
    def __init__(self, api_key):
        
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

        
def create_vector_emb(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
    outputs = model(**inputs)
    embedding = outputs.last_hidden_state.mean(dim=1).squeeze().tolist()  # Take mean of the last hidden state
    return embedding
 