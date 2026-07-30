import io
import json
import re

import numpy as np
import pandas as pd
import plotly.express as px
import requests
import streamlit as st


# =========================================================
# 1. 페이지 기본 설정
# =========================================================
st.set_page_config(
    page_title="전국 시군구 고령화율 지도",
    page_icon="🗺️",
    layout="wide",
)

POPULATION_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/"
    "main/data/population_yearly.csv.gz"
)

GEOJSON_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/"
    "main/data/boundaries/sigungu_kr.geojson"
)

# 청소년기본법에서 사용하는 청소년 연령 범위
YOUTH_AGES = range(9, 25)  # 9세 이상 24세 이하

# 청년기본법에서 사용하는 청년 연령 범위
YOUNG_ADULT_AGES = range(19, 35)  # 19세 이상 34세 이하

# 단계구분도의 고령화율 구간
AGEING_BINS = [-np.inf, 19, 23, 28, 38, np.inf]

AGEING_LABELS = [
    "19% 미만",
    "19% 이상 23% 미만",
    "23% 이상 28% 미만",
    "28% 이상 38% 미만",
    "38% 이상",
]

# 낮은 비율은 옅게, 높은 비율은 진하게 표시합니다.
AGEING_COLORS = {
    "19% 미만": "#fff3e6",
    "19% 이상 23% 미만": "#fbd3ad",
    "23% 이상 28% 미만": "#f5a175",
    "28% 이상 38% 미만": "#d95f53",
    "38% 이상": "#8e2137",
}


