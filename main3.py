import streamlit as st
import streamlit.components.v1 as components

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="AbAg-Fold AI 구조 예측 & 데이터 정제 시뮬레이터",
    page_icon="🧬",
    layout="wide",
)

# 2. 상단 헤더 (보고서 프로젝트 정보 반영)
st.title("🧬 항체-항원 결합 AI 구조 예측 및 데이터 정제 시뮬레이터")
st.caption(
    "거제상문고등학교 2026학년도 교과심화탐구 프로젝트 | 팀 '항원과 항체' (20527 정시연, 20708 박준영)"
)
st.info(
    "💡 **탐구 핵심:** AlphaFold3 기반 항체 설계(AbAg-Fold)에서 **데이터 정제(결측치 처리, 표준 용어 매핑, 물리화학적 필터링)**가 "
    "AI의 결합 구조 예측 정확도와 신뢰성을 어떻게 극대화하는지 직접 변수를 조절하며 확인해 보세요. "
    "(처음 이용하신다면 아래 **'📖 사용 방법'** 탭을 먼저 확인해 보세요!)"
)

# 3. 사이드바: 시뮬레이션 변수 제어 (슬라이더 & 수치 입력)
st.sidebar.header("⚙️ 시뮬레이션 변수 조절")

st.sidebar.subheader("1️⃣ 생명과학적 조건 (항원-항체 특성)")
antigen_type = st.sidebar.selectbox(
    "타겟 항원 그룹 선택",
    [
        "A형 인플루엔자 (표준 변이)",
        "SARS-CoV-2 (고변이 스파이크)",
        "희귀 바이러스 (제한적 데이터 그룹)",
    ],
    help="보고서 내용: 항원 그룹 구성이 제한적일수록 AI 모델링의 난이도가 상승합니다.",
)

cdr_complexity = st.sidebar.slider(
    "다중 CDR(상보성 결정 부위) 변이 복잡도",
    min_value=1,
    max_value=10,
    value=5,
    help="수치가 높을수록 다중 CDR 조합으로 인해 결합 구조 예측 변동성이 커집니다.",
)

temperature = st.sidebar.number_input(
    "반응 환경 온도 (°C)",
    min_value=30.0,
    max_value=45.0,
    value=36.5,
    step=0.5,
    help="생체 적정 온도(36.5°C)에서 벗어날수록 물리화학적 결합 안정성이 떨어집니다.",
)

st.sidebar.divider()
st.sidebar.subheader("2️⃣ AI 학습 데이터 오염도 (노이즈)")
raw_noise_rate = st.sidebar.slider(
    "원본 데이터 오류·노이즈 비율 (%)",
    min_value=0,
    max_value=80,
    value=45,
    step=5,
    help="결측치, 오기입된 아미노산 서열, 비정상 결합 구조 등 정제 전 데이터 오류 비율",
)

st.sidebar.divider()
st.sidebar.subheader("3️⃣ 데이터 정제 알고리즘 적용 (해결책)")
use_missing_filter = st.sidebar.checkbox(
    "✅ 1단계: 결측치 배제 및 이상치 필터링",
    value=True,
    help="오류 데이터를 단순 학습하지 않도록 결측치와 노이즈를 제거합니다.",
)
use_standard_vocab = st.sidebar.checkbox(
    "✅ 2단계: 표준 용어집(대표어) 매핑 전처리",
    value=True,
    help="서로 다르게 표기된 아미노산/항원 명칭을 대표어로 통일합니다.",
)
use_physicochemical = st.sidebar.checkbox(
    "✅ 3단계: 물리화학적 3D 구조 정제 (AbAg-Fold)",
    value=False,
    help="생체 내 실제 결합 에너지와 입체 장애를 검증하여 신뢰도 높은 구조만 선별합니다.",
)

