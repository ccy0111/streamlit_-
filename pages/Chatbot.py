
import streamlit as st

st.title("실습 6 - 국립부경대학교 도서관 챗봇")

if "openai_client" not in st.session_state:
    st.warning("API Key를 먼저 입력하세요.")
    st.stop()

client = st.session_state["openai_client"]

# 도서관 규정 (주요 조항 요약)
# 실습 제출 시 공식 규정 전문으로 교체 가능
LIBRARY_RULES = """
국립부경대학교 도서관 규정

제18조 (이용 자격)
교직원과 재학생, 도서관장의 허가를 받은 사람은
도서관의 자료와 시설을 이용할 수 있다.

제19조 (개관 시간)
도서관의 개관 시간은 도서관장이 별도로 정한다.

제20조 (휴관일)
- 자료실: 공휴일, 개교기념일
- 일반열람실: 설날, 추석
- 도서관장은 필요에 따라 휴관일을 조정할 수 있다.

제21조 (자료대출)
대출 자격이 있는 사람은 본인 신분증으로 대출할 수 있다.

제22조 (대출 책수 및 기간)
- 전임교원, 겸임교원, 명예교수, 강사:
  50책 이내, 90일
- 직원, 조교, 대학원생:
  20책 이내, 30일
- 학부생:
  10책 이내, 14일
- 전자책:
  5책 이내, 5일
- 세부 대출 규칙은 별도로 정할 수 있다.

제23조 (대출 제한 자료)
연속간행물, 참고자료, 학위논문, 귀중자료,
비도서자료 등은 원칙적으로 대출할 수 없다.
단, 도서관장이 예외를 허가할 수 있다.
"""

INSTRUCTIONS = f"""
너는 국립부경대학교 도서관 안내 챗봇이다.

아래 도서관 규정을 근거로 사용자 질문에 답변하라.

규정에 없는 내용은 추측하지 말고
'제공된 규정에서 확인할 수 없습니다.'라고 답변하라.

가능하면 관련 조항 번호를 함께 제시하라.

[도서관 규정]
{LIBRARY_RULES}
"""

# 대화 기록 초기화
if "chatbot_messages" not in st.session_state:
    st.session_state["chatbot_messages"] = []

# Clear 버튼
def clear_chatbot():
    st.session_state["chatbot_messages"] = []

st.button("Clear", on_click=clear_chatbot)

# 이전 대화 출력
for message in st.session_state["chatbot_messages"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 사용자 질문
prompt = st.chat_input("도서관에 대해 질문하세요.")

if prompt:
    st.session_state["chatbot_messages"].append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        stream = client.responses.create(
            model="gpt-6-luna",
            instructions=INSTRUCTIONS,
            input=st.session_state["chatbot_messages"],
            stream=True
        )

        answer = st.write_stream(stream)

    st.session_state["chatbot_messages"].append({
        "role": "assistant",
        "content": answer
    })
