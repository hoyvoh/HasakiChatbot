import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv
load_dotenv()
import requests
import json
LOCALHOST = os.getenv('LOCALHOST')


def get_response(query):
    payload = {"query":query}
    headers = {'Content-Type': 'application/json', 'accept': 'application/json'}
    response = requests.post('http://127.0.0.1:8000/send-query/', json=payload, headers=headers)
    if response.status_code == 200:
        return response.json().get('answer')
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return response.text


st.set_page_config(page_title="Hasaki Chat", page_icon="./images/hasaki_icon.png")


col1, spacer, col2 = st.columns([1, 1.5, 4]) 

with col1:
    st.image("./images/hasaki_logo.png", width=200)

with col2:
    st.title("Chat Box")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# Conversation
for message in st.session_state.chat_history:
    if isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.markdown(message.content)
    
    elif isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.markdown(message.content)

# User input
user_query = st.chat_input("Your Message...")

if user_query is not None and user_query != "":
    st.session_state.chat_history.append(HumanMessage(user_query))

    with st.chat_message("Human"):
        st.markdown(user_query)
    
    with st.chat_message("AI"):
        ai_response = get_response(user_query)
        st.markdown(ai_response)
    
    st.session_state.chat_history.append(AIMessage(ai_response))