# 4. 핵심 시뮬레이션 연산 로직 (순수 Python 수학 연산)
group_penalty = {
    "A형 인플루엔자 (표준 변이)": 2.0,
    "SARS-CoV-2 (고변이 스파이크)": 8.0,
    "희귀 바이러스 (제한적 데이터 그룹)": 14.0,
}[antigen_type]

temp_penalty = abs(temperature - 36.5) * 2.2
cdr_penalty = cdr_complexity * 1.8

effective_noise = float(raw_noise_rate)
if use_missing_filter:
    effective_noise *= 0.55
if use_standard_vocab:
    effective_noise *= 0.70
if use_physicochemical:
    effective_noise *= 0.45

raw_accuracy = max(
    5.0,
    min(99.2, 98.0 - (raw_noise_rate * 0.75) - group_penalty - cdr_penalty - temp_penalty),
)
cleaned_accuracy = max(
    8.0,
    min(99.5, 98.5 - (effective_noise * 0.75) - (group_penalty * 0.6) - (cdr_penalty * 0.7) - temp_penalty),
)

rmsd_score = round(0.8 + (100 - cleaned_accuracy) * 0.065, 2)
efficiency_gain = round(max(0.0, (cleaned_accuracy - 40) * 1.15), 1)

# 5. 상단 핵심 지표 카드 (KPI)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(
        label="🎯 AI 결합 구조 예측 정확도",
        value=f"{cleaned_accuracy:.1f}%",
        delta=f"{cleaned_accuracy - raw_accuracy:+.1f}%p (정제 전 대비)",
    )
with col2:
    st.metric(
        label="📐 3D 구조 예측 오차 (RMSD)",
        value=f"{rmsd_score} Å",
        delta="2.0Å 이하 고신뢰" if rmsd_score <= 2.0 else "결합 오차 주의",
        delta_color="normal" if rmsd_score <= 2.0 else "inverse",
    )
with col3:
    st.metric(
        label="🧹 잔여 데이터 노이즈율",
        value=f"{effective_noise:.1f}%",
        delta=f"-{raw_noise_rate - effective_noise:.1f}%p 제거됨",
        delta_color="inverse",
    )
with col4:
    st.metric(
        label="💊 신약 후보 도출 효율 상승",
        value=f"+{efficiency_gain}%",
        delta="기간·비용 단축 효과",
    )

st.divider()

# 6. 메인 시각화 영역 (좌: 항원-항체 2D 구조 결합 시뮬레이션 SVG / 우: 정제 단계별 정확도 그래프)
left_col, right_col = st.columns([1.15, 1])

