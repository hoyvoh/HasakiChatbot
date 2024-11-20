from openai import OpenAI 
import os
import json
import time
from dotenv import load_dotenv
# import prompt_design
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL")
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING")

class OpenAIClient:
    def __init__(self, api_key=API_KEY, model_name=MODEL, embedding_model=EMBEDDING_MODEL):
        self.api_key = api_key
        self.model_name = model_name
        self.embedding_model= embedding_model
        self.history = []
        self.last_request_time = None
        if self.api_key and self.model_name:
            self.client = OpenAI(api_key=API_KEY)

    def get_embeddings(self, input, mode='float'):  # mode: float | base64
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=input,
                encoding_format=mode
            )
            embeddings = response["data"][0]["embedding"]
            return embeddings
        except Exception as e:
            print(f"Error fetching embeddings: {e}")
            return None


    def add_to_history(self, role, content):
        self.history.append({"role": role, "content": content})

    def get_response(self, user_message, prompt, optimize_history=True):
        if not any(msg["role"] == "system" for msg in self.history):
            self.add_to_history("system", prompt)

        self.add_to_history("user", user_message)
        if optimize_history and len(self.history) > 100:  
            self.trim_history(max_messages=10)

        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=self.history
            )
            assistant_response = completion.choices[0].message.content

            self.add_to_history("assistant", assistant_response)

            return assistant_response

        except Exception as e:
            return f"An error occurred: {e}"
    
    def get_json_from_prompt(self, user_message, prompt, optimize_history=True):
        if not any(msg["role"] == "system" for msg in self.history):
            self.add_to_history("system", prompt)
        self.add_to_history("user", user_message)

        if optimize_history and len(self.history) > 15:
            self.trim_history(max_messages=10)

        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=self.history,
                response_format={"type": "json_object"}
            )
            assistant_response = completion.choices[0].message.content
            try:
                response_json = json.loads(assistant_response)
                return response_json
            except json.JSONDecodeError:
                return {
                    "error": "Failed to parse response as JSON",
                    "response": assistant_response,
                }

        except Exception as e:
            return {"error": str(e)}



# if __name__=='__main__':
#     client = OpenAIClient()
#     system_prompt = prompt_design.PROMPT_TEMPLATE

#     user_messages = [
#         'Giới thiệu cho tôi các sản phẩm bán chạy nhất.',
#         'Ở đây có bán gì rẻ rẻ không?',
#         'Cây son mắc nhất trên hasaki là cây nào?'
#     ]
    
#     for message in user_messages:
#         response = client.get_response(user_message=message, prompt=system_prompt)
#         print(f"User: {message}\nAssistant: {response}")
    
#     # Test history optimization
#     print("\n=== Testing Optimized History ===")
#     print("Current History:")
#     for entry in client.history:
#         print(entry)

    
#     print("\nOptimized History:")
#     for entry in client.history:
#         print(entry)

#     # Test `get_json_from_prompt`
#     print("\n=== Testing `get_json_from_prompt` ===")
#     json_prompt = (
#         "You are an API assistant. Respond to the user's message in JSON format with the following keys: "
#         "'summary', 'details'."
#     )
#     json_response = client.get_json_from_prompt(user_message="Summarize Python functions.", prompt=json_prompt)
#     print("JSON Response:", json_response)
    
