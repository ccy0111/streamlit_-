import streamlit as st
import openai 
import base64

if "openai_client" not in st.session_state:
    st.stop()

st.header("lab03")
client = st.session_state["openai_client"]
prompt = st.text_input("프롬프트를 입력하세요 : ", key="text_prompt")

@st.cache_data
def gen_response(prompt):
     response = client.responses.create(
          model = "gpt-6-luna",
          input = prompt
     )
     return response.output_text

if st.button("전송", key="text_button") and prompt:
     st.write(gen_response(prompt))

import base64

image_prompt = st.text_input("이미지 프롬프트를 입력하세요 : ", key="img_prompt")


st.header("lab04")

if st.button("전송", key="img_button") and image_prompt:
     with st.spinner("이미지를 생성중..."):
          img = client.images.generate(
               model="gpt-image-2.6-flare",
               prompt=image_prompt,
          )
     image_bytes = base64.b64decode(img.data[0].b64_json)
     st.image(image_bytes)