with left_col:
    st.subheader("🔬 항원-항체 결합 구조 시각화 (실시간 시뮬레이션)")

    gap = int((100 - cleaned_accuracy) * 0.65)
    angle_error = int((100 - cleaned_accuracy) * 0.28)

    if cleaned_accuracy >= 80:
        status_text = "✅ 정상 특이적 결합 (고신뢰 항체 설계 성공)"
        status_color = "#16a34a"
        antibody_color = "#2563eb"
    elif cleaned_accuracy >= 55:
        status_text = "⚠️ 부분 결합 / 다중 CDR 변동성 오차 발생"
        status_color = "#d97706"
        antibody_color = "#f59e0b"
    else:
        status_text = "❌ 결합 실패 / 비특이적 오작동 (노이즈 학습 부작용)"
        status_color = "#dc2626"
        antibody_color = "#ef4444"

    svg_html = f"""
    <div style="border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px; background: #f8fafc; text-align: center;">
        <div style="font-weight: 700; font-size: 16px; color: {status_color}; margin-bottom: 8px;">
            {status_text}
        </div>
        <svg width="100%" height="290" viewBox="0 0 500 290" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <pattern id="grid" width="25" height="25" patternUnits="userSpaceOnUse">
                    <path d="M 25 0 L 0 0 0 25" fill="none" stroke="#e2e8f0" stroke-width="1"/>
                </pattern>
            </defs>
            <rect width="500" height="290" fill="url(#grid)" rx="8"/>

            <g transform="translate({145 - gap//2}, 145)">
                <circle cx="0" cy="0" r="52" fill="#fee2e2" stroke="#ef4444" stroke-width="3"/>
                <polygon points="48,-18 76,0 48,18" fill="#ef4444"/>
                <circle cx="-18" cy="-48" r="10" fill="#f87171"/>
                <circle cx="-18" cy="48" r="10" fill="#f87171"/>
                <text x="0" y="5" text-anchor="middle" font-size="14" font-weight="bold" fill="#991b1b">항원 (Antigen)</text>
                <text x="0" y="22" text-anchor="middle" font-size="10" fill="#b91c1c">에피토프(항원결정기)</text>
            </g>

            <circle cx="235" cy="145" r="{max(8, 35 - gap//2)}" fill="{status_color}" opacity="{0.15 if cleaned_accuracy < 80 else 0.35}"/>

            <g transform="translate({320 + gap//2}, 145) rotate({angle_error})">
                <rect x="10" y="-14" width="85" height="11" rx="5" fill="{antibody_color}"/>
                <rect x="10" y="3" width="85" height="11" rx="5" fill="{antibody_color}"/>
                <g transform="rotate(-32)">
                    <rect x="-65" y="-12" width="75" height="11" rx="5" fill="{antibody_color}"/>
                    <polygon points="-65,-12 -82,-18 -72,-6 -82,0 -65,-1" fill="#1d4ed8"/>
                </g>
                <g transform="rotate(32)">
                    <rect x="-65" y="1" width="75" height="11" rx="5" fill="{antibody_color}"/>
                    <polygon points="-65,1 -82,0 -72,6 -82,18 -65,12" fill="#1d4ed8"/>
                </g>
                <text x="52" y="-24" text-anchor="middle" font-size="13" font-weight="bold" fill="#1e3a8a">항체 (Antibody)</text>
                <text x="-35" y="-48" text-anchor="middle" font-size="11" font-weight="bold" fill="#2563eb">CDR 결합 부위</text>
            </g>

            <text x="250" y="272" text-anchor="middle" font-size="12" fill="#475569">
                결합 간격 오차: {gap}px | CDR 변이 복잡도: Lv.{cdr_complexity} | 잔여 노이즈: {effective_noise:.1f}%
            </text>
        </svg>
    </div>
    """
    components.html(svg_html, height=345)

with right_col:
    st.subheader("📊 데이터 정제 단계별 AI 예측 정확도 비교")

    acc_step0 = round(
        max(5.0, min(99.0, 98.0 - (raw_noise_rate * 0.75) - group_penalty - cdr_penalty - temp_penalty)),
        1,
    )
    acc_step1 = round(
        max(5.0, min(99.0, 98.2 - (raw_noise_rate * 0.55 * 0.75) - (group_penalty * 0.85) - (cdr_penalty * 0.9) - temp_penalty)),
        1,
    )
    acc_step2 = round(
        max(5.0, min(99.0, 98.3 - (raw_noise_rate * 0.55 * 0.70 * 0.75) - (group_penalty * 0.75) - (cdr_penalty * 0.8) - temp_penalty)),
        1,
    )
    acc_step3 = round(
        max(5.0, min(99.5, 98.5 - (raw_noise_rate * 0.55 * 0.70 * 0.45 * 0.75) - (group_penalty * 0.6) - (cdr_penalty * 0.7) - temp_penalty)),
        1,
    )

    chart_data = {
        "정제 단계": [
            "0. 원본 데이터(미정제)",
            "1. 결측치 배제 후",
            "2. 표준 용어집 매핑 후",
            "3. 물리화학적 3D 정제 후",
        ],
        "AI 예측 정확도 (%)": [acc_step0, acc_step1, acc_step2, acc_step3],
    }
    st.bar_chart(chart_data, x="정제 단계", y="AI 예측 정확도 (%)", height=270)
    st.caption(
        "※ AI는 스스로 데이터의 진위를 완벽히 판별하지 못하므로, 단계별 전처리 필터링을 거칠수록 실제 생체 결합 구조와 일치하는 정확도가 상승합니다."
    )

