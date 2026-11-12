import json
import os
import pandas as pd
import streamlit as st

# ---------------------------------------------------------
# 1. 앱 기본 설정
# ---------------------------------------------------------
st.set_page_config(
    page_title="화장품 성분 분석 실습실",
    page_icon="🧴",
    layout="wide",
)

# 화장품 브랜드 감성(베이지, 연한 핑크, 아이보리) 커스텀 CSS
st.markdown(
    """
    <style>
    /* 전체 배경 아이보리 톤 */
    .stApp {
        background-color: #FAF7F2;
        color: #3E3632;
    }
    /* 메인 타이틀 스타일 */
    .main-title {
        font-size: 2.3rem;
        font-weight: 700;
        color: #4A3B36;
        padding-bottom: 0.4rem;
        border-bottom: 2px solid #EBD8D0;
        margin-bottom: 1.2rem;
    }
    .sub-caption {
        font-size: 1rem;
        color: #7D6B65;
        margin-bottom: 1.8rem;
    }
    /* 섹션 헤더 스타일 */
    .section-header {
        font-size: 1.35rem;
        font-weight: 600;
        color: #5C4942;
        margin-top: 1.8rem;
        margin-bottom: 0.8rem;
        padding-left: 0.6rem;
        border-left: 4px solid #E2A9A1;
    }
    /* 큰 숫자 카드 디자인 */
    .metric-card {
        background: linear-gradient(135deg, #FFFDFB 0%, #F7EAE6 100%);
        border: 1px solid #EAD7D1;
        border-radius: 16px;
        padding: 1.3rem 1.2rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(92, 73, 66, 0.05);
        margin-bottom: 1rem;
    }
    .metric-label {
        font-size: 0.92rem;
        font-weight: 600;
        color: #7D6B65;
        margin-bottom: 0.45rem;
    }
    .metric-value {
        font-size: 2.0rem;
        font-weight: 800;
        color: #4A3B36;
        line-height: 1.2;
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #9C8881;
        margin-top: 0.35rem;
    }
    /* 버튼 스타일 */
    div.stButton > button {
        background-color: #E2A9A1;
        color: #FFFFFF;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1.2rem;
        font-weight: 600;
    }
    div.stButton > button:hover {
        background-color: #D4938A;
        color: #FFFFFF;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# 2. 데이터 및 기록 경로 설정
