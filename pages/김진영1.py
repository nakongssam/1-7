import streamlit as st
import random

st.set_page_config(page_title="음식 추천 앱", page_icon="🍔")

st.title("🍽️ 오늘 뭐 먹지?")
st.write("버튼을 누르면 음식을 추천해드려요!")

foods = [
    "🍕 피자",
    "🍜 라면",
    "🍗 치킨",
    "🍣 초밥",
    "🍔 햄버거",
    "🥘 김치찌개",
    "🍝 파스타",
    "🥩 삼겹살",
    "🌮 타코",
    "🥟 만두"
]

if st.button("음식 추천 받기"):
    st.success(f"오늘의 추천 음식은 👉 {random.choice(foods)}")
