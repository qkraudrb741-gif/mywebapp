import math
import pandas as pd
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="출입문 충격 에너지 압전 하베스팅 시뮬레이터",
    page_icon="⚡",
    layout="wide"
)

# 1. 보고서 실측 데이터 기반 완충재 프로파일 (기준: 100g 추, 30cm 낙하, 30회 반복)
CUSHION_PROFILES = {
    "미적용 (직접 충격)": {
        "thickness_mm": 0.0,
        "base_avg_v": 14.2,
        "base_max_v": 18.5,
        "impact_time_ms": 1.2,      # 충격 지속 시간 Δt (짧을수록 충격력 F 급증)
        "damage_rate": 2.8,         # 회당 누적 피로도 (%)
        "recovery_rate": 1.00,      # 연속 개폐 시 복원력 계수
        "status_note": "납땜부 크랙 발생, 전선 이탈 위험 높음",
        "color": "#EF4444"
    },
    "아크릴판 (2.0mm)": {
        "thickness_mm": 2.0,
        "base_avg_v": 11.8,
        "base_max_v": 13.6,
        "impact_time_ms": 2.0,
        "damage_rate": 1.4,
        "recovery_rate": 0.98,
        "status_note": "표면 미세 스크래치, 완충 미흡",
        "color": "#F59E0B"
    },
    "고무 패드 (3.0mm - 최적)": {
        "thickness_mm": 3.0,
        "base_avg_v": 8.4,
        "base_max_v": 9.8,
        "impact_time_ms": 4.2,
        "damage_rate": 0.15,
        "recovery_rate": 0.97,
        "status_note": "손상 없음 (소자 보호 및 실용 전압 확보)",
        "color": "#10B981"
    },
    "EVA 폼 (3.0mm)": {
        "thickness_mm": 3.0,
        "base_avg_v": 5.2,
        "base_max_v": 6.1,
        "impact_time_ms": 6.8,
        "damage_rate": 0.08,
        "recovery_rate": 0.78,      # 보고서 지적사항: 복원 속도 느림
        "status_note": "손상 없음, 복원 속도 느림",
        "color": "#3B82F6"
    },
    "스펀지 (5.0mm)": {
        "thickness_mm": 5.0,
        "base_avg_v": 2.1,
        "base_max_v": 2.8,
        "impact_time_ms": 11.5,
        "damage_rate": 0.03,
        "recovery_rate": 0.85,
        "status_note": "손상 없음, 충격 과다 흡수로 출력 낮음",
        "color": "#8B5CF6"
    }
}

# 기준 실험 조건 상수 (보고서 2단계 기준)
BASE_MASS_G = 100.0
BASE_HEIGHT_CM = 30.0
G = 9.81
BASE_IMPACT_VELOCITY = math.sqrt(2 * G * (BASE_HEIGHT_CM / 100.0))  # 약 2.426 m/s
BASE_MOMENTUM = (BASE_MASS_G / 1000.0) * BASE_IMPACT_VELOCITY       # 기준 충격량 I (N·s)

# 타이틀 및 개요
st.title("⚡ 출입문 충격 에너지 기반 압전 전력 하베스팅 시뮬레이터")
st.caption("2026학년도 교과심화탐구 프로젝트 「출입문 충격 에너지를 활용한 비상 전력 하베스팅 탐구」 데이터 기반 시뮬레이션")

# 2. 시뮬레이션 사용 방법 안내 (접이식 패널)
with st.expander("📖 시뮬레이션 사용 방법 및 탐구 원리 안내 (클릭하여 열기)", expanded=True):
    col_guide1, col_guide2 = st.columns(2)
    with col_guide1:
        st.markdown("""
        **1️⃣ 조작 방법**
        * **왼쪽 사이드바**에서 **완충재 종류**, **충격 조건(질량·속도 또는 낙하 높이)**, **출입문 개폐 횟수**, **축전 회로(캐패시터 용량)** 값을 슬라이더 또는 직접 숫자 입력으로 조절하세요.
        * 값을 바꾸면 실시간으로 **예상 피크 전압, 충격력($F$), 소자 누적 피로도, 캐패시터 충전 전압**이 자동 계산됩니다.
        """)
    with col_guide2:
        st.markdown("""
        **2️⃣ 핵심 탐구 포인트**
        * **트
