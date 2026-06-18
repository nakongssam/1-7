import streamlit as st
import random
import time
import pandas as pd

# 페이지 기본 설정
st.set_page_config(page_title="청소 당번 룰렛", page_icon="🧹", layout="centered")

# 메인 타이틀
st.title("🧹 두근두근 청소 당번 룰렛")
st.write("누가 어떤 구역을 맡게 될까요? 공정하고 재미있게 오늘의 당번을 뽑아보세요!")

# 사이드바: 설정 입력
with st.sidebar:
    st.header("⚙️ 룰렛 설정")
    st.write("명단과 구역을 쉼표(,)로 구분하여 입력해주세요.")
    
    # 기본값은 학교 교실에 맞게 설정되어 있습니다.
    default_students = "김학생, 이학생, 박학생, 최학생, 정학생, 강학생, 조학생, 윤학생"
    students_input = st.text_area("👥 대상자 명단", value=default_students, height=100)
    
    default_tasks = "칠판 닦기, 분리수거, 바닥 쓸기, 복도 청소"
    tasks_input = st.text_area("🗑️ 청소 구역", value=default_tasks, height=100)
    
    st.info("💡 **안내:** 대상자 수가 청소 구역 수보다 많으면 남은 인원은 '휴식'으로 자동 배정됩니다.")

# 입력값 전처리 (공백 제거 및 리스트화)
try:
    students = [s.strip() for s in students_input.split(",") if s.strip()]
    tasks = [t.strip() for t in tasks_input.split(",") if t.strip()]
except Exception as e:
    st.error(f"입력값을 처리하는 중 오류가 발생했습니다: {e}")
    students, tasks = [], []

# 메인 화면: 룰렛 실행 버튼
if st.button("🎲 룰렛 돌리기!", type="primary", use_container_width=True):
    # 예외 처리: 입력값이 비어있는 경우
    if not students or not tasks:
        st.warning("⚠️ 대상자 명단과 청소 구역을 모두 입력해주세요!")
    # 예외 처리: 구역이 사람보다 많은 경우
    elif len(students) < len(tasks):
        st.error(f"⚠️ 청소 구역({len(tasks)}개)이 대상자 수({len(students)}명)보다 많습니다. 인원을 더 추가하거나 구역을 줄여주세요.")
    else:
        # 긴장감을 주는 로딩 애니메이션
        with st.spinner("운명의 룰렛이 돌아가는 중... 🌀"):
            time.sleep(1.5) # 1.5초 대기
            
            # 리스트 무작위 섞기
            random.shuffle(students)
            
            # 결과 매핑
            assignments = []
            
            # 1. 청소 구역 배정
            for i in range(len(tasks)):
                assignments.append({"청소 구역": tasks[i], "담당자": students[i]})
            
            # 2. 남은 인원 휴식 배정
            for i in range(len(tasks), len(students)):
                assignments.append({"청소 구역": "✨ 휴식 (면제)", "담당자": students[i]})
                
            # 데이터프레임 생성
            df = pd.DataFrame(assignments)
            
            # 성공 메시지 및 애니메이션
            st.success("🎉 오늘의 청소 당번이 결정되었습니다!")
            st.balloons()
            
            # 결과 표 출력 (인덱스 숨김)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # CSV 다운로드 기능
            csv = df.to_csv(index=False).encode('utf-8-sig') # 한글 깨짐 방지를 위해 utf-8-sig 사용
            st.download_button(
                label="📥 결과 다운로드 (CSV)",
                data=csv,
                file_name='오늘의_청소당번.csv',
                mime='text/csv',
            )
