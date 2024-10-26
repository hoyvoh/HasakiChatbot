from typing import Union
from query_processor import generate_answer
from fastapi import FastAPI
from prompt import AwanAPI
from os import getenv
from dotenv import load_dotenv
load_dotenv()

MODEL_NAME = getenv('MODEL_NAME_LARGE')

awan = AwanAPI(model_name=MODEL_NAME)
app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post('/send-query/')
async def process_answer(query):
    answer = generate_answer(query, awan)
    return {'answer':answer}