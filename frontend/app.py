import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

st.set_page_config(page_title="Hasaki Chat", page_icon="frontend/images/hasaki_icon.png")


col1, spacer, col2 = st.columns([1, 1.5, 4]) 

with col1:
    st.image("frontend/images/hasaki_logo.png", width=200)

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
        ai_response = "Bla bla bla"
        st.markdown(ai_response)
    
    st.session_state.chat_history.append(AIMessage(ai_response))
