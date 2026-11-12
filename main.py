import json
import os
import urllib.parse
import urllib.request
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
        font-weight: 400;
        color: #9C8881;
        margin-top: 0.35rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# 2. 번역 유틸리티 함수 (Google 번역 무료 API 활용 예시)
# ---------------------------------------------------------
@st.cache_data
def translate_text(text: str) -> str:
    """간단한 영-한 번역을 수행하는 함수 (필요시 사용)"""
    if not isinstance(text, str) or not text.strip():
        return text
    try:
        # 구글 번역 공개 엔드포인트 활용
        url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ko&dt=t&q=" + urllib.parse.quote(text)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            # 번역된 텍스트 조각들 합치기
            translated = "".join([item[0] for item in result[0]])
            return translated
    except Exception:
        # 네트워크 오류나 차단 시 원본 반환
        return text

# ---------------------------------------------------------
# 3. 데이터 및 기록 경로 설정
# ---------------------------------------------------------
DATA_DIR = "."
DATA_FILENAME = "product.csv"
DATA_PATH = os.path.join(DATA_DIR, DATA_FILENAME)
DATA_ENCODING = "utf-8"

RECORD_DIR = "내_기록"
RECORD_FILE = os.path.join(RECORD_DIR, "데이터_소개_기록.json")

def load_saved_notes():
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
    df = pd.read_csv(filepath, sep="|", encoding=encoding)
    return df, filepath

def get_friendly_dtype(series: pd.Series) -> str:
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
st.markdown('<div class="main-title">🧴 화장품 성분 분석 실습실 (자동 번역 기능 탑재)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-caption">INCIDB 데이터를 활용하여 화장품 성분과 제품 정보를 탐색하며, 필요시 영어를 한국어로 자동 번역합니다.</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 데이터 불러오기 및 예외 처리
# ---------------------------------------------------------
try:
    df, loaded_path = load_dataset(DATA_PATH, DATA_ENCODING)
except FileNotFoundError:
    st.error(f"📂 데이터 파일을 찾을 수 없습니다: `{DATA_PATH}`\n\n`main.py`와 같은 폴더에 `{DATA_FILENAME}` 파일이 위치해 있는지 확인해 주세요.")
    st.stop()
except Exception as e:
    st.error(f"⚠️ CSV 파일을 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

# ---------------------------------------------------------
# 사이드바: 자동 번역 옵션 설정
# ---------------------------------------------------------
st.sidebar.header("⚙️ 번역 설정")
enable_translation = st.sidebar.checkbox("영문 컬럼명/데이터 한국어로 자동 번역", value=False, help="체크하면 데이터 안의 영어 텍스트를 한글로 번역하여 보여줍니다.")

# ---------------------------------------------------------
# 3. 첫 화면: 데이터 소개
# ---------------------------------------------------------
st.markdown('<div class="section-header">1. 데이터 한눈에 보기</div>', unsafe_allow_html=True)

total_products = len(df)
total_columns = len(df.columns)

if "raw_ingredient_text" in df.columns:
    valid_ingredient_count = int(df["raw_ingredient_text"].notna().sum())
    ingredient_desc = "전성분 정보 보유 제품 수"
else:
    valid_ingredient_count = int(df.dropna().shape[0])
    ingredient_desc = "결측치 없는 완전한 제품 수"

ingredient_ratio = (valid_ingredient_count / total_products * 100) if total_products > 0 else 0.0

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">전체 제품 수</div>
            <div class="metric-value">{total_products:,}개</div>
            <div class="metric-sub">파일: {os.path.basename(loaded_path)}</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">전체 열 개수</div>
            <div class="metric-value">{total_columns}개</div>
            <div class="metric-sub">인코딩: {DATA_ENCODING.upper()}</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">분석 주요 데이터 수</div>
            <div class="metric-value">{valid_ingredient_count:,}개</div>
            <div class="metric-sub">{ingredient_desc}</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">주요 데이터의 비율</div>
            <div class="metric-value">{ingredient_ratio:.1f}%</div>
            <div class="metric-sub">전체 대비 유효 성분 비율</div>
        </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 열 정보 표
# ---------------------------------------------------------
st.markdown('<div class="section-header">2. 데이터 열(Column) 구조 및 우리말 뜻 정리</div>', unsafe_allow_html=True)
st.caption("교재를 참고하여 '우리말 뜻' 칸을 직접 입력해 보세요. 사이드바에서 자동 번역을 켤 수도 있습니다.")

saved_notes = load_saved_notes()
saved_meanings = saved_notes.get("column_meanings", {})
saved_source = saved_notes.get("data_source", "")

col_info_rows = []
for col_name in df.columns:
    meaning = saved_meanings.get(col_name, "")
    # 만약 저장된 뜻이 없고 자동 번역이 켜져 있다면 컬럼명을 번역해서 제안
    if not meaning and enable_translation:
        meaning = translate_text(col_name)

    col_info_rows.append({
        "열 이름": col_name,
        "우리말 뜻": meaning,
        "값의 종류": get_friendly_dtype(df[col_name]),
        "빈 값 개수": int(df[col_name].isna().sum())
    })

col_info_df = pd.DataFrame(col_info_rows)

edited_col_df = st.data_editor(
    col_info_df,
    use_container_width=True,
    hide_index=True,
    disabled=["열 이름", "값의 종류", "빈 값 개수"],
    column_config={
        "열 이름": st.column_config.TextColumn("열 이름", width="medium"),
        "우리말 뜻": st.column_config.TextColumn("우리말 뜻 (교재 참고 또는 자동 번역)", help="더블클릭하여 수정 가능합니다.", width="large"),
        "값의 종류": st.column_config.TextColumn("값의 종류", width="small"),
        "빈 값 개수": st.column_config.NumberColumn("빈 값 개수", format="%d개", width="small"),
    },
    key="column_info_editor",
)

updated_meanings = {
    row["열 이름"]: (row["우리말 뜻"] if pd.notna(row["우리말 뜻"]) else "")
    for _, row in edited_col_df.iterrows()
}

# ---------------------------------------------------------
# 데이터 미리보기 (번역 옵션 적용 가능)
# ---------------------------------------------------------
st.markdown('<div class="section-header">3. 원본 데이터 미리보기 (처음 5줄)</div>', unsafe_allow_html=True)

preview_df = df.head(5).copy()
if enable_translation:
    st.info("💡 자동 번역 옵션이 켜져 있어 미리보기의 텍스트 셀을 한국어로 번역하여 표시합니다.")
    # 문자열 타입 컬럼들에 대해 번역 적용 (성능을 위해 일부 셀만 간단히 처리하거나 전체 적용)
    for col in preview_df.select_dtypes(include=['object']).columns:
        preview_df[col] = preview_df[col].apply(lambda x: translate_text(str(x)) if pd.notna(x) else x)

st.dataframe(preview_df, use_container_width=True)

# ---------------------------------------------------------
# 데이터 출처 입력 및 자동 저장
# ---------------------------------------------------------
st.markdown('<div class="section-header">4. 데이터 출처 기록</div>', unsafe_allow_html=True)

updated_source = st.text_area(
    "데이터 출처",
    value=saved_source,
    placeholder="데이터 출처를 입력하세요.",
    height=90,
    key="data_source_input",
)

if updated_meanings != saved_meanings or updated_source != saved_source:
    save_notes(updated_meanings, updated_source)
    st.toast("입력한 내용이 '내_기록' 폴더의 JSON 파일에 자동 저장되었습니다.", icon="💾")

st.caption(f"📁 자동 저장 위치: `{RECORD_FILE}`")
