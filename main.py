import streamlit as st

# -------------------------------------------------
# 기본 설정
# -------------------------------------------------
st.set_page_config(
    page_title="콩닥콩닥 MBTI 직업 추천소",
    page_icon="💖",
    layout="centered",
)

# -------------------------------------------------
# MBTI별 데이터
# -------------------------------------------------
MBTI_DATA = {
    "ISTJ": {
        "nickname": "꼼꼼한 계획 요정",
        "emoji": "📚",
        "description": "책임감이 강하고 체계적으로 일을 처리하는 현실적인 유형이에요.",
        "strengths": ["책임감", "정확성", "계획성"],
        "jobs": [
            ("회계사", "숫자와 자료를 꼼꼼하게 분석하는 능력을 살릴 수 있어요.", "🧾"),
            ("공무원", "정해진 절차에 따라 안정적으로 업무를 수행하는 데 잘 맞아요.", "🏛️"),
            ("데이터 분석가", "복잡한 데이터를 정확하게 정리하고 의미를 찾을 수 있어요.", "📊"),
            ("품질관리 전문가", "작은 오류도 놓치지 않는 세심함이 큰 장점이 돼요.", "🔍"),
        ],
    },
    "ISFJ": {
        "nickname": "따뜻한 배려 요정",
        "emoji": "🧸",
        "description": "다른 사람을 세심하게 살피고 맡은 일을 성실하게 해내는 유형이에요.",
        "strengths": ["배려심", "성실함", "관찰력"],
        "jobs": [
            ("간호사", "사람의 상태를 세심히 살피고 따뜻하게 돌볼 수 있어요.", "🩺"),
            ("초등학교 교사", "학생의 성장을 차분하고 다정하게 도울 수 있어요.", "🍎"),
            ("사회복지사", "도움이 필요한 사람에게 현실적인 지원을 제공할 수 있어요.", "🤝"),
            ("사서", "조용하고 체계적인 환경에서 정보와 사람을 연결할 수 있어요.", "📖"),
        ],
    },
    "INFJ": {
        "nickname": "마음 읽는 별빛 요정",
        "emoji": "🌙",
        "description": "사람의 마음과 가능성을 깊이 이해하고 의미 있는 변화를 꿈꾸는 유형이에요.",
        "strengths": ["통찰력", "공감 능력", "창의성"],
        "jobs": [
            ("상담심리사", "사람의 감정을 깊이 이해하고 성장을 도울 수 있어요.", "💬"),
            ("작가", "풍부한 생각과 감정을 글로 섬세하게 표현할 수 있어요.", "✍️"),
            ("UX 리서처", "사용자의 숨은 필요를 발견하고 더 나은 경험을 설계해요.", "🔎"),
            ("교육 기획자", "사람의 성장을 돕는 의미 있는 교육을 설계할 수 있어요.", "🎓"),
        ],
    },
    "INTJ": {
        "nickname": "미래 설계 천재 고양이",
        "emoji": "🐈‍⬛",
        "description": "복잡한 문제의 구조를 파악하고 장기적인 전략을 세우는 유형이에요.",
        "strengths": ["전략적 사고", "독립성", "문제 해결력"],
        "jobs": [
            ("소프트웨어 개발자", "논리적으로 시스템을 설계하고 문제를 해결할 수 있어요.", "💻"),
            ("연구원", "한 분야를 깊이 탐구하며 새로운 지식을 만들 수 있어요.", "🔬"),
            ("정보보안 전문가", "위험을 미리 예측하고 체계적인 방어 전략을 세워요.", "🛡️"),
            ("전략 컨설턴트", "복잡한 상황을 분석해 장기적인 해결책을 제시할 수 있어요.", "♟️"),
        ],
    },
    "ISTP": {
        "nickname": "척척 해결 발명 요정",
        "emoji": "🛠️",
        "description": "도구와 원리를 빠르게 이해하고 실제 문제를 능숙하게 해결하는 유형이에요.",
        "strengths": ["실용성", "적응력", "분석력"],
        "jobs": [
            ("로봇 엔지니어", "기계와 프로그램을 직접 다루며 새로운 장치를 만들 수 있어요.", "🤖"),
            ("항공 정비사", "정밀한 장비의 문제를 빠르게 찾아 해결할 수 있어요.", "✈️"),
            ("응급구조사", "긴박한 상황에서도 침착하게 판단하고 행동할 수 있어요.", "🚑"),
            ("게임 개발자", "논리와 기술을 활용해 상호작용하는 세계를 만들 수 있어요.", "🎮"),
        ],
    },
    "ISFP": {
        "nickname": "말랑말랑 감성 요정",
        "emoji": "🎨",
        "description": "자신만의 감각이 뚜렷하고 사람과 세상을 따뜻하게 바라보는 유형이에요.",
        "strengths": ["감수성", "유연성", "미적 감각"],
        "jobs": [
            ("그래픽 디자이너", "색과 형태를 활용해 자신만의 감성을 표현할 수 있어요.", "🖌️"),
            ("반려동물 전문가", "생명을 다정하고 세심하게 돌보는 강점을 살릴 수 있어요.", "🐶"),
            ("플로리스트", "자연과 색감을 활용해 아름다운 공간을 만들 수 있어요.", "🌷"),
            ("사진작가", "순간의 분위기와 감정을 섬세하게 포착할 수 있어요.", "📷"),
        ],
    },
    "INFP": {
        "nickname": "꿈꾸는 구름 요정",
        "emoji": "☁️",
        "description": "풍부한 상상력과 가치관을 바탕으로 자신만의 이야기를 만드는 유형이에요.",
        "strengths": ["상상력", "공감 능력", "진정성"],
        "jobs": [
            ("콘텐츠 작가", "자신만의 세계관과 메시지를 이야기로 표현할 수 있어요.", "📝"),
            ("일러스트레이터", "상상 속 장면과 감정을 그림으로 전달할 수 있어요.", "🖼️"),
            ("상담사", "다른 사람의 이야기를 진심으로 듣고 위로할 수 있어요.", "🌿"),
            ("브랜드 스토리텔러", "브랜드의 가치와 감성을 매력적인 이야기로 만들어요.", "💌"),
        ],
    },
    "INTP": {
        "nickname": "호기심 폭발 탐구 요정",
        "emoji": "🧪",
        "description": "새로운 원리를 탐구하고 논리적으로 아이디어를 발전시키는 유형이에요.",
        "strengths": ["논리력", "호기심", "창의적 사고"],
        "jobs": [
            ("AI 연구원", "새로운 알고리즘과 기술의 가능성을 깊이 탐구할 수 있어요.", "🧠"),
            ("데이터 과학자", "데이터 속 규칙을 발견하고 새로운 가치를 만들 수 있어요.", "📈"),
            ("게임 시스템 기획자", "복잡한 규칙과 구조를 창의적으로 설계할 수 있어요.", "🕹️"),
            ("대학교수", "관심 분야를 깊이 연구하고 지식을 나눌 수 있어요.", "🏫"),
        ],
    },
    "ESTP": {
        "nickname": "에너지 뿜뿜 모험 요정",
        "emoji": "⚡",
        "description": "빠르게 상황을 파악하고 사람들과 직접 부딪치며 성과를 만드는 유형이에요.",
        "strengths": ["행동력", "순발력", "사교성"],
        "jobs": [
            ("스포츠 마케터", "활동적인 현장에서 사람들의 관심을 끌어낼 수 있어요.", "🏀"),
            ("소방관", "위기 상황에서 신속하고 용감하게 행동할 수 있어요.", "🚒"),
            ("영업 전문가", "사람들과 빠르게 친밀감을 만들고 기회를 발견해요.", "🤝"),
            ("방송 리포터", "현장의 생생한 소식을 빠르고 활기차게 전달할 수 있어요.", "🎤"),
        ],
    },
    "ESFP": {
        "nickname": "반짝반짝 분위기 요정",
        "emoji": "✨",
        "description": "밝은 에너지와 뛰어난 표현력으로 주변 사람을 즐겁게 만드는 유형이에요.",
        "strengths": ["표현력", "친화력", "긍정성"],
        "jobs": [
            ("공연 기획자", "사람들이 즐거워할 특별한 경험을 만들 수 있어요.", "🎪"),
            ("크리에이터", "자신만의 매력과 아이디어를 콘텐츠로 표현할 수 있어요.", "📹"),
            ("승무원", "다양한 사람을 밝고 친절하게 응대할 수 있어요.", "🛫"),
            ("이벤트 플래너", "활기찬 분위기 속에서 행사를 멋지게 완성할 수 있어요.", "🎉"),
        ],
    },
    "ENFP": {
        "nickname": "아이디어 팡팡 햇살 요정",
        "emoji": "🌈",
        "description": "새로운 가능성을 발견하고 사람들에게 즐거운 영감을 주는 유형이에요.",
        "strengths": ["창의성", "열정", "소통 능력"],
        "jobs": [
            ("광고 기획자", "톡톡 튀는 아이디어로 사람의 마음을 움직일 수 있어요.", "📣"),
            ("콘텐츠 크리에이터", "다양한 관심사와 개성을 매력적인 콘텐츠로 만들어요.", "🎬"),
            ("진로 상담사", "사람의 장점과 가능성을 발견하고 용기를 줄 수 있어요.", "🧭"),
            ("서비스 기획자", "새로운 아이디어를 사람들에게 유용한 서비스로 발전시켜요.", "💡"),
        ],
    },
    "ENTP": {
        "nickname": "엉뚱발랄 아이디어 요정",
        "emoji": "🚀",
        "description": "새로운 아이디어를 빠르게 떠올리고 기존 방식에 도전하는 유형이에요.",
        "strengths": ["창의적 문제 해결", "도전 정신", "토론 능력"],
        "jobs": [
            ("창업가", "새로운 아이디어를 실제 서비스나 사업으로 만들 수 있어요.", "🌱"),
            ("제품 기획자", "사람들이 필요로 할 새로운 제품을 상상하고 설계해요.", "📱"),
            ("변리사", "새로운 기술과 아이디어의 가치를 논리적으로 보호해요.", "⚖️"),
            ("방송 PD", "참신한 기획으로 새로운 형식의 콘텐츠를 만들 수 있어요.", "📺"),
        ],
    },
    "ESTJ": {
        "nickname": "믿음직한 리더 요정",
        "emoji": "👑",
        "description": "목표와 기준을 분명히 세우고 조직을 효율적으로 이끄는 유형이에요.",
        "strengths": ["리더십", "실행력", "조직력"],
        "jobs": [
            ("프로젝트 매니저", "일정과 역할을 체계적으로 관리해 목표를 완수할 수 있어요.", "📋"),
            ("경영 관리자", "조직의 자원과 사람을 효율적으로 운영할 수 있어요.", "🏢"),
            ("경찰", "원칙과 책임감을 바탕으로 질서와 안전을 지킬 수 있어요.", "👮"),
            ("행정 전문가", "복잡한 업무를 체계적으로 조정하고 실행할 수 있어요.", "🗂️"),
        ],
    },
    "ESFJ": {
        "nickname": "다정다감 인기 요정",
        "emoji": "🍰",
        "description": "사람들과 조화롭게 어울리며 필요한 도움을 친절하게 제공하는 유형이에요.",
        "strengths": ["협동심", "배려심", "소통 능력"],
        "jobs": [
            ("호텔리어", "사람들에게 세심하고 기분 좋은 서비스를 제공할 수 있어요.", "🏨"),
            ("보건교사", "학생의 건강과 마음을 따뜻하게 돌볼 수 있어요.", "💗"),
            ("인사 담당자", "조직 구성원과 소통하며 좋은 근무 환경을 만들 수 있어요.", "👥"),
            ("고객 경험 매니저", "고객의 목소리를 듣고 더 좋은 서비스를 만들어요.", "🎀"),
        ],
    },
    "ENFJ": {
        "nickname": "용기를 주는 리더 요정",
        "emoji": "🌟",
        "description": "사람의 가능성을 발견하고 모두가 함께 성장하도록 이끄는 유형이에요.",
        "strengths": ["리더십", "공감 능력", "설득력"],
        "jobs": [
            ("교사", "학생의 장점을 발견하고 성장할 수 있도록 이끌어 줄 수 있어요.", "🏫"),
            ("HRD 전문가", "구성원의 역량을 키우는 교육과 프로그램을 설계해요.", "🌱"),
            ("홍보 전문가", "사람과 조직의 가치를 진정성 있게 전달할 수 있어요.", "📢"),
            ("사회적 기업가", "사람들과 협력해 사회 문제를 해결하는 일을 만들 수 있어요.", "🌍"),
        ],
    },
    "ENTJ": {
        "nickname": "당당한 목표 달성 요정",
        "emoji": "🦁",
        "description": "큰 목표를 세우고 전략적으로 사람과 자원을 이끄는 유형이에요.",
        "strengths": ["결단력", "전략성", "리더십"],
        "jobs": [
            ("기업 경영자", "큰 방향을 설정하고 조직을 목표까지 이끌 수 있어요.", "💼"),
            ("경영 컨설턴트", "기업의 문제를 분석하고 효과적인 전략을 제안할 수 있어요.", "📊"),
            ("프로덕트 매니저", "기술과 사용자, 비즈니스를 연결해 제품을 성장시켜요.", "🧩"),
            ("변호사", "논리적 사고와 설득력을 활용해 복잡한 문제를 해결해요.", "⚖️"),
        ],
    },
}

