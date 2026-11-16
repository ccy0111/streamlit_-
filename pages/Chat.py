
import streamlit as st

st.title("lab05")

if "openai_client" not in st.session_state:
    st.stop()

client = st.session_state["openai_client"]

if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = []

def clear_chat():
    st.session_state["chat_messages"] = []

st.button("Clear", on_click=clear_chat)

for message in st.session_state["chat_messages"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])

prompt = st.chat_input("메시지를 입력하세요.")

if prompt:
    st.session_state["chat_messages"].append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):

        stream = client.responses.create(
            model="gpt-6-luna",
            input=st.session_state["chat_messages"],
            stream=True
        )

        response = st.write_stream(stream)

    st.session_state["chat_messages"].append({
        "role": "assistant",
        "content": response
    })
