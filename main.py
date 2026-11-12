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
# 2. 데이터 및 기록 경로 설정 (product.csv 반영)
# ---------------------------------------------------------
DATA_DIR = "."
DATA_FILENAME = "product.csv"
DATA_PATH = os.path.join(DATA_DIR, DATA_FILENAME)
DATA_ENCODING = "utf-8"

RECORD_DIR = "내_기록"
RECORD_FILE = os.path.join(RECORD_DIR, "데이터_소개_기록.json")


def load_saved_notes():
    """내_기록 폴더의 JSON 파일에서 저장된 열 우리말 뜻과 데이터 출처를 불러옵니다."""
    if not os.path.exists(RECORD_DIR):
        os.makedirs(RECORD_DIR, exist_ok=True)

    if not os.path.exists(RECORD_FILE):
        default_data = {"column_meanings": {}, "data_source": ""}
        with open(RECORD_FILE, "w", encoding="utf-8") as f:
            json.dump(default_data, f, ensure_ascii=False, indent=2)
        return default_data

    try:
        with open(RECORD_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "column_meanings" not in data:
                data["column_meanings"] = {}
            if "data_source" not in data:
                data["data_source"] = ""
            return data
    except Exception:
        return {"column_meanings": {}, "data_source": ""}


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
    target_path = filepath
    if not os.path.exists(target_path) and os.path.exists("products.csv"):
        target_path = "products.csv"

    df = pd.read_csv(target_path, sep="|", encoding=encoding)
    return df, target_path


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

# 성분/제품 관련 유효 데이터 수 (예: 전성분이 입력된 제품 수)
if "raw_ingredient_text" in df.columns:
    valid_ingredient_count = int(df["raw_ingredient_text"].notna().sum())
    ingredient_desc = "전성분 정보 보유 제품 수"
else:
    valid_ingredient_count = int(df.dropna().shape[0])
    ingredient_desc = "결측치 없는 완전한 제품 수"

ingredient_ratio = (
    (valid_ingredient_count / total_products * 100) if total_products > 0 else 0.0
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">전체 제품 수</div>
            <div class="metric-value">{total_products:,}개</div>
            <div class="metric-sub">파일: {os.path.basename(loaded_path)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">전체 열 개수</div>
            <div class="metric-value">{total_columns}개</div>
            <div class="metric-sub">인코딩: {DATA_ENCODING.upper()}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">분석 주요 데이터 수</div>
            <div class="metric-value">{valid_ingredient_count:,}개</div>
            <div class="metric-sub">{ingredient_desc}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">주요 데이터의 비율</div>
            <div class="metric-value">{ingredient_ratio:.1f}%</div>
            <div class="metric-sub">전체 대비 유효 성분 비율</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------
# 열 정보 표 (우리말 뜻 직접 입력 및 JSON 자동 저장)
# ---------------------------------------------------------
st.markdown(
    '<div class="section-header">2. 데이터 열(Column) 구조 및 우리말 뜻 정리</div>',
    unsafe_allow_html=True,
)
st.caption("교재를 참고하여 '우리말 뜻' 칸을 직접 입력해 보세요. 입력 내용은 내_기록 폴더에 자동 저장됩니다.")

saved_notes = load_saved_notes()
saved_meanings = saved_notes.get("column_meanings", {})
saved_source = saved_notes.get("data_source", "")

col_info_rows = []
for col_name in df.columns:
    col_info_rows.append(
        {
            "열 이름": col_name,
            "우리말 뜻": saved_meanings.get(col_name, ""),
            "값의 종류": get_friendly_dtype(df[col_name]),
            "빈 값 개수": int(df[col_name].isna().sum()),
        }
    )

col_info_df = pd.DataFrame(col_info_rows)

edited_col_df = st.data_editor(
    col_info_df,
    use_container_width=True,
    hide_index=True,
    disabled=["열 이름", "값의 종류", "빈 값 개수"],
    column_config={
        "열 이름": st.column_config.TextColumn("열 이름", width="medium"),
        "우리말 뜻": st.column_config.TextColumn(
            "우리말 뜻 (교재를 보고 직접 입력)",
            help="이곳을 더블클릭하여 교재에 나오는 우리말 뜻을 입력하세요.",
            width="large",
        ),
        "값의 종류": st.column_config.TextColumn("값의 종류", width="small"),
        "빈 값 개수": st.column_config.NumberColumn("빈 값 개수", format="%d개", width="small"),
    },
    key="column_info_editor",
)

# 편집된 우리말 뜻 추출
updated_meanings = {
    row["열 이름"]: (row["우리말 뜻"] if pd.notna(row["우리말 뜻"]) else "")
    for _, row in edited_col_df.iterrows()
}

# ---------------------------------------------------------
# 데이터 처음 5줄 원본 미리보기
# ---------------------------------------------------------
st.markdown(
    '<div class="section-header">3. 원본 데이터 미리보기 (처음 5줄)</div>',
    unsafe_allow_html=True,
)
st.dataframe(df.head(5), use_container_width=True)

# ---------------------------------------------------------
# 맨 아래: 데이터 출처 입력 및 자동 저장
# ---------------------------------------------------------
st.markdown(
    '<div class="section-header">4. 데이터 출처 기록</div>',
    unsafe_allow_html=True,
)

updated_source = st.text_area(
    "데이터 출처 (교재를 보고 직접 입력해 주세요)",
    value=saved_source,
    placeholder="",
    height=90,
    key="data_source_input",
)

# 변경 사항이 감지되면 '내_기록' 폴더 내 JSON 파일에 자동 업데이트
if updated_meanings != saved_meanings or updated_source != saved_source:
    save_notes(updated_meanings, updated_source)
    st.toast("입력한 내용이 '내_기록' 폴더의 JSON 파일에 자동 저장되었습니다.", icon="💾")

st.caption(f"📁 자동 저장 위치: `{RECORD_FILE}`")
