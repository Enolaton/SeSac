import streamlit as st
import openai

# 1. API 키 설정 (Secrets 활용)
if "OPENAI_API_KEY" in st.secrets:
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("API 키가 설정되지 않았습니다. .streamlit/openai_key.toml 파일을 확인하세요.")
    st.stop()

def get_gpt_response(gender, age, foods, times, user_prompt):
    system_instruction = """
                    당신은 트렌디한 맛집 가이드입니다. 사용자의 입력에 맞게 맛집을 추천해주세요.
                    1. 사용자의 성별과 연령대에 맞는 추천을 제공합니다.
                    2. 음식 카테고리와 방문 시간대를 고려하여 최적의 장소를 추천합니다.
                    3. 추천 시, 각 장소의 특징과 분위기를 간략히 설명합니다.
                    4. 추천은 3~5개 정도로 제한합니다.
                    5. 이모지를 적절히 사용하여 친근하고 감각적인 톤을 유지합니다.
                    """
    user_message = f"[{gender}/{age}] {', '.join(foods)} 종류를 원하며 시간대는 {', '.join(times)}입니다. 요청: {user_prompt}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system_instruction}, {"role": "user", "content": user_message}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"에러가 발생했습니다 😭: {str(e)}"

# ==========================================
# UI 스타일링 (CSS)
# ==========================================
st.set_page_config(page_title="AI 맛집 큐레이터", layout="centered")

st.markdown("""
    <style>
    /* 배경 및 폰트 설정 */
    .main {
        background-color: #f8f9fa;
    }
    
    /* 카드 스타일 컨테이너 */
    .stSecondaryBlock {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    /* 버튼 스타일 커스텀 */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #FF4B2B 0%, #FF416C 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.6rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(255, 75, 43, 0.4);
    }
    
    /* 결과 박스 스타일 */
    .result-box {
        background-color: #ffffff;
        border-left: 5px solid #FF4B2B;
        padding: 25px;
        border-radius: 10px;
        line-height: 1.6;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 화면 로직
# ==========================================
if 'generated' not in st.session_state:
    st.session_state['generated'] = False
    st.session_state['result_text'] = ""

if not st.session_state['generated']:
    # [입력 화면]
    st.title("🍽️ AI 맛집 큐레이터")
    st.subheader("당신의 취향을 분석하여 최고의 장소를 추천합니다.")
    
    with st.container():
        st.markdown('<div class="stSecondaryBlock">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            gender = st.selectbox(" 성별", ["남성", "여성"])
        with col2:
            age_group = st.selectbox(" 연령대", ["20대", "30대", "40대", "50대", "60대 이상"])

        selected_foods = st.multiselect("🍕 음식 카테고리", ["한식", "양식", "중식", "일식", "분식", "카페/디저트", "고기", "술"])
        selected_times = st.multiselect("⏰ 방문 시간", ["07~09시", "09~11시", "11~13시", "13~15시", "15~17시", "17~19시", "19~21시", "21~23시"])

        st.markdown("---")
        user_prompt = st.text_area("📝 상세 요청 ", placeholder="예: 조용한 분위기의 식당 추천해줘")
        
        if st.button("나를 위한 맛집 찾기 ✨"):
            if not selected_foods or not selected_times:
                st.error("카테고리와 시간을 선택해주세요!")
            else:
                with st.spinner('당신의 취향을 분석하고 있습니다...'):
                    answer = get_gpt_response(gender, age_group, selected_foods, selected_times, user_prompt)
                    st.session_state['result_text'] = answer
                    st.session_state['generated'] = True
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # [결과 화면]
    st.title("✨ AI 큐레이션 결과")
    st.write("당신만을 위해 엄선된 리스트입니다.")
    
    st.markdown(f"""
    <div class="result-box">
        {st.session_state['result_text'].replace('\n', '<br>')}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🔄 다시 검색하기"):
        st.session_state['generated'] = False
        st.rerun()