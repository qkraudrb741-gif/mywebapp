import io
import json
import re

import numpy as np
import pandas as pd
import plotly.express as px
import requests
import streamlit as st


# ---------------------------------------------------------
# 1. 기본 설정
# ---------------------------------------------------------
st.set_page_config(
    page_title="전국 시군구 고령화율 지도",
    page_icon="🗺️",
    layout="wide",
)

POPULATION_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/"
    "main/data/population_yearly.csv.gz"
)
BOUNDARY_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/"
    "main/data/boundaries/sigungu_kr.geojson"
)

# 청소년기본법: 9~24세
YOUTH_AGES = range(9, 25)

# 청년기본법: 19~34세
YOUNG_ADULT_AGES = range(19, 35)

# 고령인구: 65세 이상
ELDERLY_AGES = range(65, 100)


# ---------------------------------------------------------
# 2. 화면 디자인
# ---------------------------------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background: #f7f9fc;
        color: #20242c;
    }

    .block-container {
        max-width: 1500px;
        padding-top: 1.8rem;
        padding-bottom: 3rem;
    }

    .title-box {
        padding: 1.5rem 1.7rem;
        margin-bottom: 1.2rem;
        border: 1px solid #d9e1ec;
        border-radius: 20px;
        background: #ffffff;
        box-shadow: 0 8px 24px rgba(42, 56, 78, 0.07);
    }

    .title-box h1 {
        margin: 0;
        color: #23324a;
        font-size: 2.15rem;
    }

    .title-box p {
        margin: 0.65rem 0 0;
        color: #536176;
        line-height: 1.7;
    }

    .info-box {
        padding: 0.9rem 1.1rem;
        margin-bottom: 1rem;
        border-left: 5px solid #5479a8;
        border-radius: 10px;
        background: #edf3fa;
        color: #26364d;
    }

    [data-testid="stMetric"] {
        padding: 1rem;
        border: 1px solid #dce4ee;
        border-radius: 15px;
        background: #ffffff;
    }

    [data-testid="stMetricLabel"] {
        color: #536176;
    }

    [data-testid="stMetricValue"] {
        color: #23324a;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #dce4ee;
        border-radius: 14px;
        overflow: hidden;
        background: #ffffff;
    }

    h2, h3 {
        color: #2b3d56;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# 3. 데이터 다운로드 함수
# ---------------------------------------------------------
def request_file(url: str) -> bytes:
    """인터넷 주소에서 파일을 내려받습니다."""
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    return response.content


@st.cache_data(show_spinner=False, ttl=60 * 60 * 6)
def load_population() -> pd.DataFrame:
    """
    압축된 인구 CSV를 읽습니다.

    '코드'는 계산할 숫자가 아니라 행정동을 구분하는 이름표이므로
    반드시 문자열로 읽습니다.
    """
    content = request_file(POPULATION_URL)

    return pd.read_csv(
        io.BytesIO(content),
        compression="gzip",
        dtype={"코드": "string"},
        low_memory=False,
    )


@st.cache_data(show_spinner=False, ttl=60 * 60 * 24)
def load_geojson() -> dict:
    """전국 시군구 경계 GeoJSON을 읽습니다."""
    content = request_file(BOUNDARY_URL)
    return json.loads(content.decode("utf-8"))


# ---------------------------------------------------------
# 4. 코드와 숫자 정리 함수
# ---------------------------------------------------------
def clean_admin_code(value: object, length: int) -> str | None:
    """
    행정구역 코드를 숫자로 계산하지 않고 문자열로 정리합니다.

    CSV 프로그램에서 코드가 1234567890.0처럼 보이는 경우를 대비해
    끝의 '.0'을 제거한 뒤 필요한 길이만 남깁니다.
    """
    if pd.isna(value):
        return None

    text = str(value).strip()
    text = re.sub(r"\\.0$", "", text)
    digits = re.sub(r"[^0-9]", "", text)

    if not digits:
        return None

    digits = digits.zfill(length)
    return digits[:length]


def to_number(series: pd.Series) -> pd.Series:
    """
    쉼표가 포함된 인구 값도 계산할 수 있도록 숫자로 바꿉니다.
    빈칸이나 잘못된 값은 0으로 처리합니다.
    """
    return pd.to_numeric(
        series.astype("string").str.replace(",", "", regex=False),
        errors="coerce",
    ).fillna(0)


def find_age_column(columns: list[str], age: int) -> str | None:
    """특정 나이의 남녀 합계 열 이름을 찾습니다."""
    expected = f"계_{age}세"
    return expected if expected in columns else None


def make_age_columns(columns: list[str], ages: range) -> list[str]:
    """주어진 나이 범위에 해당하는 '계_' 열만 모읍니다."""
    result = []

    for age in ages:
        column = find_age_column(columns, age)
        if column is not None:
            result.append(column)

    return result


def find_total_age_columns(columns: list[str]) -> list[str]:
    """
    '계_0세'부터 '계_100세 이상'까지 남녀 합계 열만 찾습니다.
    '남_'과 '여_' 열은 중복 계산을 막기 위해 제외합니다.
    """
    pattern = re.compile(r"^계_(\\d+)세(?: 이상)?$")
    age_columns = []

    for column in columns:
        match = pattern.match(str(column))

        if match:
            age = int(match.group(1))
            age_columns.append((age, column))

    age_columns.sort(key=lambda item: item[0])
    return [column for _, column in age_columns]


# ---------------------------------------------------------
# 5. 최신 연도 시군구 자료 만들기
# ---------------------------------------------------------
def prepare_sigungu_data(
    population: pd.DataFrame,
    geojson: dict,
) -> tuple[pd.DataFrame, int, list[str]]:
    """
    읍·면·동 자료를 시군구 단위로 합산하고
    고령화율, 청소년비율, 청년비율을 계산합니다.
    """
    required_columns = {"연도", "시도", "시군구", "코드"}
    missing_columns = required_columns.difference(population.columns)

    if missing_columns:
        missing_text = ", ".join(sorted(missing_columns))
        raise ValueError(f"인구 파일에 필요한 열이 없습니다: {missing_text}")

    data = population.copy()

    # 연도 열을 숫자로 바꾸고 파일 안의 가장 최신 연도를 찾습니다.
    data["연도_숫자"] = pd.to_numeric(data["연도"], errors="coerce")

    if data["연도_숫자"].notna().sum() == 0:
        raise ValueError("'연도' 열에서 숫자 연도를 찾지 못했습니다.")

    latest_year = int(data["연도_숫자"].max())
    data = data.loc[data["연도_숫자"] == latest_year].copy()

    # 10자리 행정동 코드의 앞 5자리를 시군구 코드로 사용합니다.
    data["행정동코드"] = data["코드"].map(
        lambda value: clean_admin_code(value, 10)
    )
    data["시군구코드"] = data["행정동코드"].str[:5]

    total_columns = find_total_age_columns(list(data.columns))
    youth_columns = make_age_columns(list(data.columns), YOUTH_AGES)
    young_adult_columns = make_age_columns(
        list(data.columns),
        YOUNG_ADULT_AGES,
    )
    elderly_columns = make_age_columns(list(data.columns), ELDERLY_AGES)

    # 100세 이상 열은 65세 이상 인구에 포함합니다.
    if "계_100세 이상" in data.columns:
        elderly_columns.append("계_100세 이상")

    if not total_columns:
        raise ValueError("'계_0세' 형식의 나이별 합계 열을 찾지 못했습니다.")

    warnings = []

    if len(youth_columns) != 16:
        warnings.append(
            f"청소년 연령 열을 16개 중 {len(youth_columns)}개만 찾았습니다."
        )

    if len(young_adult_columns) != 16:
        warnings.append(
            f"청년 연령 열을 16개 중 {len(young_adult_columns)}개만 찾았습니다."
        )

    if len(elderly_columns) != 36:
        warnings.append(
            f"65세 이상 연령 열을 36개 중 {len(elderly_columns)}개만 찾았습니다."
        )

    # 필요한 인구 열을 숫자로 변환합니다.
    calculation_columns = sorted(
        set(
            total_columns
            + youth_columns
            + young_adult_columns
            + elderly_columns
        )
    )

    for column in calculation_columns:
        data[column] = to_number(data[column])

    data["총인구"] = data[total_columns].sum(axis=1)
    data["청소년인구"] = data[youth_columns].sum(axis=1)
    data["청년인구"] = data[young_adult_columns].sum(axis=1)
    data["고령인구"] = data[elderly_columns].sum(axis=1)

    # 읍·면·동 행을 같은 앞 5자리 코드끼리 묶어 시군구 단위로 합칩니다.
    sigungu_population = (
        data.dropna(subset=["시군구코드"])
        .groupby("시군구코드", as_index=False)[
            ["총인구", "청소년인구", "청년인구", "고령인구"]
        ]
        .sum()
    )

    # GeoJSON을 기준으로 표를 만들면 경계 데이터의 시도·시군구 이름을
    # 그대로 사용할 수 있고, 동명이인 지역 문제도 코드로 안전하게 피할 수 있습니다.
    boundary_rows = []

    for feature in geojson.get("features", []):
        properties = feature.get("properties", {})
        code = clean_admin_code(properties.get("코드"), 5)

        boundary_rows.append(
            {
                "시군구코드": code,
                "시도": properties.get("시도", ""),
                "시군구": properties.get("시군구", ""),
            }
        )

        # Plotly가 feature의 고유 ID로도 코드를 사용할 수 있게 지정합니다.
        feature["id"] = code

    boundary = pd.DataFrame(boundary_rows).drop_duplicates(
        subset=["시군구코드"]
    )

    result = boundary.merge(
        sigungu_population,
        on="시군구코드",
        how="left",
        validate="one_to_one",
    )

    population_columns = [
        "총인구",
        "청소년인구",
        "청년인구",
        "고령인구",
    ]
    result[population_columns] = result[population_columns].fillna(0)

    # 총인구가 0이면 0으로 나누지 않도록 결측값으로 둡니다.
    valid_total = result["총인구"].replace(0, np.nan)

    result["고령화율"] = result["고령인구"] / valid_total * 100
    result["청소년비율"] = result["청소년인구"] / valid_total * 100
    result["청년비율"] = result["청년인구"] / valid_total * 100

    # 요청한 실제 구간 경계값으로 5단계를 만듭니다.
    bins = [-np.inf, 19, 23, 28, 38, np.inf]
    labels = [
        "19% 미만",
        "19% 이상 23% 미만",
        "23% 이상 28% 미만",
        "28% 이상 38% 미만",
        "38% 이상",
    ]

    result["고령화 단계"] = pd.cut(
        result["고령화율"],
        bins=bins,
        labels=labels,
        right=False,
    )

    return result, latest_year, warnings


# ---------------------------------------------------------
# 6. 지도 만들기
# ---------------------------------------------------------
def make_map(data: pd.DataFrame, geojson: dict):
    """5단계 색으로 구분한 전국 시군구 단계구분도를 만듭니다."""
    category_order = [
        "19% 미만",
        "19% 이상 23% 미만",
        "23% 이상 28% 미만",
        "28% 이상 38% 미만",
        "38% 이상",
    ]

    # 낮은 비율은 옅게, 높은 비율은 진하게 보이는 5단계 색입니다.
    color_map = {
        "19% 미만": "#fff3e8",
        "19% 이상 23% 미만": "#fbcfa9",
        "23% 이상 28% 미만": "#f49a73",
        "28% 이상 38% 미만": "#d85c50",
        "38% 이상": "#8f2035",
    }

    map_data = data.dropna(
        subset=["고령화 단계", "고령화율"]
    ).copy()

    fig = px.choropleth(
        map_data,
        geojson=geojson,
        locations="시군구코드",
        featureidkey="properties.코드",
        color="고령화 단계",
        color_discrete_map=color_map,
        category_orders={"고령화 단계": category_order},
        custom_data=[
            "시군구",
            "시도",
            "고령화율",
            "청소년비율",
            "청년비율",
            "총인구",
        ],
    )

    fig.update_traces(
        marker_line_color="#6f747c",
        marker_line_width=0.45,
        hovertemplate=(
            "<b>%{customdata[1]} %{customdata[0]}</b><br>"
            "고령화율: %{customdata[2]:.1f}%<br>"
            "청소년비율(9~24세): %{customdata[3]:.1f}%<br>"
            "청년비율(19~34세): %{customdata[4]:.1f}%<br>"
            "총인구: %{customdata[5]:,.0f}명"
            "<extra></extra>"
        ),
    )

    # 배경 지도 타일은 사용하지 않고 시군구 경계 도형만 표시합니다.
    fig.update_geos(
        fitbounds="locations",
        visible=False,
        projection_type="mercator",
    )

    fig.update_layout(
        height=820,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="#f7f9fc",
        plot_bgcolor="#f7f9fc",
        legend=dict(
            title="65세 이상 인구 비율",
            orientation="v",
            x=0.01,
            y=0.98,
            xanchor="left",
            yanchor="top",
            bgcolor="rgba(255,255,255,0.92)",
            bordercolor="#cfd8e5",
            borderwidth=1,
            font=dict(size=12, color="#20242c"),
            title_font=dict(size=13, color="#20242c"),
            traceorder="normal",
        ),
    )

    return fig


# ---------------------------------------------------------
# 7. 화면 출력
# ---------------------------------------------------------
st.markdown(
    """
    <div class="title-box">
        <h1>🗺️ 전국 시군구 고령화율 지도</h1>
        <p>
            전국 읍·면·동 인구를 시군구 코드 앞 5자리로 합산한 뒤,
            65세 이상 인구 비율을 다섯 단계 색으로 표시합니다.
            지역에 마우스를 올리면 청소년과 청년 인구 비율도 확인할 수 있습니다.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    with st.spinner("최신 인구 자료와 지도 경계를 불러오는 중입니다..."):
        population_df = load_population()
        boundary_geojson = load_geojson()
        sigungu_df, latest_year, data_warnings = prepare_sigungu_data(
            population_df,
            boundary_geojson,
        )

    valid_df = sigungu_df.loc[
        sigungu_df["총인구"] > 0
    ].copy()

    national_total = valid_df["총인구"].sum()
    national_elderly = valid_df["고령인구"].sum()
    national_rate = (
        national_elderly / national_total * 100
        if national_total > 0
        else np.nan
    )

    metric1, metric2, metric3, metric4 = st.columns(4)

    metric1.metric("사용 연도", f"{latest_year}년")
    metric2.metric("지도 시군구", f"{len(sigungu_df):,}개")
    metric3.metric("인구 자료 연결", f"{len(valid_df):,}개")
    metric4.metric("전국 고령화율", f"{national_rate:.1f}%")

    st.markdown(
        f"""
        <div class="info-box">
            <b>계산 기준</b> · 고령화율: 65세 이상 / 총인구 ·
            청소년: 9~24세 · 청년: 19~34세 ·
            기준 연도: {latest_year}년
        </div>
        """,
        unsafe_allow_html=True,
    )

    for warning in data_warnings:
        st.warning(warning)

    missing_count = int((sigungu_df["총인구"] <= 0).sum())

    if missing_count:
        st.warning(
            f"경계 자료 중 인구 자료와 연결되지 않은 지역이 "
            f"{missing_count}개 있어 지도 색상에서 제외되었습니다."
        )

    st.plotly_chart(
        make_map(sigungu_df, boundary_geojson),
        use_container_width=True,
        config={
            "displaylogo": False,
            "scrollZoom": True,
            "modeBarButtonsToRemove": [
                "lasso2d",
                "select2d",
            ],
        },
    )

    st.markdown("## 시군구 고령화율 상·하위 지역")

    table_data = (
        valid_df[
            [
                "시도",
                "시군구",
                "고령화율",
                "청소년비율",
                "청년비율",
                "총인구",
            ]
        ]
        .dropna(subset=["고령화율"])
        .copy()
    )

    highest = (
        table_data.sort_values(
            ["고령화율", "시도", "시군구"],
            ascending=[False, True, True],
        )
        .head(10)
        .reset_index(drop=True)
    )

    lowest = (
        table_data.sort_values(
            ["고령화율", "시도", "시군구"],
            ascending=[True, True, True],
        )
        .head(10)
        .reset_index(drop=True)
    )

    highest.index = highest.index + 1
    lowest.index = lowest.index + 1

    left, right = st.columns(2)

    column_config = {
        "시도": st.column_config.TextColumn("시도"),
        "시군구": st.column_config.TextColumn("시군구"),
        "고령화율": st.column_config.NumberColumn(
            "고령화율",
            format="%.1f%%",
        ),
        "청소년비율": st.column_config.NumberColumn(
            "청소년비율",
            format="%.1f%%",
        ),
        "청년비율": st.column_config.NumberColumn(
            "청년비율",
            format="%.1f%%",
        ),
        "총인구": st.column_config.NumberColumn(
            "총인구",
            format="%d명",
        ),
    }

    with left:
        st.subheader("🔴 고령화율 높은 곳 10개")
        st.dataframe(
            highest,
            use_container_width=True,
            hide_index=False,
            column_config=column_config,
        )

    with right:
        st.subheader("🟡 고령화율 낮은 곳 10개")
        st.dataframe(
            lowest,
            use_container_width=True,
            hide_index=False,
            column_config=column_config,
        )

    with st.expander("데이터 처리 방법 보기"):
        st.markdown(
            f"""
            1. 인구 CSV에서 **가장 최신 연도인 {latest_year}년** 자료만 선택했습니다.
            2. 행정동 코드 10자리를 문자열로 읽고 **앞 5자리**를 시군구 코드로 사용했습니다.
            3. 같은 시군구 코드를 가진 읍·면·동 인구를 모두 합산했습니다.
            4. `계_`로 시작하는 연령별 열만 사용해 남녀 인구의 중복 합산을 막았습니다.
            5. 고령화율은 **65세 이상 인구 ÷ 총인구 × 100**으로 계산했습니다.
            6. 지도 경계와 인구 자료는 지역 이름이 아니라 **5자리 코드**로 연결했습니다.
            """
        )

except requests.RequestException as error:
    st.error(
        "인터넷에서 데이터를 내려받지 못했습니다. "
        "잠시 후 새로고침해 주세요."
    )
    st.exception(error)

except (ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
    st.error(
        "데이터 구조를 확인하는 과정에서 문제가 발생했습니다. "
        "원본 파일의 열 이름이나 GeoJSON 속성을 확인해 주세요."
    )
    st.exception(error)
