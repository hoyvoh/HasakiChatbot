from awan_llm_api import AwanLLMClient, Role
from awan_llm_api.completions import ChatCompletions
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv
load_dotenv()

AWANLLM_API_KEY = os.getenv('AWAN_API_KEY')
MODEL = os.getenv('MODEL_NAME_LARGE')

class AwanAPI():
    def __init__(self, api_key=AWANLLM_API_KEY, model_name=MODEL):
        self.api_token = api_key
        self.model_name = MODEL
        self.history = []
       
        if self.api_token and self.model_name:
            self.client = AwanLLMClient(self.api_token)
            self.chat = ChatCompletions(self.model_name)

    def add_to_history(self, role, message):
        self.history.append({'role': role, 'message': message})

    def get_response(self, prompt, customer_query, mode="text"):
        self.add_to_history(Role.SYSTEM, prompt)  
        self.add_to_history(Role.USER, customer_query)

        for entry in self.history:
            self.chat.add_message(entry['role'], entry['message'])

        response = self.client.chat_completion(self.chat)
        self.add_to_history(Role.ASSISTANT, response)

        if mode == "json":
            return {
                "response": response,
                "history": self.history
            }
        return response  # Default to returning text if no mode is specified