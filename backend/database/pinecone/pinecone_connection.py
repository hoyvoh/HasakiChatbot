from pinecone import Pinecone, ServerlessSpec
import os
import sys
from .pc_utils import create_vector_emb, time_it_ms
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# from dotenv import load_dotenv
# load_dotenv()

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')

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
    
    @time_it_ms
    def query_index_name_to_id(self, query, indexname='hasaki-index-v3', namespace='product-pname-namespace', topk=3):
        index = self.pc.Index(indexname)
        embeddings = create_vector_emb(query)
        query_response = index.query(
            vector=embeddings,
            top_k=topk,            
            namespace=namespace,        
            include_values=True  
        )
        return query_response
    
    @time_it_ms
    def query_support_metadata(self, query):
        index = self.pc.Index('hasaki-index-v3')
        query_embedded = create_vector_emb(query)
        query_response = index.query(
            vector=query_embedded,
            top_k=2,
            namespace='support-namespace',
            include_values = True,
            include_metadata=True
        )
        metadata = []
        for match in query_response['matches']:
            metadata.append({'title': match['metadata']['title'], 'content': match['metadata']['content'], 'link': match['metadata']['link']})
        
        return metadata

if __name__ == '__main__':
    query = 'Sữa_rửa_mặt sáng_da mờ_sẹo'
  
    pc = PineConeDB()
    
    print(pc.query_index_name_to_id(query=query, topk=10))
 