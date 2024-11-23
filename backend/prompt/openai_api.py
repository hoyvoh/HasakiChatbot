from openai import OpenAI 
import os
import json
from dotenv import load_dotenv
# import prompt_design
import json
import logging
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL")
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING")



logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class OpenAIClient:
    def __init__(self, api_key=API_KEY, model_name=MODEL, embedding_model=EMBEDDING_MODEL):
        self.api_key = api_key
        self.model_name = model_name
        self.embedding_model = embedding_model
        self.history = []
        self.last_request_time = None
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def get_embeddings(self, input, mode='float'):  # mode: float | base64
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=input,
                encoding_format=mode
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error fetching embeddings: {e}")
            return None

    def add_to_history(self, role, content):
        self.history.append({"role": role, "content": content})

    def trim_history(self, max_messages=15):
        if len(self.history) > max_messages:
            system_message = [msg for msg in self.history if msg["role"] == "system"]
            trimmed_history = self.history[-max_messages:]
            self.history = system_message + [msg for msg in trimmed_history if msg["role"] != "system"]

    def ensure_system_message(self, prompt):
        """
        Ensures that the system message exists in the conversation history.
        """
        if not any(msg["role"] == "system" for msg in self.history):
            self.add_to_history("system", prompt)

    def get_response(self, user_message, prompt, optimize_history=True):
        self.ensure_system_message(prompt)
        self.add_to_history("user", user_message)

        if optimize_history:
            self.trim_history(max_messages=15)

        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=self.history
            )
            assistant_response = completion.choices[0].message.content
            self.add_to_history("assistant", assistant_response)
            return assistant_response
        except IndexError:
            logger.error("The API response was empty or invalid.")
            return "The API response was empty or invalid."
        except Exception as e:
            logger.error(f"Error in get_response: {e}")
            return f"An error occurred: {e}"

    def get_json_from_prompt(self, user_message, prompt, optimize_history=True):
        self.ensure_system_message(prompt)
        self.add_to_history("user", user_message)

        if optimize_history:
            self.trim_history(max_messages=15)

        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=self.history,
                response_format={"type": "json_object"}
            )
            assistant_response = completion.choices[0].message.content

            try:
                return json.loads(assistant_response)
            except json.JSONDecodeError:
                logger.error("Failed to parse response as JSON")
                return {"error": "Failed to parse response as JSON", "response": assistant_response}
        except IndexError:
            logger.error("The API response was empty or invalid.")
            return {"error": "The API response was empty or invalid."}
        except Exception as e:
            logger.error(f"Error in get_json_from_prompt: {e}")
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
    
