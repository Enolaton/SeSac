import streamlit as st
import openai
import json
from datetime import datetime
from collections import defaultdict
# 청킹을 위한 라이브러리 추가
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. API 키 및 클라이언트 설정
if "OPENAI_API_KEY" in st.secrets:
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("API 키가 설정되지 않았습니다. .streamlit/secrets.toml을 확인하세요.")
    st.stop()

# 2. JSON 데이터 로드
@st.cache_data
def load_data():
    try:
        with open('category_recommendation_map.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("category_recommendation_map.json 파일을 찾을 수 없습니다.")
        return {}

recommendation_data = load_data()

# 3. 시간 문자열 파싱 (예: "11~13시" -> [11, 12])
def parse_time_ranges(time_ranges):
    hours = []
    for tr in time_ranges:
        parts = tr.replace('시', '').split('~')
        start, end = int(parts[0]), int(parts[1])
        hours.extend(range(start, end))
    return hours

# 4. JSON 기반 통계 분석 함수
def analyze_data(gender, age_group, selected_times):
    g_code = "M" if gender == "남성" else "F"
    a_code = {"20대": "2", "30대": "3", "40대": "4", "50대": "5", "60대 이상": "6"}.get(age_group, "2")
    target_hours = parse_time_ranges(selected_times) if selected_times else [int(datetime.now().strftime("%H")), int(datetime.now().strftime("%H"))+1]
    
    score_map = defaultdict(float)
    for day in range(1, 8):
        for hour in target_hours:
            key = f"{a_code}_{g_code}_{day}_{hour}"
            if key in recommendation_data:
                for item in recommendation_data[key]:
                    score_map[item['category']] += item['score']
    
    sorted_cats = sorted(score_map.items(), key=lambda x: x[1], reverse=True)
    return [cat[0] for cat in sorted_cats[:3]]

# 5. 프롬프트 청킹 및 요약 로직 (추가된 부분)
def process_long_prompt(text):
    # 10자 이상일 경우에만 청킹 진행 (기준은 조절 가능)
    if len(text) < 10:
        return text

    # 1) 청킹 설정
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=7,      # 한 조각당 글자 수
        chunk_overlap=3,    # 조각 간 겹치는 부분 (문맥 유지)
        separators=["\n\n", "\n", ". ", " "]
    )
    chunks = text_splitter.split_text(text)
    
    # 2) 각 청크에서 핵심 키워드/요구사항 추출 (GPT 활용)
    summaries = []
    for i, chunk in enumerate(chunks):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "사용자의 긴 요구사항 중 맛집 추천에 필요한 핵심 조건만 한 문장으로 요약하세요."},
                {"role": "user", "content": chunk}
            ],
            max_tokens=100
        )
        summaries.append(response.choices[0].message.content)
    
    # 요약된 내용을 다시 합침
    return " | ".join(summaries)

# 6. GPT 최종 답변 생성 함수
def get_gpt_response(gender, age, foods, times, processed_prompt, data_cats):
    system_msg = f"""
    당신은 데이터 기반 맛집 전문가입니다.
    통계적으로 이 사용자와 비슷한 그룹은 현재 [{', '.join(data_cats)}] 카테고리를 선호합니다.
    분석된 데이터와 사용자의 정돈된 요청을 조합해 최적의 맛집 3~5곳을 추천하세요. 
    이모지를 섞어 친절하게 답변하세요.
    """
    user_msg = f"""
    - 사용자: {gender}/{age}
    - 선호 카테고리: {foods if foods else '없음'}
    - 희망 시간: {times if times else '무관'}
    - 정돈된 상세 요청: {processed_prompt}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"GPT 호출 중 오류 발생: {e}"

# ==========================================
# UI 레이아웃
# ==========================================
st.set_page_config(page_title="AI 맛집 큐레이터", layout="centered")

st.markdown("""
    <style>
    .stSecondaryBlock { background-color: #ffffff; padding: 30px; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
    div.stButton > button { background: linear-gradient(90deg, #FF4B2B 0%, #FF416C 100%); color: white; border-radius: 25px; width: 100%; border: none; font-weight: bold; }
    .result-box { background-color: #f9f9f9; padding: 20px; border-left: 5px solid #FF4B2B; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

if 'generated' not in st.session_state:
    st.session_state['generated'] = False

now = datetime.now()
weekday_korean = ['월', '화', '수', '목', '금', '토', '일'][now.weekday()]
current_time_str = now.strftime(f"%Y-%m-%d ({weekday_korean}) %H:%M")

if not st.session_state['generated']:
    st.title("🍽️ AI 맛집 추천 서비스")
    st.write("사용자 입력에 기반해 최적의 맛집을 추천합니다.")
    
    with st.container():
        st.markdown('<div class="stSecondaryBlock">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            gender = st.selectbox("🙋‍♂️ 성별", ["남성", "여성"])
        with col2:
            age_group = st.selectbox("🎂 연령대", ["20대", "30대", "40대", "50대", "60대 이상"])

        selected_foods = st.multiselect("🍕 선호 음식 카테고리", ["한식", "양식", "중식", "일식", "분식", "카페/디저트", "고기", "술"], 
                                        placeholder="원하는 카테고리를 선택하세요")
        selected_times = st.multiselect(f"⏰ 방문 시간 (현재: {current_time_str})", 
                                        ["07~09시", "09~11시", "11~13시", "13~15시", "15~17시", "17~19시", "19~21시", "21~23시"], 
                                        placeholder="시간대를 선택하세요")

        user_prompt = st.text_area("📝 상세 요청", placeholder="예: 소개팅 맛집 추천해줘 / 친구들끼리 술마시기 좋은 장소 추천해줘 / 분위기 좋은 데이트 맛집 추천해줘")

        if st.button(" 추천 받기 "):
            with st.spinner('요청 내용을 분석하고 맛집을 찾는 중입니다...'):
                # 1) 통계 데이터 분석
                top_cats = analyze_data(gender, age_group, selected_times)
                
                # 2) 긴 프롬프트 청킹 및 정제 (핵심 로직 적용)
                refined_prompt = process_long_prompt(user_prompt)
                
                # 3) 최종 GPT 응답 생성
                result = get_gpt_response(gender, age_group, selected_foods, selected_times, refined_prompt, top_cats)
                
                st.session_state['res'] = result
                st.session_state['cats'] = top_cats
                st.session_state['generated'] = True
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.title("✨ 분석 및 추천 결과")
    st.info(f"💡 분석 결과, 해당 시간대 유사 그룹은 **{', '.join(st.session_state['cats'])}**를 가장 선호합니다.")
    
    st.markdown(f"<div class='result-box'>{st.session_state['res'].replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
    
    if st.button("🔄 다시 설정하기"):
        st.session_state['generated'] = False
        st.rerun()