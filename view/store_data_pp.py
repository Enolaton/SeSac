import jsonlines
import openai
import streamlit as st


file_path = 'view/중랑구_store_cards(600,100).jsonl'

if "OPENAI_API_KEY" in st.secrets:
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("API 키가 설정되지 않았습니다. .streamlit/secrets.toml을 확인하세요.")
    st.stop()


with jsonlines.open(file_path, mode='r') as f:
    for line in f:
        if int(line['review_count']) < 10:
            continue
        elif int(line['review_count']) < 20:
            summaries = []
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "사용자의 리뷰를 요약하는 전문가입니다. 이 리뷰의 핵심 내용을 간결하게 1~2문장으로 요약하세요."},
                    {"role": "user", "content": line['merged_review']}
                ],
                max_tokens=100
            )
            summaries.append(response.choices[0].message.content)
            print(summaries)
