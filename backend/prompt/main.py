from awan_api import AwanAPI
from prompt_design import prompt

# Example data to populate the template:
customer_query = "Giá của các loại sản phẩm dưỡng trắng da như thế nào"
retrieved_info = "Brightening Serum - Price: $29.99, Promotion: 10% off for members, Stock: Available"

awan = AwanAPI()

# Generate the prompt
# final_prompt = prompt.format(retrieved_info=retrieved_info)

final_prompt = ''

chat_response = awan.get_response(final_prompt, customer_query)

print("Customer query: ", customer_query)
print("Response: ", chat_response.get('choices')[0]['message']['content'])