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
diode_drop_v = st.sidebar.slider("브릿지 정류 다이오드 전압 강하 (V)", min_value=0.0, max_value=1.4, value=0.7, step=0.1)

# 4. 물리 및 전기 출력 계산 모델
momentum_ns = (mass_g / 1000.0) * velocity_ms
impact_scale = momentum_ns / BASE_MOMENTUM

delta_t_sec = profile["impact_time_ms"] / 1000.0
avg_force_n = momentum_ns / delta_t_sec

recovery_factor = profile["recovery_rate"] if rapid_open else 1.0

effective_scale = (impact_scale ** 0.85) * recovery_factor
est_avg_v = profile["base_avg_v"] * effective_scale
est_max_v = profile["base_max_v"] * effective_scale

force_stress = impact_scale ** 1.35
fatigue_percent = min(100.0, profile["damage_rate"] * force_stress * cycle_count)

if fatigue_percent >= 80.0:
    health_status = "🔴 파손 위험 (납땜 크랙/이탈)"
elif fatigue_percent >= 35.0:
    health_status = "🟡 주의 (표면 피로 누적)"
else:
    health_status = "🟢 안전 (소자 정상 작동)"

# 5. 메인 화면: 핵심 지표(KPI) 카드
st.subheader(f"📊 시뮬레이션 결과 요약 — [{selected_cushion}]")

k1, k2, k3, k4 = st.columns(4)
k1.metric(
    label="예상 평균 피크 전압",
    value=f"{est_avg_v:.2f} V",
    delta=f"최대 피크 {est_max_v:.2f} V",
)
k2.metric(
    label="평균 충격력 (F = I / Δt)",
    value=f"{avg_force_n:.1f} N",
    delta=f"충격시간 {profile['impact_time_ms']} ms",
    delta_color="off",
)
k3.metric(
    label=f"{cycle_count}회 후 소자 피로도",
    value=f"{fatigue_percent:.1f} %",
    delta=health_status,
    delta_color="inverse" if fatigue_percent >= 35.0 else "normal",
)

# 캐패시터 충전 시뮬레이션
usable_rectified_v = max(0.0, est_avg_v - diode_drop_v)
charge_efficiency = 0.035 * (100.0 / capacitor_uf)
cap_voltages = []
current_cap_v = 0.0

for step in range(1, int(cycle_count) + 1):
    step_fatigue = profile["damage_rate"] * force_stress * step
    efficiency_loss = 0.2 if step_fatigue > 85.0 else (1.0 - step_fatigue / 250.0)
    target_v = usable_rectified_v * max(0.1, efficiency_loss)
    if target_v > current_cap_v:
        current_cap_v += (target_v - current_cap_v) * min(0.5, charge_efficiency)
    cap_voltages.append({
        "개폐 횟수 (회)": step,
        "캐패시터 충전 전압 (V)": round(current_cap_v, 3),
        "소자 피로도 (%)": round(min(100.0, step_fatigue), 2),
    })

stored_energy_mj = 0.5 * (capacitor_uf * 1e-6) * (current_cap_v ** 2) * 1000.0
k4.metric(
    label="캐패시터 최종 충전 전압",
    value=f"{current_cap_v:.2f} V",
    delta=f"축전 에너지 {stored_energy_mj:.2f} mJ",
)

if current_cap_v >= 3.3:
    st.success(f"✅ **비상 전원 구동 가능:** 충전 전압({current_cap_v:.2f} V)이 고휘도 LED(약 2.0~3.0V) 및 저전력 비상 센서(3.3V) 구동 기준을 충족합니다.")
elif current_cap_v >= 1.8:
    st.info(f"💡 **저전력 LED 점등 가능:** 충전 전압({current_cap_v:.2f} V)으로 적색/황색 비상 표시 LED 점등이 가능합니다. 센서 구동을 위해 개폐 횟수를 늘리거나 캐패시터 용량을 조정해 보세요.")
else:
    st.warning(f"⚠️ **전압 부족 ({current_cap_v:.2f} V):** 다이오드 전압 강하({diode_drop_v}V) 이후 유효 충전 전압이 낮습니다. 완충재 조건 또는 개폐 횟수를 변경해 보세요.")

st.divider()

# 6. 시각적 비교 차트 1: 전체 완충재 조건별 트레이드오프 비교
st.subheader("📈 1. 완충재별 전압 출력 vs 소자 피로도 트레이드오프 비교")
st.caption("현재 설정된 충격 조건에서 5가지 완충재의 예상 성능을 한눈에 비교합니다.")

comparison_rows = []
for name, p in CUSHION_PROFILES.items():
    r_fac = p["recovery_rate"] if rapid_open else 1.0
    v_avg = p["base_avg_v"] * (impact_scale ** 0.85) * r_fac
    fat = min(100.0, p["damage_rate"] * force_stress * cycle_count)
    comparison_rows.append({
        "완충재 조건": name,
        "예상 평균 피크 전압 (V)": round(v_avg, 2),
        f"{cycle_count}회 후 소자 피로도 (%)": round(fat, 1),
        "충격 지속시간 (ms)": p["impact_time_ms"],
        "보고서 관찰 결과": p["status_note"],
    })

df_comp = pd.DataFrame(comparison_rows)

col_chart1, col_chart2 = st.columns(2)
with col_chart1:
    st.markdown("**완충재별 예상 평균 피크 전압 (V)**")
    st.bar_chart(df_comp.set_index("완충재 조건")["예상 평균 피크 전압 (V)"], color="#10B981")

with col_chart2:
    st.markdown(f"**완충재별 {cycle_count}회 충격 후 소자 피로도 (%) — 낮을수록 안전**")
    st.bar_chart(df_comp.set_index("완충재 조건")[f"{cycle_count}회 후 소자 피로도 (%)"], color="#EF4444")

with st.expander("📋 완충재별 상세 비교 데이터 표 보기"):
    st.dataframe(df_comp, use_container_width=True, hide_index=True)

st.divider()

# 7. 시각적 비교 차트 2: 개폐 반복에 따른 캐패시터 충전 곡선 및 피로도 추이
st.subheader("🔋 2. 브릿지 정류 · 캐패시터 축전 및 소자 피로도 변화 추이")
df_history = pd.DataFrame(cap_voltages).set_index("개폐 횟수 (회)")

col_line1, col_line2 = st.columns(2)
with col_line1:
    st.markdown(f"**출입문 개폐 횟수에 따른 캐패시터 충전 전압 (V) [용량: {capacitor_uf}μF]**")
    st.line_chart(df_history["캐패시터 충전 전압 (V)"], color="#2563EB")

with col_line2:
    st.markdown("**출입문 개폐 횟수에 따른 소자 누적 피로도 (%)**")
    st.line_chart(df_history["소자 피로도 (%)"], color="#F97316")
