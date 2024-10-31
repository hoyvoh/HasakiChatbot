from typing import Union
from query_processor import generate_answer
from fastapi import FastAPI
from prompt import AwanAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from os import getenv
from dotenv import load_dotenv
load_dotenv()

MODEL_NAME = getenv('MODEL_NAME_LARGE')

origins = [
    "http://localhost:8501",
]

class Query(BaseModel):
    query: str

awan = AwanAPI(model_name=MODEL_NAME)
app = FastAPI()

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
    answer = generate_answer(query_request.query, awan)
    return {'answer': answer}

#@app.get('/get-mongo/')

