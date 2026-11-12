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
# ---------------------------------------------------------
DATA_DIR = "."
DATA_FILENAME = "products.csv"
DATA_PATH = os.path.join(DATA_DIR, DATA_FILENAME)
DATA_ENCODING = "utf-8"

RECORD_DIR = "내_기록"
RECORD_FILE = os.path.join(RECORD_DIR, "데이터_소개_기록.json")

# 자동으로 제공할 기본 우리말 뜻 사전 (자동 번역 및 매핑)
DEFAULT_COLUMN_MEANINGS = {
    "product_id": "제품 고유 ID",
    "brand_id": "브랜드 고유 ID",
    "barcode_ean": "상품 바코드 번호 (EAN)",
    "name": "화장품 제품명",
    "obf_categories_tags": "제품 카테고리 태그 (분류용)",
    "raw_ingredient_text": "전성분 원문 텍스트",
    "created_at": "데이터 생성 일시",
}

DEFAULT_DATA_SOURCE = "INCIDB (Skincare and Cosmetics INCI Formulations) - 자동 번역 및 연동 데이터셋"


def load_saved_notes():
    """내_기록 폴더의 JSON 파일에서 저장된 열 우리말 뜻과 데이터 출처를 불러옵니다."""
    if not os.path.exists(RECORD_DIR):
        os.makedirs(RECORD_DIR, exist_ok=True)

    if not os.path.exists(RECORD_FILE):
        default_data = {
            "column_meanings": DEFAULT_COLUMN_MEANINGS,
            "data_source": DEFAULT_DATA_SOURCE,
        }
        with open(RECORD_FILE, "w", encoding="utf-8") as f:
            json.dump(default_data, f, ensure_ascii=False, indent=2)
        return default_data

    try:
        with open(RECORD_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not data.get("column_meanings"):
                data["column_meanings"] = DEFAULT_COLUMN_MEANINGS
            if not data.get("data_source"):
                data["data_source"] = DEFAULT_DATA_SOURCE
            return data
    except Exception:
        return {
            "column_meanings": DEFAULT_COLUMN_MEANINGS,
            "data_source": DEFAULT_DATA_SOURCE,
        }


def save_notes(column_meanings: dict, data_source: str):
    """입력한 열 우리말 뜻과 데이터 출처를 JSON 파일에 저장합니다."""
    if not os.path.exists(RECORD_DIR):
        os.makedirs(RECORD_DIR, exist_ok=True)

    payload = {
        "column_meanings": column_meanings,
        "data_source": data_source,
    }
    with open(RECORD_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


@st.cache_data
def load_dataset(filepath: str, encoding: str):
    """실제 CSV 파일을 파이프(|) 구분자로 불러옵니다."""
    df = pd.read_csv(filepath, sep="|", encoding=encoding)
    return df, filepath


def get_friendly_dtype(series: pd.Series) -> str:
    """판다스 데이터 타입을 이해하기 쉬운 값의 종류로 변환합니다."""
    if pd.api.types.is_integer_dtype(series):
        return "정수 (int)"
    elif pd.api.types.is_float_dtype(series):
        return "실수 (float)"
    elif pd.api.types.is_bool_dtype(series):
        return "참/거짓 (bool)"
    else:
        return "텍스트 (string)"


# ---------------------------------------------------------
# 앱 상단 헤더
# ---------------------------------------------------------
st.markdown(
    '<div class="main-title">🧴 화장품 성분 분석 실습실</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-caption">INCIDB 데이터를 활용하여 화장품 성분과 제품 정보를 탐색하는 실습 공간입니다.</div>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# 데이터 불러오기 및 예외 처리
# ---------------------------------------------------------
try:
    df, loaded_path = load_dataset(DATA_PATH, DATA_ENCODING)
except FileNotFoundError:
    st.error(
        f"📂 데이터 파일을 찾을 수 없습니다: `{DATA_PATH}`\n\n"
        f"`main.py`와 같은 폴더에 `{DATA_FILENAME}` 파일이 위치해 있는지 확인해 주세요."
    )
    st.stop()
except UnicodeDecodeError as e:
    st.error(
        f"🔤 파일 인코딩({DATA_ENCODING})을 읽는 중 오류가 발생했습니다.\n\n"
        f"상세 원인: {e}"
    )
    st.stop()
except Exception as e:
    st.error(
        f"⚠️ CSV 파일을 불러오는 중 예상치 못한 오류가 발생했습니다.\n\n"
        f"오류 원인: {e}"
    )
    st.stop()

# ---------------------------------------------------------
# 3. 첫 화면: 데이터 소개
# ---------------------------------------------------------
st.markdown(
    '<div class="section-header">1. 데이터 한눈에 보기</div>',
    unsafe_allow_html=True,
)

# 실제 CSV 구조 기반 지표 계산
total_products = len(df)
total_columns = len(df.columns)

if "raw_ingredient_text" in df.columns:
    valid_ingredient_count = int(df
