import math
import pandas as pd
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="출입문 충격 에너지 압전 하베스팅 시뮬레이터",
    page_icon="⚡",
    layout="wide",
)

# 1. 보고서 실측 데이터 기반 완충재 프로파일 (기준: 100g 추, 30cm 낙하, 30회 반복)
CUSHION_PROFILES = {
    "미적용 (직접 충격)": {
        "thickness_mm": 0.0,
        "base_avg_v": 14.2,
        "base_max_v": 18.5,
        "impact_time_ms": 1.2,
        "damage_rate": 2.8,
        "recovery_rate": 1.00,
        "status_note": "납땜부 크랙 발생, 전선 이탈 위험 높음",
    },
    "아크릴판 (2.0mm)": {
        "thickness_mm": 2.0,
        "base_avg_v": 11.8,
        "base_max_v": 13.6,
        "impact_time_ms": 2.0,
        "damage_rate": 1.4,
        "recovery_rate": 0.98,
        "status_note": "표면 미세 스크래치, 완충 미흡",
    },
    "고무 패드 (3.0mm - 최적)": {
        "thickness_mm": 3.0,
        "base_avg_v": 8.4,
        "base_max_v": 9.8,
        "impact_time_ms": 4.2,
        "damage_rate": 0.15,
        "recovery_rate": 0.97,
        "status_note": "손상 없음 (소자 보호 및 실용 전압 확보)",
    },
    "EVA 폼 (3.0mm)": {
        "thickness_mm": 3.0,
        "base_avg_v": 5.2,
        "base_max_v": 6.1,
        "impact_time_ms": 6.8,
        "damage_rate": 0.08,
        "recovery_rate": 0.78,
        "status_note": "손상 없음, 복원 속도 느림",
    },
    "스펀지 (5.0mm)": {
        "thickness_mm": 5.0,
        "base_avg_v": 2.1,
        "base_max_v": 2.8,
        "impact_time_ms": 11.5,
        "damage_rate": 0.03,
        "recovery_rate": 0.85,
        "status_note": "손상 없음, 충격 과다 흡수로 출력 낮음",
    },
}

# 기준 실험 조건 상수 (보고서 2단계 기준)
BASE_MASS_G = 100.0
BASE_HEIGHT_CM = 30.0
G = 9.81
BASE_IMPACT_VELOCITY = math.sqrt(2 * G * (BASE_HEIGHT_CM / 100.0))
BASE_MOMENTUM = (BASE_MASS_G / 1000.0) * BASE_IMPACT_VELOCITY

# 타이틀 및 개요
st.title("⚡ 출입문 충격 에너지 기반 압전 전력 하베스팅 시뮬레이터")
st.caption("2026학년도 교과심화탐구 프로젝트 「출입문 충격 에너지를 활용한 비상 전력 하베스팅 탐구」 데이터 기반 시뮬레이션")

# 2. 시뮬레이션 사용 방법 안내 (접이식 패널)
with st.expander("📖 시뮬레이션 사용 방법 및 탐구 원리 안내 (클릭하여 열기)", expanded=True):
    col_guide1, col_guide2 = st.columns(2)
    with col_guide1:
        st.markdown("**1️⃣ 조작 방법**")
        st.markdown("- **왼쪽 사이드바**에서 **완충재 종류**, **충격 조건(질량·속도 또는 낙하 높이)**, **출입문 개폐 횟수**, **축전 회로(캐패시터 용량)** 값을 슬라이더 또는 직접 숫자 입력으로 조절하세요.")
        st.markdown("- 값을 바꾸면 실시간으로 **예상 피크 전압, 충격력(F), 소자 누적 피로도, 캐패시터 충전 전압**이 자동 계산됩니다.")
    with col_guide2:
        st.markdown("**2️⃣ 핵심 탐구 포인트**")
        st.markdown("- **트레이드오프(상충관계) 확인:** 완충재가 없을수록 순간 전압은 높지만 충격 시간(Δt)이 짧아 충격력(F = I / Δt)이 커지므로 소자가 파손됩니다.")
        st.markdown("- **최적 조건 검증:** **3.0mm 고무 패드**와 다른 소재를 번갈아 선택해 소자 보호와 실용 전압(약 8.4V) 사이의 균형을 비교해 보세요.")

st.divider()

# 3. 사이드바: 입력 파라미터
st.sidebar.header("🎛️ 시뮬레이션 변수 설정")

selected_cushion = st.sidebar.selectbox(
    "1. 완충재 조건 선택",
    options=list(CUSHION_PROFILES.keys()),
    index=2,
)
profile = CUSHION_PROFILES[selected_cushion]

st.sidebar.subheader("2. 충격 조건 (문 닫힘 강도)")
input_mode = st.sidebar.radio(
    "입력 기준 선택",
    ["보고서 실험 기준 (추 질량 · 낙하 높이)", "출입문 적용 기준 (문 유효질량 · 닫힘 속도)"],
    index=0,
)

if input_mode == "보고서 실험 기준 (추 질량 · 낙하 높이)":
    mass_g = st.sidebar.slider("낙하 추 질량 (g)", min_value=50, max_value=500, value=100, step=10)
    height_cm = st.sidebar.slider("낙하 높이 (cm)", min_value=10, max_value=100, value=30, step=5)
    velocity_ms = math.sqrt(2 * G * (height_cm / 100.0))
else:
    mass_g = st.sidebar.slider("문 충격부 유효 질량 (g)", min_value=100, max_value=1000, value=250, step=50)
    velocity_ms = st.sidebar.slider("문 닫힘 충돌 속도 (m/s)", min_value=0.5, max_value=5.0, value=1.8, step=0.1)
    height_cm = ((velocity_ms ** 2) / (2 * G)) * 100.0

st.sidebar.subheader("3. 반복 작동 및 축전 회로 설정")
cycle_count = st.sidebar.number_input(
    "출입문 개폐(충격) 반복 횟수 (회)",
    min_value=1,
    max_value=500,
    value=30,
    step=5,
)
rapid_open = st.sidebar.checkbox("연속 빠른 개폐 조건 적용 (복원 속도 반영)", value=True)

capacitor_uf = st.sidebar.slider("축전 캐패시터 용량 (μF)", min_value=10, max_value=1000, value=100, step=10)
diode_drop_v = st.sidebar.slider("브릿지 정류 다이오드 전압 강하 (V)", min_value=0.0, max_value=1.4, value=