# =========================================================
# 2. 간단한 화면 디자인
# =========================================================
st.markdown(
    """
    <style>
    .stApp {
        background: #f6f8fb;
        color: #202938;
    }

    .block-container {
        max-width: 1500px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    .hero {
        padding: 1.5rem 1.7rem;
        margin-bottom: 1.2rem;
        border: 1px solid #dce3ed;
        border-radius: 20px;
        background: #ffffff;
        box-shadow: 0 8px 24px rgba(32, 41, 56, 0.07);
    }

    .hero h1 {
        margin: 0;
        color: #283b57;
        font-size: 2.15rem;
    }

    .hero p {
        margin: 0.7rem 0 0;
        color: #58677c;
        line-height: 1.7;
    }

    .notice {
        padding: 0.9rem 1.1rem;
        margin: 0.7rem 0 1rem;
        border-left: 5px solid #5479a7;
        border-radius: 10px;
        background: #edf3fa;
        color: #26364d;
        line-height: 1.65;
    }

    [data-testid="stMetric"] {
        padding: 1rem;
        border: 1px solid #dce3ed;
        border-radius: 15px;
        background: #ffffff;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #dce3ed;
        border-radius: 14px;
        overflow: hidden;
        background: #ffffff;
    }

    h2, h3 {
        color: #2d405b;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 3. 인터넷에서 데이터 불러오기
# =========================================================
def download_bytes(url: str) -> bytes:
    """인터넷 주소에서 파일을 내려받아 바이트 형태로 돌려줍니다."""
    response = requests.get(
        url,
        timeout=90,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    response.raise_for_status()
    return response.content


@st.cache_data(show_spinner=False, ttl=60 * 60 * 6)
def load_population() -> pd.DataFrame:
    """
    압축된 인구 CSV를 읽습니다.

    '코드'는 계산용 숫자가 아니라 행정구역을 구분하는 이름표이므로
    반드시 문자열로 읽습니다.
    """
    content = download_bytes(POPULATION_URL)

    return pd.read_csv(
        io.BytesIO(content),
        compression="gzip",
        dtype={"코드": "string"},
        low_memory=False,
    )


@st.cache_data(show_spinner=False, ttl=60 * 60 * 24)
def load_geojson() -> dict:
    """전국 시군구 경계 GeoJSON을 읽습니다."""
    content = download_bytes(GEOJSON_URL)
    return json.loads(content.decode("utf-8-sig"))


# =========================================================
# 4. 데이터 정리용 함수
# =========================================================
def normalize_code(value: object, length: int) -> str | None:
    """
    행정구역 코드를 지정한 길이의 문자열로 정리합니다.

    엑셀이나 CSV 처리 과정에서 코드가 '1234567890.0'처럼 보이는 경우를
    대비해 끝의 '.0'을 제거하고 숫자 문자만 남깁니다.
    """
    if pd.isna(value):
        return None

    text = str(value).strip()
    text = re.sub(r"\.0$", "", text)
    digits = re.sub(r"[^0-9]", "", text)

    if not digits:
        return None

    # 코드가 짧아졌다면 앞에 0을 붙여 길이를 맞춥니다.
    return digits.zfill(length)[:length]


def to_number(series: pd.Series) -> pd.Series:
    """
    쉼표가 들어간 인구 값도 계산할 수 있도록 숫자로 변환합니다.
    변환할 수 없는 값과 빈칸은 0으로 처리합니다.
    """
    return pd.to_numeric(
        series.astype("string").str.replace(",", "", regex=False),
        errors="coerce",
    ).fillna(0)


def find_total_age_columns(columns: list[str]) -> list[str]:
    """
    '계_0세', '계_1세', ..., '계_100세 이상' 열만 찾습니다.

    '남_'과 '여_' 열까지 더하면 같은 인구를 중복 계산하게 되므로
    남녀 합계인 '계_' 열만 사용합니다.
    """
    pattern = re.compile(r"^계_(\d+)세(?: 이상)?$")
    age_columns = []

    for column in columns:
        match = pattern.match(str(column))

        if match:
            age = int(match.group(1))
            age_columns.append((age, str(column)))

    age_columns.sort(key=lambda item: item[0])
    return [column for _, column in age_columns]


def columns_for_ages(
    all_columns: list[str],
    ages: range,
) -> list[str]:
    """원하는 연령 범위의 '계_' 열 이름만 모읍니다."""
    column_set = set(all_columns)
    result = []

    for age in ages:
        column = f"계_{age}세"
        if column in column_set:
            result.append(column)

    return result


# =========================================================
# 5. 읍·면·동 자료를 시군구 단위로 합산
# =========================================================
def prepare_data(
    population: pd.DataFrame,
    geojson: dict,
) -> tuple[pd.DataFrame, dict, int, list[str]]:
    """
    가장 최신 연도의 읍·면·동 인구를 시군구별로 합산하고
    고령화율, 청소년비율, 청년비율을 계산합니다.
    """
    required = {"연도", "시도", "시군구", "동", "코드"}
    missing = required.difference(population.columns)

    if missing:
        raise ValueError(
            "인구 파일에 필요한 열이 없습니다: "
            + ", ".join(sorted(missing))
        )

    data = population.copy()

    # 연도를 숫자로 바꾼 뒤 파일에 실제로 들어 있는 가장 최신 연도를 찾습니다.
    data["연도_숫자"] = pd.to_numeric(data["연도"], errors="coerce")

    if data["연도_숫자"].notna().sum() == 0:
        raise ValueError("연도 열에서 사용할 수 있는 숫자 연도를 찾지 못했습니다.")

    latest_year = int(data["연도_숫자"].max())
    data = data.loc[data["연도_숫자"] == latest_year].copy()

    # 10자리 행정동 코드를 문자열로 정리하고 앞 5자리를 시군구 코드로 씁니다.
    data["행정동코드"] = data["코드"].map(
        lambda value: normalize_code(value, 10)
    )
    data["시군구코드"] = data["행정동코드"].str[:5]

    all_age_columns = find_total_age_columns(list(data.columns))

    if not all_age_columns:
        raise ValueError(
            "'계_0세' 형식의 연령별 남녀 합계 열을 찾지 못했습니다."
        )

    youth_columns = columns_for_ages(
        all_age_columns,
        YOUTH_AGES,
    )

    young_adult_columns = columns_for_ages(
        all_age_columns,
        YOUNG_ADULT_AGES,
    )

    # 65세부터 99세까지 찾은 뒤 100세 이상 열을 더합니다.
    elderly_columns = columns_for_ages(
        all_age_columns,
        range(65, 100),
    )

    if "계_100세 이상" in data.columns:
        elderly_columns.append("계_100세 이상")

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

    # 계산에 사용할 모든 인구 열을 숫자로 변환합니다.
    calculation_columns = sorted(
        set(
            all_age_columns
            + youth_columns
            + young_adult_columns
            + elderly_columns
        )
    )

    for column in calculation_columns:
        data[column] = to_number(data[column])

    # 읍·면·동별 인구를 먼저 계산합니다.
    data["총인구"] = data[all_age_columns].sum(axis=1)
    data["청소년인구"] = data[youth_columns].sum(axis=1)
    data["청년인구"] = data[young_adult_columns].sum(axis=1)
    data["고령인구"] = data[elderly_columns].sum(axis=1)

    # 같은 앞 5자리 코드를 가진 읍·면·동을 시군구별로 합산합니다.
    sigungu_population = (
        data.dropna(subset=["시군구코드"])
        .groupby("시군구코드", as_index=False)[
            ["총인구", "청소년인구", "청년인구", "고령인구"]
        ]
        .sum()
    )

    # 원본 GeoJSON을 직접 바꾸지 않도록 깊은 복사를 만듭니다.
    normalized_geojson = json.loads(json.dumps(geojson, ensure_ascii=False))

    boundary_rows = []

    for feature in normalized_geojson.get("features", []):
        properties = feature.setdefault("properties", {})
        code = normalize_code(properties.get("코드"), 5)

        # Plotly가 문자열 코드로 정확히 연결할 수 있도록
        # GeoJSON 속성의 코드도 5자리 문자열로 바꿉니다.
        properties["코드"] = code
        feature["id"] = code

        boundary_rows.append(
            {
                "시군구코드": code,
                "시도": properties.get("시도", ""),
                "시군구": properties.get("시군구", ""),
            }
        )

    boundary = (
        pd.DataFrame(boundary_rows)
        .dropna(subset=["시군구코드"])
        .drop_duplicates(subset=["시군구코드"])
    )

    # 이름이 아니라 5자리 코드로만 인구와 경계를 연결합니다.
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

    # 총인구가 0이면 0으로 나누지 않도록 NaN으로 바꿉니다.
    valid_total = result["총인구"].replace(0, np.nan)

    result["고령화율"] = result["고령인구"] / valid_total * 100
    result["청소년비율"] = result["청소년인구"] / valid_total * 100
    result["청년비율"] = result["청년인구"] / valid_total * 100

    # 요청한 경계값으로 고령화율을 5단계로 나눕니다.
    result["고령화 단계"] = pd.cut(
        result["고령화율"],
        bins=AGEING_BINS,
        labels=AGEING_LABELS,
        right=False,
        ordered=True,
    )

    return result, normalized_geojson, latest_year, warnings


# =========================================================
# 6. 단계구분도 만들기
# =========================================================
def create_map(data: pd.DataFrame, geojson: dict):
    """배경 지도 타일 없이 시군구 경계만 표시하는 단계구분도를 만듭니다."""
    map_data = data.dropna(
        subset=["고령화 단계", "고령화율"]
    ).copy()

    fig = px.choropleth(
        map_data,
        geojson=geojson,
        locations="시군구코드",
        featureidkey="properties.코드",
        color="고령화 단계",
        color_discrete_map=AGEING_COLORS,
        category_orders={"고령화 단계": AGEING_LABELS},
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
        marker_line_color="#6e747d",
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

    # 배경 지도 타일 없이 GeoJSON 경계 도형만 표시합니다.
    fig.update_geos(
        fitbounds="locations",
        visible=False,
        projection_type="mercator",
    )

    fig.update_layout(
        height=840,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="#f6f8fb",
        plot_bgcolor="#f6f8fb",
        legend=dict(
            title="65세 이상 인구 비율",
            orientation="v",
            x=0.01,
            y=0.99,
            xanchor="left",
            yanchor="top",
            bgcolor="rgba(255,255,255,0.94)",
            bordercolor="#cfd8e5",
            borderwidth=1,
            font=dict(size=12, color="#202938"),
            title_font=dict(size=13, color="#202938"),
            traceorder="normal",
        ),
    )

    return fig


# =========================================================
# 7. 표 만들기
# =========================================================
def make_rank_table(
    data: pd.DataFrame,
    ascending: bool,
) -> pd.DataFrame:
    """고령화율 상위 또는 하위 10개 표를 만듭니다."""
    table = (
        data.loc[
            data["총인구"] > 0,
            [
                "시도",
                "시군구",
                "고령화율",
                "청소년비율",
                "청년비율",
                "총인구",
            ],
        ]
        .dropna(subset=["고령화율"])
        .sort_values(
            ["고령화율", "시도", "시군구"],
            ascending=[ascending, True, True],
        )
        .head(10)
        .reset_index(drop=True)
    )

    table.index = table.index + 1
    return table




# =========================================================
# 8. 청소년 인구 변화 자료와 그래프 만들기
# =========================================================
@st.cache_data(show_spinner=False)
def prepare_youth_trend(population: pd.DataFrame) -> pd.DataFrame:
    """
    모든 연도의 읍·면·동 자료를 시군구 단위로 합산해
    청소년 인구 변화 그래프에 사용할 자료를 만듭니다.
    """
    data = population.copy()

    data["연도"] = pd.to_numeric(data["연도"], errors="coerce")
    data = data.dropna(subset=["연도"]).copy()
    data["연도"] = data["연도"].astype(int)

    # 행정동 코드 앞 5자리를 시군구 코드로 사용합니다.
    data["행정동코드"] = data["코드"].map(
        lambda value: normalize_code(value, 10)
    )
    data["시군구코드"] = data["행정동코드"].str[:5]

    all_age_columns = find_total_age_columns(list(data.columns))
    youth_columns = columns_for_ages(all_age_columns, YOUTH_AGES)

    if not all_age_columns:
        raise ValueError(
            "청소년 변화 그래프를 만들 연령별 인구 열을 찾지 못했습니다."
        )

    if not youth_columns:
        raise ValueError(
            "청소년 변화 그래프를 만들 9~24세 인구 열을 찾지 못했습니다."
        )

    # 필요한 연령별 열만 숫자로 변환합니다.
    for column in sorted(set(all_age_columns + youth_columns)):
        data[column] = to_number(data[column])

    data["총인구"] = data[all_age_columns].sum(axis=1)
    data["청소년인구"] = data[youth_columns].sum(axis=1)

    # 같은 시군구에 속한 읍·면·동을 연도별로 합산합니다.
    trend = (
        data.dropna(subset=["시군구코드"])
        .groupby(
            ["연도", "시군구코드", "시도", "시군구"],
            as_index=False,
        )[["총인구", "청소년인구"]]
        .sum()
    )

    valid_total = trend["총인구"].replace(0, np.nan)
    trend["청소년비율"] = trend["청소년인구"] / valid_total * 100

    return trend


def select_youth_trend(
    trend: pd.DataFrame,
    level: str,
    selected_sido: str | None = None,
    selected_code: str | None = None,
) -> tuple[pd.DataFrame, str]:
    """선택한 지역 수준에 맞는 연도별 청소년 인구 자료를 반환합니다."""
    if level == "전국":
        selected = (
            trend.groupby("연도", as_index=False)[["총인구", "청소년인구"]]
            .sum()
            .sort_values("연도")
        )
        title = "전국"

    elif level == "시도":
        selected = (
            trend.loc[trend["시도"] == selected_sido]
            .groupby("연도", as_index=False)[["총인구", "청소년인구"]]
            .sum()
            .sort_values("연도")
        )
        title = str(selected_sido)

    else:
        selected = (
            trend.loc[trend["시군구코드"] == selected_code]
            .groupby("연도", as_index=False)[["총인구", "청소년인구"]]
            .sum()
            .sort_values("연도")
        )

        name_rows = trend.loc[
            trend["시군구코드"] == selected_code,
            ["시도", "시군구"],
        ].drop_duplicates()

        if name_rows.empty:
            title = str(selected_code)
        else:
            title = (
                f"{name_rows.iloc[0]['시도']} "
                f"{name_rows.iloc[0]['시군구']}"
            )

    valid_total = selected["총인구"].replace(0, np.nan)
    selected["청소년비율"] = (
        selected["청소년인구"] / valid_total * 100
    )

    return selected, title


def create_youth_population_chart(
    data: pd.DataFrame,
    region_title: str,
):
    """연도별 청소년 인구수를 보여 주는 꺾은선 그래프입니다."""
    fig = px.line(
        data,
        x="연도",
        y="청소년인구",
        markers=True,
        title=f"{region_title} 청소년 인구 변화",
    )

    fig.update_traces(
        line_width=3,
        marker_size=8,
        hovertemplate=(
            "<b>%{x}년</b><br>"
            "청소년 인구: %{y:,.0f}명"
            "<extra></extra>"
        ),
    )

    fig.update_layout(
        height=430,
        xaxis_title="연도",
        yaxis_title="청소년 인구(명)",
        hovermode="x unified",
        margin=dict(l=20, r=20, t=65, b=20),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
    )

    fig.update_xaxes(dtick=1, showgrid=False)
    fig.update_yaxes(tickformat=",", gridcolor="#e8edf3")

    return fig


def create_youth_rate_chart(
    data: pd.DataFrame,
    region_title: str,
):
    """연도별 전체 인구 대비 청소년 비율을 보여 주는 그래프입니다."""
    fig = px.line(
        data,
        x="연도",
        y="청소년비율",
        markers=True,
        title=f"{region_title} 청소년 인구 비율 변화",
    )

    fig.update_traces(
        line_width=3,
        marker_size=8,
        hovertemplate=(
            "<b>%{x}년</b><br>"
            "청소년 비율: %{y:.1f}%"
            "<extra></extra>"
        ),
    )

    fig.update_layout(
        height=430,
        xaxis_title="연도",
        yaxis_title="청소년 비율(%)",
        hovermode="x unified",
        margin=dict(l=20, r=20, t=65, b=20),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
    )

    fig.update_xaxes(dtick=1, showgrid=False)
    fig.update_yaxes(ticksuffix="%", gridcolor="#e8edf3")

    return fig


# =========================================================
# 9. 화면 출력
# =========================================================
st.markdown(
    """
    <div class="hero">
        <h1>🗺️ 전국 시군구 고령화율 지도</h1>
        <p>
            전국 읍·면·동 인구를 행정동 코드 앞 5자리로 합산하고,
            시군구별 65세 이상 인구 비율을 다섯 단계 색으로 표시합니다.
            지역에 마우스를 올리면 청소년과 청년 인구 비율도 확인할 수 있습니다.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    with st.spinner("최신 인구 자료와 시군구 경계를 불러오는 중입니다..."):
        population_df = load_population()
        raw_geojson = load_geojson()

        (
            sigungu_df,
            normalized_geojson,
            latest_year,
            data_warnings,
        ) = prepare_data(
            population_df,
            raw_geojson,
        )

        youth_trend_df = prepare_youth_trend(population_df)

    valid_df = sigungu_df.loc[sigungu_df["총인구"] > 0].copy()

    national_total = valid_df["총인구"].sum()
    national_elderly = valid_df["고령인구"].sum()

    national_ageing_rate = (
        national_elderly / national_total * 100
        if national_total > 0
        else np.nan
    )

    metric1, metric2, metric3, metric4 = st.columns(4)

    metric1.metric("사용 연도", f"{latest_year}년")
    metric2.metric("경계 시군구", f"{len(sigungu_df):,}개")
    metric3.metric("인구 연결 지역", f"{len(valid_df):,}개")
    metric4.metric("전국 고령화율", f"{national_ageing_rate:.1f}%")

    st.markdown(
        f"""
        <div class="notice">
            <b>계산 기준</b><br>
            고령화율 = 65세 이상 인구 ÷ 총인구 × 100 ·
            청소년 = 9~24세 · 청년 = 19~34세 ·
            기준 연도 = {latest_year}년
        </div>
        """,
        unsafe_allow_html=True,
    )

    for warning_message in data_warnings:
        st.warning(warning_message)

    unmatched_count = int((sigungu_df["총인구"] <= 0).sum())

    if unmatched_count:
        st.warning(
            f"경계 자료 중 인구 자료와 연결되지 않은 지역이 "
            f"{unmatched_count}개 있습니다. 이 지역은 지도에서 색이 표시되지 않습니다."
        )

    st.plotly_chart(
        create_map(sigungu_df, normalized_geojson),
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

    # -----------------------------------------------------
    # 청소년 인구 변화 그래프
    # -----------------------------------------------------
    st.markdown("## 📈 청소년 인구 변화")

    st.markdown(
        """
        <div class="notice">
            전국·시도·시군구 중 원하는 지역을 선택하면
            2015년부터 최신 연도까지의 청소년 인구수와
            전체 인구 대비 청소년 비율 변화를 확인할 수 있습니다.
        </div>
        """,
        unsafe_allow_html=True,
    )

    selector1, selector2, selector3 = st.columns([1, 1.2, 1.8])

    with selector1:
        trend_level = st.selectbox(
            "지역 범위",
            ["전국", "시도", "시군구"],
            key="청소년_지역범위",
        )

    selected_sido = None
    selected_sigungu_code = None

    sido_options = sorted(
        youth_trend_df["시도"].dropna().astype(str).unique().tolist()
    )

    with selector2:
        if trend_level in ["시도", "시군구"]:
            selected_sido = st.selectbox(
                "시도 선택",
                sido_options,
                key="청소년_시도",
            )
        else:
            st.markdown("**시도 선택**")
            st.caption("전국을 선택했습니다.")

    with selector3:
        if trend_level == "시군구":
            sigungu_options_df = (
                youth_trend_df.loc[
                    youth_trend_df["시도"] == selected_sido,
                    ["시군구코드", "시군구"],
                ]
                .drop_duplicates()
                .sort_values(["시군구", "시군구코드"])
            )

            sigungu_label_to_code = {
                f"{row['시군구']} ({row['시군구코드']})": row["시군구코드"]
                for _, row in sigungu_options_df.iterrows()
            }

            selected_sigungu_label = st.selectbox(
                "시군구 선택",
                list(sigungu_label_to_code.keys()),
                key="청소년_시군구",
            )

            selected_sigungu_code = sigungu_label_to_code[
                selected_sigungu_label
            ]
        else:
            st.markdown("**시군구 선택**")
            st.caption("시군구 선택이 필요하지 않습니다.")

    selected_trend, selected_region_title = select_youth_trend(
        youth_trend_df,
        level=trend_level,
        selected_sido=selected_sido,
        selected_code=selected_sigungu_code,
    )

    if selected_trend.empty:
        st.warning("선택한 지역의 연도별 청소년 인구 자료가 없습니다.")
    else:
        first_row = selected_trend.iloc[0]
        last_row = selected_trend.iloc[-1]

        population_change = (
            last_row["청소년인구"] - first_row["청소년인구"]
        )

        if first_row["청소년인구"] > 0:
            population_change_rate = (
                population_change / first_row["청소년인구"] * 100
            )
        else:
            population_change_rate = np.nan

        trend_metric1, trend_metric2, trend_metric3 = st.columns(3)

        trend_metric1.metric(
            f"{int(last_row['연도'])}년 청소년 인구",
            f"{last_row['청소년인구']:,.0f}명",
        )

        trend_metric2.metric(
            f"{int(last_row['연도'])}년 청소년 비율",
            f"{last_row['청소년비율']:.1f}%",
        )

        trend_metric3.metric(
            f"{int(first_row['연도'])}년 대비 변화",
            f"{population_change:,.0f}명",
            (
                f"{population_change_rate:+.1f}%"
                if pd.notna(population_change_rate)
                else None
            ),
        )

        chart_left, chart_right = st.columns(2)

        with chart_left:
            st.plotly_chart(
                create_youth_population_chart(
                    selected_trend,
                    selected_region_title,
                ),
                use_container_width=True,
                config={"displaylogo": False},
            )

        with chart_right:
            st.plotly_chart(
                create_youth_rate_chart(
                    selected_trend,
                    selected_region_title,
                ),
                use_container_width=True,
                config={"displaylogo": False},
            )

        with st.expander("연도별 청소년 인구 자료 보기"):
            trend_table = selected_trend[
                ["연도", "총인구", "청소년인구", "청소년비율"]
            ].copy()

            st.dataframe(
                trend_table,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "연도": st.column_config.NumberColumn(
                        "연도",
                        format="%d년",
                    ),
                    "총인구": st.column_config.NumberColumn(
                        "총인구",
                        format="%d명",
                    ),
                    "청소년인구": st.column_config.NumberColumn(
                        "청소년 인구",
                        format="%d명",
                    ),
                    "청소년비율": st.column_config.NumberColumn(
                        "청소년 비율",
                        format="%.1f%%",
                    ),
                },
            )

    st.markdown("## 시군구 고령화율 상·하위 지역")

    highest = make_rank_table(sigungu_df, ascending=False)
    lowest = make_rank_table(sigungu_df, ascending=True)

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

    left, right = st.columns(2)

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
1. 인구 CSV에서 가장 최신 연도인 **{latest_year}년** 자료만 선택했습니다.
2. `코드`를 문자열로 읽고 행정동 코드의 **앞 5자리**를 시군구 코드로 사용했습니다.
3. 같은 시군구 코드를 가진 읍·면·동의 인구를 합산했습니다.
4. 남녀 합계인 `계_` 열만 사용해 중복 계산을 막았습니다.
5. 고령화율은 **65세 이상 인구 ÷ 총인구 × 100**으로 계산했습니다.
6. 인구 자료와 지도 경계는 지역 이름이 아니라 **5자리 코드**로 연결했습니다.
7. 고령화율은 19%, 23%, 28%, 38%를 경계로 다섯 단계로 구분했습니다.
8. 청소년 변화 그래프는 모든 연도의 9~24세 인구를 지역별로 다시 합산해 만들었습니다.
            """
        )

except requests.RequestException as error:
    st.error(
        "인터넷에서 데이터를 내려받지 못했습니다. "
        "네트워크 상태를 확인한 뒤 새로고침해 주세요."
    )
    st.exception(error)

except (
    ValueError,
    KeyError,
    TypeError,
    json.JSONDecodeError,
) as error:
    st.error(
        "데이터를 처리하는 중 문제가 발생했습니다. "
        "원본 CSV의 열 이름이나 GeoJSON 속성을 확인해 주세요."
    )
    st.exception(error)
