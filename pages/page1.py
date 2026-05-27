import streamlit as st
import google.generativeai as genai

# 페이지 설정
st.set_page_config(
    page_title="연애상담 챗봇",
    page_icon="💖"
)

st.title("💖 연애상담 챗봇")
st.caption("Gemini 기반 고민 상담 챗봇")

# API 키 불러오기
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)

except Exception:
    st.error("❌ Secrets에 GOOGLE_API_KEY가 설정되지 않았습니다.")
    st.stop()

# 모델 설정
model = genai.GenerativeModel("gemini-2.5-flash-lite")

# 채팅 기록 저장
if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 채팅 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력
prompt = st.chat_input("연애 고민을 입력하세요...")

if prompt:
    # 사용자 메시지 저장
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    # 사용자 메시지 출력
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # 시스템 프롬프트
        system_prompt = """
        너는 따뜻하고 공감 능력이 뛰어난 연애상담 챗봇이다.
        사용자의 고민을 비난하지 말고 공감하며 조언해라.
        답변은 자연스럽고 친근한 한국어로 해라.
        """

        # 대화 기록 구성
        conversation = system_prompt + "\n\n"

        for msg in st.session_state.messages:
            role = "사용자" if msg["role"] == "user" else "챗봇"
            conversation += f"{role}: {msg['content']}\n"

        # Gemini 응답 생성
        response = model.generate_content(conversation)

        bot_reply = response.text

    except Exception as e:
        bot_reply = f"❌ 오류가 발생했습니다:\n\n{e}"

    # 챗봇 응답 저장
    st.session_state.messages.append({
        "role": "assistant",
        "content": bot_reply
    })

    # 챗봇 응답 출력
    with st.chat_message("assistant"):
        st.markdown(bot_reply)

# 사이드바
with st.sidebar:
    st.header("⚙️ 설정")

    if st.button("채팅 기록 삭제"):
        st.session_state.messages = []
        st.rerun()

    st.info(
        "주제만 바꾸면 다양한 챗봇으로 활용 가능!\n\n"
        "예: 진로상담, 공부코칭, 고민상담 등"
    )
