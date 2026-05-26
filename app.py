import streamlit as st
import random

st.set_page_config(page_title="연애 코칭 앱", page_icon="💖")

st.title("💖 AI 연애 코칭 앱")
st.write("현재 고민을 입력하면 간단한 연애 조언을 해드려요!")

# 고민 입력
question = st.text_input("연애 고민 입력하기")

# 조언 리스트
advice_list = [
    "상대방의 말을 끝까지 들어주는 것이 중요해요 😊",
    "너무 조급해하지 말고 자연스럽게 다가가보세요 🌸",
    "진심 어린 표현은 큰 힘이 돼요 💌",
    "연애에서도 자신을 먼저 아끼는 게 중요해요 💪",
    "가끔은 솔직한 대화가 관계를 더 깊게 만들어요 ☕",
]

# 버튼 클릭 시 결과 출력
if st.button("연애 코칭 받기"):
    if question == "":
        st.warning("고민을 입력해주세요!")
    else:
        st.success(random.choice(advice_list))
