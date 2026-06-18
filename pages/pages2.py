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

# 시각적 룰렛 HTML/CSS/JS 생성 함수
def get_wheel_html(student_names, winner_index):
    """원형 룰렛을 생성하는 HTML/CSS/JS 문자열을 반환합니다."""
    
    # 세그먼트 수
    num_students = len(student_names)
    angle_per_segment = 360 / num_students
    
    # 색상 리스트 (최대 20명, 반복 사용)
    colors = [
        "#f44336", "#e91e63", "#9c27b0", "#673ab7", "#3f51b5",
        "#2196f3", "#03a9f4", "#00bcd4", "#009688", "#4caf50",
        "#8bc34a", "#cddc39", "#ffeb3b", "#ffc107", "#ff9800",
        "#ff5722", "#795548", "#9e9e9e", "#607d8b", "#333333"
    ]
    
    # HTML 구성
    html_content = f"""
    <style>
        .roulette-container {{
            position: relative;
            width: 400px;
            height: 400px;
            margin: 20px auto;
        }}
        .wheel {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border-radius: 50%;
            overflow: hidden;
            border: 5px solid #ccc;
            box-shadow: 0 0 10px rgba(0,0,0,0.2);
            transition: transform 5s cubic-bezier(0.1, 0.7, 0.2, 1); /* 부드러운 감속 */
        }}
        .pointer {{
            position: absolute;
            top: -20px;
            left: 50%;
            transform: translateX(-50%);
            width: 0;
            height: 0;
            border-left: 20px solid transparent;
            border-right: 20px solid transparent;
            border-top: 30px solid #f44336; /* 빨간색 포인터 */
            z-index: 10;
        }}
        .segment {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            transform-origin: 50% 50%;
        }}
        .segment-content {{
            position: absolute;
            left: 50%;
            transform: translateX(-50%);
            font-weight: bold;
            font-size: 16px;
            color: white;
            writing-mode: vertical-rl; /* 세로 텍스트 */
            text-orientation: upright;
            padding-bottom: 70px; /* 원 바깥으로 이동 */
        }}
    </style>
    
    <div class="roulette-container">
        <div class="pointer"></div>
        <div class="wheel" id="wheel">
    """
    
    # 세그먼트 생성
    for i, name in enumerate(student_names):
        color = colors[i % len(colors)]
        angle = angle_per_segment * i
        html_content += f"""
            <div class="segment" style="transform: rotate({angle}deg); background-color: {color};">
                <span class="segment-content">{name}</span>
            </div>
        """
        
    html_content += """
        </div>
    </div>
    <script>
        // Python에서 미리 계산된 최종 각도
        var finalAngle = Python.get_final_angle(); 
        
        // 룰렛 회전 애니메이션 실행
        setTimeout(function() {
            var wheel = document.getElementById('wheel');
            // 부드러운 회전을 위해 여러 바퀴 돌림 (360 * 10 = 3600도) + 최종 각도
            wheel.style.transform = 'rotate(' + (360 * 10 + finalAngle) + 'deg)'; 
        }, 100);
    </script>
    """
    return html_content

# 세션 상태 초기화 (결과 저장을 위해)
if 'result_df' not in st.session_state:
    st.session_state['result_df'] = None
if 'show_wheel' not in st.session_state:
    st.session_state['show_wheel'] = False
if 'student_names' not in st.session_state:
    st.session_state['student_names'] = []
if 'winner_index' not in st.session_state:
    st.session_state['winner_index'] = -1


# 메인 화면: 룰렛 실행 버튼
if st.button("🎲 룰렛 돌리기!", type="primary", use_container_width=True):
    # 예외 처리: 입력값이 비어있는 경우
    if not students or not tasks:
        st.warning("⚠️ 대상자 명단과 청소 구역을 모두 입력해주세요!")
        st.session_state['result_df'] = None
        st.session_state['show_wheel'] = False
    # 예외 처리: 구역이 사람보다 많은 경우
    elif len(students) < len(tasks):
        st.error(f"⚠️ 청소 구역({len(tasks)}개)이 대상자 수({len(students)}명)보다 많습니다. 인원을 더 추가하거나 구역을 줄여주세요.")
        st.session_state['result_df'] = None
        st.session_state['show_wheel'] = False
    else:
        # 애니메이션 상태 활성화
        st.session_state['show_wheel'] = True
        
        # 1. 대상자 무작위 섞기
        random.shuffle(students)
        st.session_state['student_names'] = students
        
        # 2. 당번 배정 logic
        assignments = []
        for i in range(len(tasks)):
            assignments.append({"청소 구역": tasks[i], "담당자": students[i]})
        for i in range(len(tasks), len(students)):
            assignments.append({"청소 구역": "✨ 휴식 (면제)", "담당자": students[i]})
            
        # 데이터프레임 생성 및 저장
        st.session_state['result_df'] = pd.DataFrame(assignments)
        
        # 3. 시각적 '승자' (포인터가 가리킬 사람) 인덱스 결정 (첫 번째 비휴식 사람)
        # 휴식 없이 모두 당번일 경우 첫 번째 사람이 승자
        winner_idx = 0
        for i in range(len(tasks), len(students)):
             if st.session_state['result_df'].iloc[i]["청소 구역"] != "✨ 휴식 (면제)":
                winner_idx = i
                break
        st.session_state['winner_index'] = winner_idx
        

# 룰렛 애니메이션 출력
if st.session_state['show_wheel']:
    # Python에서 JS로 데이터를 넘기기 위한 임시 함수 정의 (Streamlit-specific hack)
    # 이 부분은 이 앱 고유의 안정적인 방식입니다.
    def get_final_angle_for_js():
        """룰렛 포인터가 winner_index의 세그먼트를 가리키도록 최종 각도를 계산합니다."""
        num_students = len(st.session_state['student_names'])
        angle_per_segment = 360 / num_students
        winner_idx = st.session_state['winner_index']
        # 포인터는 상단에 있으므로, 세그먼트의 중간이 상단을 가리키도록 각도 계산
        # 360 - (세그먼트 중간 각도) + 약간의 무작위 오차(0~세그먼트/4)
        base_angle = 360 - (angle_per_segment * winner_idx + angle_per_segment / 2)
        random_offset = random.uniform(-angle_per_segment / 4, angle_per_segment / 4)
        return base_angle + random_offset

    # HTML 룰렛 렌더링
    st.write("---") # 구분선
    st.components.v1.html(
        get_wheel_html(st.session_state['student_names'], st.session_state['winner_index']),
        height=600 # 룰렛 크기에 맞춰 충분한 높이 확보
    )
    
    # 긴장감을 주는 로딩 애니메이션 및 대기
    with st.spinner("운명의 룰렛이 돌아가는 중... 🌀"):
        time.sleep(5) # JS 애니메이션 시간(5초)과 동일하게 대기

    # 대기 후 결과 출력
    df = st.session_state['result_df']
    st.success("🎉 오늘의 청소 당번이 결정되었습니다!")
    st.balloons()
    
    # 결과 표 출력 (인덱스 숨김)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # CSV 다운로드 기능
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 결과 다운로드 (CSV)",
        data=csv,
        file_name='오늘의_청소당번.csv',
        mime='text/csv',
    )
    
    # visual 상태 초기화 (다음 클릭을 위해)
    st.session_state['show_wheel'] = False
