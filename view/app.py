import streamlit as st
import openai
from datetime import datetime
# 분리한 모듈 불러오기
import login
import data_utils
import gpt_utils

# 1. 환경 설정
st.set_page_config(page_title="AI 맛집 큐레이터", layout="centered")

if "OPENAI_API_KEY" in st.secrets:
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("API 키가 없습니다.")
    st.stop()

# 2. 세션 상태 초기화
if 'authenticated' not in st.session_state: st.session_state['authenticated'] = False
if 'generated' not in st.session_state: st.session_state['generated'] = False

# 3. 화면 분기 로직
if not st.session_state['authenticated']:
    login.login_screen()
else:
    # --- [사이드바] ---
    with st.sidebar:
        st.write("🎉 환영합니다!")
        if st.button("로그아웃"): auth.logout()

    # --- [메인 페이지] ---
    if not st.session_state['generated']:
        st.title("🍽️ AI 맛집 큐레이터")
        recommendation_data = data_utils.load_data()
        
        with st.container():
            # (입력 위젯 CSS 주입 생략 - 이전과 동일하게 추가 가능)
            col1, col2 = st.columns(2)
            gender = col1.selectbox("🙋‍♂️ 성별", ["남성", "여성"])
            age_group = col2.selectbox("🎂 연령대", ["20대", "30대", "40대", "50대", "60대 이상"])
            selected_foods = st.multiselect("🍕 카테고리", ["한식", "양식", "중식", "일식", "분식", "고기", "술"], placeholder="카테고리 선택")
            selected_times = st.multiselect("⏰ 시간대", ["07~09시", "11~13시", "17~19시", "21~23시"], placeholder="시간대 선택")
            user_prompt = st.text_area("📝 상세 요청", placeholder="요구사항을 입력하세요")

            if st.button("추천 받기 ✨"):
                with st.spinner('분석 중...'):
                    top_cats = data_utils.analyze_data(recommendation_data, gender, age_group, selected_times)
                    refined_prompt = gpt_utils.process_long_prompt(client, user_prompt)
                    result = gpt_utils.get_gpt_response(client, gender, age_group, selected_foods, selected_times, refined_prompt, top_cats)
                    
                    st.session_state['res'] = result
                    st.session_state['cats'] = top_cats
                    st.session_state['generated'] = True
                    st.rerun()
    else:
        st.title("✨ 분석 결과")
        st.info(f"💡 통계 분석 상위 카테고리: {', '.join(st.session_state['cats'])}")
        st.markdown(f"<div style='padding:20px; background:#f9f9f9; border-left:5px solid #FF4B2B;'>{st.session_state['res'].replace('\n', '<br>')}</div>", unsafe_allow_html=True)
        
        if st.button("🔄 다시 하기"):
            st.session_state['generated'] = False
            st.rerun()