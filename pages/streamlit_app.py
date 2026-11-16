import streamlit as st
import openai


st.title("Streamlit 실습")
with st.sidebar:
     OPEN_API_KEY = st.text_input("OpenAI API Key")
if OPEN_API_KEY:
     st.session_state["openai_client"] = openai.OpenAI(api_key=OPEN_API_KEY)
pg = st.navigation([
     st.Page("./Home.py", title="Home", icon=":material/home:"),
     st.Page("./Chat.py", title="Chat", icon=":material/chat:"),
     st.Page("./Chatbot.py", title="Chat", icon=":material/chat:"),
     st.Page("./ChatPDF.py", title="Chat", icon=":material/chat:"),


])
pg.run()