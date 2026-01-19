import json
import streamlit as st
from collections import defaultdict

@st.cache_data
def load_data():
    try:
        with open('category_recommendation_map.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def parse_time_ranges(time_ranges):
    hours = []
    for tr in time_ranges:
        parts = tr.replace('시', '').split('~')
        start, end = int(parts[0]), int(parts[1])
        hours.extend(range(start, end))
    return hours

def analyze_data(recommendation_data, gender, age_group, selected_times):
    g_code = "M" if gender == "남성" else "F"
    a_code = {"20대": "2", "30대": "3", "40대": "4", "50대": "5", "60대 이상": "6"}.get(age_group, "2")
    target_hours = parse_time_ranges(selected_times) if selected_times else range(24)
    
    score_map = defaultdict(float)
    for day in range(1, 8):
        for hour in target_hours:
            key = f"{a_code}_{g_code}_{day}_{hour}"
            if key in recommendation_data:
                for item in recommendation_data[key]:
                    score_map[item['category']] += item['score']
    
    sorted_cats = sorted(score_map.items(), key=lambda x: x[1], reverse=True)
    return [cat[0] for cat in sorted_cats[:3]]