# -------------------------------------------------
# 스타일
# -------------------------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at 10% 20%, rgba(255, 210, 225, 0.65), transparent 30%),
            radial-gradient(circle at 90% 10%, rgba(218, 210, 255, 0.60), transparent 28%),
            linear-gradient(180deg, #fff9fc 0%, #fffef8 100%);
    }

    .block-container {
        max-width: 850px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    .hero {
        text-align: center;
        padding: 2.2rem 1rem 1.4rem;
        border-radius: 28px;
        background: rgba(255, 255, 255, 0.75);
        border: 2px solid rgba(255, 181, 205, 0.5);
        box-shadow: 0 12px 35px rgba(220, 130, 170, 0.13);
        margin-bottom: 1.5rem;
    }

    .hero-title {
        font-size: clamp(2rem, 6vw, 3.4rem);
        font-weight: 900;
        color: #ff5f9e;
        margin-bottom: 0.45rem;
        letter-spacing: -0.04em;
    }

    .hero-subtitle {
        color: #765d69;
        font-size: 1.05rem;
        line-height: 1.7;
    }

    .result-box {
        background: linear-gradient(135deg, #fff 0%, #fff2f8 100%);
        border: 2px solid #ffc5da;
        border-radius: 26px;
        padding: 1.7rem;
        margin: 1.1rem 0 1.4rem;
        box-shadow: 0 10px 30px rgba(255, 105, 160, 0.12);
        text-align: center;
    }

    .mbti-badge {
        display: inline-block;
        background: #ff77aa;
        color: white;
        font-weight: 900;
        font-size: 1.05rem;
        padding: 0.4rem 0.9rem;
        border-radius: 999px;
        margin-bottom: 0.65rem;
    }

    .result-name {
        font-size: 1.75rem;
        font-weight: 900;
        color: #5c4350;
        margin-bottom: 0.55rem;
    }

    .result-desc {
        color: #775f6a;
        line-height: 1.65;
    }

    .job-card {
        background: rgba(255, 255, 255, 0.92);
        border: 1.5px solid #ffd0df;
        border-radius: 22px;
        padding: 1.2rem 1.25rem;
        min-height: 160px;
        box-shadow: 0 8px 24px rgba(192, 113, 143, 0.09);
        margin-bottom: 1rem;
    }

    .job-title {
        font-size: 1.18rem;
        font-weight: 900;
        color: #d84c85;
        margin-bottom: 0.45rem;
    }

    .job-description {
        color: #6e5d65;
        font-size: 0.96rem;
        line-height: 1.58;
    }

    .strength-chip {
        display: inline-block;
        background: #f1e8ff;
        color: #7454a6;
        border-radius: 999px;
        padding: 0.34rem 0.72rem;
        margin: 0.2rem;
        font-weight: 700;
        font-size: 0.9rem;
    }

    .cheer {
        background: #fff7d9;
        border: 1.5px dashed #f3bd46;
        border-radius: 20px;
        padding: 1.1rem;
        text-align: center;
        color: #76571f;
        font-weight: 700;
        margin-top: 1.1rem;
    }

    .notice {
        color: #8a7480;
        font-size: 0.88rem;
        line-height: 1.6;
        text-align: center;
        padding-top: 1rem;
    }

    div[data-baseweb="select"] > div {
        border-radius: 16px;
        border-color: #ffb6ce;
        background: white;
    }

    .stButton > button {
        width: 100%;
        border: none;
        border-radius: 16px;
        background: linear-gradient(90deg, #ff78aa, #a886f7);
        color: white;
        font-weight: 900;
        font-size: 1.05rem;
        padding: 0.75rem 1rem;
        box-shadow: 0 8px 22px rgba(210, 102, 160, 0.22);
        transition: 0.2s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        color: white;
        border: none;
    }

    h2, h3 {
        color: #5f4854;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------
# 화면
# -------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <div style="font-size: 2.4rem;">💗 🐰 ✨</div>
        <div class="hero-title">콩닥콩닥 MBTI 직업 추천소</div>
        <div class="hero-subtitle">
            나의 MBTI를 선택하면<br>
            성격의 장점을 살릴 수 있는 직업을 사랑스럽게 추천해 드려요!
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("### 🌸 나의 MBTI는?")
selected_mbti = st.selectbox(
    "MBTI 선택",
    options=list(MBTI_DATA.keys()),
    index=None,
    placeholder="MBTI를 골라 주세요 💕",
    label_visibility="collapsed",
)

show_result = st.button("내게 어울리는 직업 찾기 💫")

if show_result:
    if selected_mbti is None:
        st.warning("먼저 MBTI를 선택해 주세요! 🐣")
    else:
        data = MBTI_DATA[selected_mbti]

        st.balloons()

        st.markdown(
            f"""
            <div class="result-box">
                <div class="mbti-badge">{selected_mbti}</div>
                <div style="font-size: 3rem;">{data["emoji"]}</div>
                <div class="result-name">{data["nickname"]}</div>
                <div class="result-desc">{data["description"]}</div>
                <div style="margin-top: 0.9rem;">
                    {''.join(f'<span class="strength-chip">#{strength}</span>' for strength in data["strengths"])}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### 🎀 이런 직업과 잘 어울려요")

        jobs = data["jobs"]
        for start in range(0, len(jobs), 2):
            columns = st.columns(2)
            for column, job in zip(columns, jobs[start:start + 2]):
                title, reason, icon = job
                with column:
                    st.markdown(
                        f"""
                        <div class="job-card">
                            <div style="font-size: 2rem;">{icon}</div>
                            <div class="job-title">{title}</div>
                            <div class="job-description">{reason}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        st.markdown(
            f"""
            <div class="cheer">
                🌷 {selected_mbti}의 장점은 하나의 정답이 아니라 특별한 가능성이에요.<br>
                관심 있는 분야를 직접 경험하며 나만의 꿈을 찾아보세요!
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown(
    """
    <div class="notice">
        ※ MBTI 결과는 진로를 결정하는 절대적인 기준이 아니에요.<br>
        흥미, 적성, 가치관, 경험을 함께 고려하는 진로 탐색 자료로 활용해 주세요.
    </div>
    """,
    unsafe_allow_html=True,
)
