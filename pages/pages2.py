import streamlit as st
import random
import time
import math
import pandas as pd

# 페이지 기본 설정
st.set_page_config(page_title="청소 당번 룰렛", page_icon="🧹", layout="centered")

# 메인 타이틀
st.title("🧹 두근두근 청소 당번 룰렛")
st.write("메인 화면에서 명단을 입력하고 바로 룰렛을 돌려보세요!")

# 메인 화면 내 입력 메뉴 (2열 구성)
col1, col2 = st.columns(2)

with col1:
    default_students = "김학생, 이학생, 박학생, 최학생, 정학생, 강학생, 조학생, 윤학생"
    students_input = st.text_area("👥 대상자 명단 (쉼표로 구분)", value=default_students, height=120)

with col2:
    default_tasks = "칠판 닦기, 분리수거, 바닥 쓸기, 복도 청소"
    tasks_input = st.text_area("🗑️ 청소 구역 (쉼표로 구분)", value=default_tasks, height=120)

st.caption("💡 **안내:** 인원이 구역보다 많으면 남은 사람은 '✨ 휴식 (면제)'으로 자동 배정됩니다.")

# 입력값 전처리
try:
    students = [s.strip() for s in students_input.split(",") if s.strip()]
    tasks = [t.strip() for t in tasks_input.split(",") if t.strip()]
except Exception as e:
    st.error(f"입력값 처리 중 오류 발생: {e}")
    students, tasks = [], []

# SVG 기반 룰렛 HTML 생성 함수 (크기: 300px로 축소)
def generate_wheel_html(student_list, final_spin_angle):
    n = len(student_list)
    angle_per_seg = 360 / n
    
    # 화사하고 직관적인 고유 색상 스펙트럼
    colors = [
        "#FF6B6B", "#4DABF7", "#20C997", "#FFD43B", "#A07EED", 
        "#FF922B", "#38D9A9", "#66d9ff", "#FAA2C1", "#63E6BE",
        "#FF8787", "#748FFC", "#94D82D", "#ffd8a8", "#E599F7"
    ]
    
    svg_paths = ""
    for i, name in enumerate(student_list):
        color = colors[i % len(colors)]
        start_deg = i * angle_per_seg
        end_deg = (i + 1) * angle_per_seg
        mid_deg = (start_deg + end_deg) / 2
        
        # 부채꼴 좌표 계산 (중심 150, 150 / 반지름 140)
        # 단, SVG는 오른쪽(3시 방향)이 0도이므로 각도 그대로 적용
        rad_start = math.radians(start_deg)
        rad_end = math.radians(end_deg)
        
        x1 = 150 + 140 * math.cos(rad_start)
        y1 = 150 + 140 * math.sin(rad_start)
        x2 = 150 + 140 * math.cos(rad_end)
        y2 = 150 + 140 * math.sin(rad_end)
        
        # 큰 호 플래그 설정 (인원이 1명 또는 2명일 때 예외 방지)
        large_arc = 1 if angle_per_seg > 180 else 0
        
        # 부채꼴 패스 생성
        svg_paths += f'<path d="M 150 150 L {x1} {y1} A 140 140 0 {large_arc} 1 {x2} {y2} Z" fill="{color}" stroke="#ffffff" stroke-width="2"/>\n'
        
        # 부채꼴 내부 텍스트 레이아웃 (반지름 방향 배치)
        svg_paths += f'<text x="260" y="154" transform="rotate({mid_deg}, 150, 150)" text-anchor="end" fill="#ffffff" font-size="13px" font-weight="bold">{name}</text>\n'

    html_markup = f"""
    <style>
        .roulette-box {{
            position: relative;
            width: 300px;
            height: 300px;
            margin: 30px auto;
        }}
        .pointer {{
            position: absolute;
            top: -18px;
            left: 50%;
            transform: translateX(-50%);
            width: 0;
            height: 0;
            border-left: 12px solid transparent;
            border-right: 12px solid transparent;
            border-top: 22px solid #E63946; /* 상단 고정 빨간 바늘 */
            z-index: 99;
            filter: drop-shadow(0px 2px 3px rgba(0,0,0,0.3));
        }}
        .wheel-canvas {{
            width: 100%;
            height: 100%;
            border-radius: 50%;
            box-shadow: 0 4px 15px rgba(0,0,0,0.15);
            transition: transform 4s cubic-bezier(0.1, 0.8, 0.1, 1);
        }}
    </style>
    <div class="roulette-box">
        <div class="pointer"></div>
        <div class="wheel-canvas" id="wheel">
            <svg width="300" height="300" viewBox="0 0 300 300">
                <circle cx="150" cy="150" r="142" fill="#e0e0e0"/>
                {svg_paths}
                <circle cx="150" cy="150" r="15" fill="#ffffff" filter="drop-shadow(0px 1px 3px rgba(0,0,0,0.2))"/>
            </svg>
        </div>
    </div>
    <script>
        setTimeout(function() {{
            var element = document.getElementById('wheel');
            element.style.transform = 'rotate({final_spin_angle}deg)';
        }}, 150);
    </script>
    """
    return html_markup

