from query_processor import generate_answer
from fastapi import FastAPI
from prompt import OpenAIClient
from pydantic import BaseModel
from database import MongoDB, PineConeDB
import os
from fastapi.middleware.cors import CORSMiddleware
from os import getenv
from dotenv import load_dotenv
from time import time
os.environ.clear()
load_dotenv()

MODEL_NAME = getenv('MODEL_NAME_LARGE')
USERNAME = getenv('USERNAME')
PASSWORD = getenv('PASSWORD')
CLUSTER_URL = getenv('CLUSTER_URL')
PINECONE_API_KEY = getenv('PINECONE_API_KEY')

class Query(BaseModel):
    query: str

openai = OpenAIClient()
pc = PineConeDB(api_key=PINECONE_API_KEY)
mongo = MongoDB(username=USERNAME, password=PASSWORD, cluster_url=CLUSTER_URL)
app = FastAPI()

origins = [
    "http://localhost:8501",
    "http://0.0.0.0:8501",
    "*",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post('/send-query/')
async def process_answer(query_request: Query):
    start = time()
    answer = generate_answer(query_request.query, openai, pc, mongo)
    end = time()
    print("Time used while query:", end-start, "s")

    return {'answer': answer}