# 7. 하단 탭 영역 (사용 방법 탭 추가)
st.divider()
tab_guide, tab1, tab2, tab3 = st.tabs(
    [
        "📖 사용 방법",
        "🧪 전처리 알고리즘 데이터 비교표",
        "📈 CDR 변이 복잡도에 따른 한계 곡선",
        "📝 탐구 보고서 요약 & 결론",
    ]
)

with tab_guide:
    st.markdown(
        """
        ### 📖 웹앱 사용 방법 안내

        이 시뮬레이터는 **항체-항원 결합의 생물학적 특성**과 **AI 구조 예측(AbAg-Fold)의 한계**, 그리고 이를 극복하기 위한 **데이터 정제의 효과**를 직관적으로 체험할 수 있도록 만들어졌습니다.

        #### 1단계: 왼쪽 사이드바에서 조건 설정하기
        * **타겟 항원 그룹 선택:** 항원 종류에 따른 데이터 구성 차이를 선택합니다. *(예: 희귀 바이러스일수록 제한된 데이터로 인해 예측 난이도가 올라갑니다.)*
        * **다중 CDR 변이 복잡도(1~10 슬라이더):** 항체의 항원 결합 부위(CDR) 조합이 얼마나 복잡하고 변이가 많은지 조절합니다.
        * **반응 환경 온도(°C 숫자 입력):** 30.0°C~45.0°C 사이에서 온도를 직접 입력해 보세요. 생체 적정 온도(36.5°C)에서 멀어질수록 결합 안정성에 영향을 줍니다.
        * **원본 데이터 오류·노이즈 비율(0~80% 슬라이더):** 결측치, 잘못된 서열 등 정제 전 학습 데이터에 섞인 오류 비율을 설정합니다.

        #### 2단계: 데이터 정제 단계 체크박스 켜고 끄기
        * **1단계 결측치 배제 및 이상치 필터링:** 잘못된 값이나 누락된 데이터를 학습에서 제외합니다.
        * **2단계 표준 용어집(대표어) 매핑 전처리:** 서로 다르게 표기된 용어를 표준 대표어로 통일합니다.
        * **3단계 물리화학적 3D 구조 정제(AbAg-Fold):** 결합 에너지와 구조적 타당성을 검증해 신뢰할 수 있는 데이터만 남깁니다.
        * 👉 **추천 실험:** 노이즈 비율을 높게(예: 60~70%) 둔 상태에서 체크박스를 하나씩 해제/선택해 보며 **정확도**와 **항원-항체 결합 모습**이 어떻게 달라지는지 비교해 보세요.

        #### 3단계: 시각적 결과 및 상세 탭 확인하기
        * **상단 4개 지표 카드:** 예측 정확도, 3D 구조 오차(RMSD, 낮을수록 좋음), 잔여 노이즈율, 신약 후보 도출 효율 상승률을 한눈에 봅니다.
        * **왼쪽 항원-항체 결합 그림:** 정확도가 낮을수록 항원(왼쪽)과 항체(오른쪽)가 어긋나거나 결합이 불안정해지고, 정제를 거치면 정상 결합 상태로 가까워집니다.
        * **오른쪽 막대그래프 & 아래 탭:** 정제 단계별 정확도 변화, CDR 복잡도에 따른 모델 한계 곡선, 탐구 결론 요약을 확인할 수 있습니다.
        """
    )

