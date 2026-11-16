
import streamlit as st

st.title("실습 7 - ChatPDF")

if "openai_client" not in st.session_state:
    st.warning("API Key를 먼저 입력하세요.")
    st.stop()

client = st.session_state["openai_client"]

# 대화 기록 초기화
if "chatpdf_messages" not in st.session_state:
    st.session_state["chatpdf_messages"] = []


# ---------------------------
# PDF 업로드 및 Vector Store 생성
# ---------------------------
if "chatpdf_vector_store_id" not in st.session_state:

    uploaded_pdf = st.file_uploader(
        "PDF 파일을 업로드하세요.",
        type=["pdf"],
        accept_multiple_files=False
    )

    if uploaded_pdf and st.button("PDF 등록"):
        vector_store_id = None
        file_id = None

        try:
            with st.spinner("PDF를 처리하고 있습니다..."):

                # OpenAI에 PDF 업로드
                uploaded_file = client.files.create(
                    file=(
                        uploaded_pdf.name,
                        uploaded_pdf.getvalue(),
                        "application/pdf"
                    ),
                    purpose="assistants"
                )
                file_id = uploaded_file.id

                # Vector Store 생성
                vector_store = client.vector_stores.create(
                    name="ChatPDF",
                    expires_after={
                        "anchor": "last_active_at",
                        "days": 1
                    }
                )
                vector_store_id = vector_store.id

                # PDF 연결 및 인덱싱 완료 대기
                result = client.vector_stores.files.create_and_poll(
                    vector_store_id=vector_store_id,
                    file_id=file_id
                )

                if result.status != "completed":
                    raise RuntimeError(
                        f"인덱싱 실패: {result.status}"
                    )

            # 세션에 한 번만 저장
            st.session_state["chatpdf_vector_store_id"] = vector_store_id
            st.session_state["chatpdf_file_id"] = file_id
            st.session_state["chatpdf_file_name"] = uploaded_pdf.name
            st.session_state["chatpdf_messages"] = []

            st.rerun()

        except Exception as e:
            # 실패 시 생성한 리소스 정리
            if vector_store_id:
                try:
                    client.vector_stores.delete(vector_store_id)
                except Exception:
                    pass

            if file_id:
                try:
                    client.files.delete(file_id)
                except Exception:
                    pass

            st.error(f"PDF 처리 중 오류: {e}")

    st.stop()


# ---------------------------
# PDF 챗봇
# ---------------------------
st.success(
    f"등록된 PDF: {st.session_state['chatpdf_file_name']}"
)

# Clear: 대화 기록만 삭제
def clear_chatpdf():
    st.session_state["chatpdf_messages"] = []

col1, col2 = st.columns(2)

with col1:
    st.button("Clear", on_click=clear_chatpdf)

with col2:
    # Leave: Vector Store와 업로드 파일 삭제
    if st.button("Leave"):
        try:
            with st.spinner("파일을 정리하고 있습니다..."):
                client.vector_stores.delete(
                    st.session_state["chatpdf_vector_store_id"]
                )
                client.files.delete(
                    st.session_state["chatpdf_file_id"]
                )

            for key in [
                "chatpdf_vector_store_id",
                "chatpdf_file_id",
                "chatpdf_file_name",
                "chatpdf_messages"
            ]:
                st.session_state.pop(key, None)

            st.rerun()

        except Exception as e:
            st.error(f"리소스 삭제 중 오류: {e}")
            st.stop()


# 이전 대화 출력
for message in st.session_state["chatpdf_messages"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])


# 사용자 입력
prompt = st.chat_input("PDF에 대해 질문하세요.")

if prompt:
    st.session_state["chatpdf_messages"].append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        try:
            stream = client.responses.create(
                model="gpt-6-luna",
                instructions=(
                    "업로드된 PDF의 내용을 바탕으로 답변하세요. "
                    "문서에서 확인할 수 없는 내용은 "
                    "추측하지 말고 확인할 수 없다고 답하세요."
                ),
                input=st.session_state["chatpdf_messages"],
                tools=[
                    {
                        "type": "file_search",
                        "vector_store_ids": [
                            st.session_state[
                                "chatpdf_vector_store_id"
                            ]
                        ]
                    }
                ],
                stream=True
            )

            answer = st.write_stream(stream)

        except Exception as e:
            st.error(f"응답 생성 중 오류: {e}")
            st.stop()

    st.session_state["chatpdf_messages"].append({
        "role": "assistant",
        "content": answer
    })
