import time
from awan_llm_api import AwanLLMClient, Role
from awan_llm_api.completions import ChatCompletions
import sys
import os
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

AWANLLM_API_KEY = os.getenv('AWAN_API_KEY')
MODEL = os.getenv('MODEL_NAME_LARGE')

class AwanAPI:
    def __init__(self, api_key=AWANLLM_API_KEY, model_name=MODEL):
        self.api_token = api_key
        self.model_name = MODEL
        self.history = []
        self.last_request_time = None  # Initialize the last request time

        if self.api_token and self.model_name:
            self.client = AwanLLMClient(self.api_token)
            self.chat = ChatCompletions(self.model_name)

    def add_to_history(self, role, message):
        self.history.append({'role': role, 'message': message})

    def get_response(self, prompt, customer_query, mode="text"):
        self.add_to_history(Role.SYSTEM, prompt)  
        self.add_to_history(Role.USER, customer_query)

        # Check time elapsed since last request to stay under rate limit (20 requests/min)
        if self.last_request_time:
            time_since_last_request = time.time() - self.last_request_time
            min_interval_between_requests = 60 / 20  # 3 seconds for 20 req/min

            if time_since_last_request < min_interval_between_requests:
                time_to_wait = min_interval_between_requests - time_since_last_request
                print(f"Rate limit in effect. Waiting for {time_to_wait:.2f} seconds.")
                time.sleep(time_to_wait)

        # Process the request and store the time
        for entry in self.history:
            self.chat.add_message(entry['role'], entry['message'])

        response = self.client.chat_completion(self.chat)
        self.last_request_time = time.time()  # Update the last request time
        self.add_to_history(Role.ASSISTANT, response)

        if mode == "json":
            return {
                "response": response,
                "history": self.history
            }
        return response  # Default to returning text if no mode is specified
