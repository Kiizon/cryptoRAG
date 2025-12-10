import streamlit as st
from rag import ChatBot, Documents
import cohere

st.title("CryptoRAG ChatBot")
st.markdown("This is a chatbot that uses cohere's RAG model to answer questions about cryptography.")


with st.sidebar:
    st.title("CryptoRAG ChatBot")
    st.markdown("This is chatbot provides information about cryptography. It is powered by cohere's RAG model. This project is inspired by TMU's CPS 633 course.")
    api_key = st.text_input("Enter your Cohere API key", type="password")
    st.divider()
    st.markdown("Made by Kish Dizon")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

sources = [
    {
        "title": "Crypto101",
        "url": "https://www.crypto101.io/Crypto101.pdf"
    }
]

def is_valid_api_key(api_key):
    """
    Checks if the API key is valid.
    """
    if not api_key:
        st.info("Please enter your Cohere API key in the sidebar to continue.")
        return False
    try:
        co  = cohere.ClientV2(api_key)
        co.generate(prompt="Hello, I am Crypto. How can I help you today?")
        return True

    except Exception as e:
        st.warning("Invalid API key. Please enter a valid API key.")
        return False

if is_valid_api_key(api_key):
    client =  cohere.ClientV2(api_key)
    documents = Documents(sources, client)
    chatbot = ChatBot(documents, client)

    if prompt := st.chat_input("How can I help you today?"):
        with st.chat_message("user"):
            st.markdown(prompt)

        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            try: 
                response = chatbot.generate_response(prompt)
                text = st.write_stream(response)
            except Exception as e:
                text = f"Sorry, I am limited to only a few api calls a minute. Please try again later."
                st.error(e)
        st.session_state.messages.append({"role": "assistant", "content": text})