# 세션 상태 초기화
if 'assigned_df' not in st.session_state:
    st.session_state['assigned_df'] = None
if 'trigger_animation' not in st.session_state:
    st.session_state['trigger_animation'] = False
if 'current_students' not in st.session_state:
    st.session_state['current_students'] = []
if 'computed_angle' not in st.session_state:
    st.session_state['computed_angle'] = 0

# 실행 버튼
if st.button("🎲 룰렛 돌리기!", type="primary", use_container_width=True):
    if not students or not tasks:
        st.warning("⚠️ 대상자 명단과 청소 구역을 입력해 주세요.")
        st.session_state['trigger_animation'] = False
    elif len(students) < len(tasks):
        st.error(f"⚠️ 구역 수({len(tasks)}개)가 인원({len(students)}명)보다 많습니다. 명단을 늘리거나 구역을 줄여주세요.")
        st.session_state['trigger_animation'] = False
    else:
        # 데이터 셔플 및 배정 결과 미리 계산
        random.shuffle(students)
        st.session_state['current_students'] = students
        
        final_list = []
        for idx in range(len(tasks)):
            final_list.append({"청소 구역": tasks[idx], "담당자": students[idx]})
        for idx in range(len(tasks), len(students)):
            final_list.append({"청소 구역": "✨ 휴식 (면제)", "담당자": students[idx]})
            
        st.session_state['assigned_df'] = pd.DataFrame(final_list)
        
        # 룰렛 바늘이 12시 방향(270도)에 위치하므로, 당선될 사람의 각도를 계산하여 매칭
        # 회전 후 당선자 칸의 중심이 정확히 270도 지점에 오도록 제어
        total_peeps = len(students)
        seg_width = 360 / total_peeps
        
        # 첫 번째 구역(대장) 당번을 포인터가 가리킬 주인공으로 설정
        target_winner_idx = 0 
        mid_target_angle = (target_winner_idx * seg_width) + (seg_width / 2)
        
        # 시계방향 회전 보정 공식 적용
        rotation_needed = 270 - mid_target_angle
        total_spins = 360 * 8  # 8바퀴 힘차게 돌기
        st.session_state['computed_angle'] = total_spins + rotation_needed
        st.session_state['trigger_animation'] = True

# 애니메이션 시각화 프레임 구현
if st.session_state['trigger_animation']:
    # 축소된 원형 룰렛 컴포넌트 출력
    st.components.v1.html(
        generate_wheel_html(st.session_state['current_students'], st.session_state['computed_angle']),
        height=350
    )
    
    # 회전 시간과 동기화된 스피너 대기 효과
    with st.spinner("운명의 룰렛이 도는 중... 🌀"):
        time.sleep(4.2)
        
    # 결과 리포트 출력
    df_result = st.session_state['assigned_df']
    st.success("🎉 오늘의 청소 배정이 완료되었습니다!")
    st.balloons()
    
    st.dataframe(df_result, use_container_width=True, hide_index=True)
    
    # 엑셀 호환 한글 파일 다운로드
    csv_data = df_result.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 배정 결과 CSV 다운로드",
        data=csv_data,
        file_name='오늘의_청소당번_결과.csv',
        mime='text/csv'
    )
    
    # 상태 리셋으로 연속 실행 보장
    st.session_state['trigger_animation'] = False