with tab1:
    st.markdown("#### 공공데이터 및 AbAg-Fold 전처리 알고리즘 적용 전/후 비교")
    st.write(
        "조사한 전처리 알고리즘(결측치 배제, 표준 용어집 대표어 치환, 물리화학적 검증)이 실제 학습 데이터셋을 어떻게 정제하는지 보여줍니다."
    )
    sample_rows = [
        {
            "데이터 ID": "AB-101",
            "원본 항원 표기": "SARS_CoV2_Spike",
            "원본 결합 에너지": "NaN (결측치)",
            "정제 후 표준 표기": "SARS-CoV-2 (대표어 매핑)" if use_standard_vocab else "SARS_CoV2_Spike (미정제)",
            "정제 처리 결과": "학습 제외 (결측치 배제)" if use_missing_filter else "⚠️ 오류 학습됨 (AI 오작동 원인)",
        },
        {
            "데이터 ID": "AB-102",
            "원본 항원 표기": "Influenza_A_H1N1",
            "원본 결합 에너지": "-11.4 kcal/mol",
            "정제 후 표준 표기": "Influenza-A (대표어 매핑)" if use_standard_vocab else "Influenza_A_H1N1",
            "정제 처리 결과": "✅ 고신뢰 3D 구조 채택" if use_physicochemical else "일반 학습 데이터 포함",
        },
        {
            "데이터 ID": "AB-103",
            "원본 항원 표기": "h1n1_virus_var",
            "원본 결합 에너지": "+42.8 kcal/mol (비정상 반발)",
            "정제 후 표준 표기": "Influenza-A (대표어 매핑)" if use_standard_vocab else "h1n1_virus_var",
            "정제 처리 결과": "물리화학적 필터링으로 제거됨" if use_physicochemical else "⚠️ 비특이적 결합 구조 학습",
        },
    ]
    st.dataframe(sample_rows, use_container_width=True)

with tab2:
    st.markdown("#### 다중 CDR 조합 복잡도 증가에 따른 예측 안정성 비교")
    st.write(
        "보고서에서 분석한 기술적 한계인 **'다중 CDR 조합에서의 개선률 변동성 및 다중 변이 모델링 한계'**를 시뮬레이션한 그래프입니다."
    )
    cdr_levels = list(range(1, 11))
    uncleaned_curve = [
        round(max(5.0, 95.0 - (raw_noise_rate * 0.75) - (c * 2.4) - group_penalty), 1)
        for c in cdr_levels
    ]
    cleaned_curve = [
        round(max(10.0, 98.0 - (effective_noise * 0.75) - (c * 1.4) - (group_penalty * 0.6)), 1)
        for c in cdr_levels
    ]
    line_data = {
        "CDR 변이 복잡도 (Lv.1~10)": cdr_levels,
        "미정제 데이터 학습 모델 (%)": uncleaned_curve,
        "정제 데이터(AbAg-Fold) 학습 모델 (%)": cleaned_curve,
    }
    st.line_chart(
        line_data,
        x="CDR 변이 복잡도 (Lv.1~10)",
        y=["미정제 데이터 학습 모델 (%)", "정제 데이터(AbAg-Fold) 학습 모델 (%)"],
        height=280,
    )

with tab3:
    st.markdown(
        """
        ### 📌 프로젝트 탐구 결론 요약
        1. **AI-생명과학 융합의 가치:** 항원-항체 복합체 3차원 구조를 AI(AlphaFold3 기반)로 대량 예측함으로써 신약 개발 기간과 비용을 획기적으로 단축하고 난치병 치료 가능성을 넓힐 수 있습니다.
        2. **기술적 한계:** 실제 실험 대비 정확도 한계, 제한적인 항원 그룹 구성, 그리고 **다중 CDR 조합에서의 높은 변동성**으로 인해 다중 변이 조건에서의 모델링 안정성이 떨어집니다.
        3. **데이터 정제의 필수성:** AI는 데이터의 진위를 스스로 완벽히 판별하지 못해 노이즈를 그대로 학습하므로, **결측치 제거·표준 용어집 매핑·물리화학적 구조 정제**를 거쳐야만 예측 정확도와 신뢰성을 극대화할 수 있습니다.
        """
    )
