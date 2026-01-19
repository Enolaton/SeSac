from langchain_text_splitters import RecursiveCharacterTextSplitter

def process_long_prompt(client, text):
    if len(text) < 300:
        return text

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=200, chunk_overlap=50, separators=["\n\n", "\n", ". ", " "]
    )
    chunks = text_splitter.split_text(text)
    
    summaries = []
    for chunk in chunks:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "맛집 추천에 필요한 핵심 조건만 한 문장으로 요약하세요."},
                {"role": "user", "content": chunk}
            ],
            max_tokens=100
        )
        summaries.append(response.choices[0].message.content)
    return " | ".join(summaries)

def get_gpt_response(client, gender, age, foods, times, processed_prompt, data_cats):
    system_msg = f"당신은 맛집 전문가입니다. 데이터 결과인 [{', '.join(data_cats)}]를 참고하여 추천하세요."
    user_msg = f"사용자: {gender}/{age}, 선호: {foods}, 시간: {times}, 요청: {processed_prompt}"
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}]
    )
    return response.choices[0].message.content