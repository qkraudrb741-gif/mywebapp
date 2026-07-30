import streamlit as st

st.set_page_config(
    page_title="멜로디 프롬프트 공방",
    page_icon="🎵",
    layout="centered",
)

GENRE_GUIDES = {
    "K-POP": {
        "tempo": "중간 템포 또는 빠른 템포",
        "instruments": "신스, 전자 드럼, 베이스, 피아노",
        "structure": "Intro - Verse - Pre-Chorus - Chorus - Verse - Chorus - Bridge - Final Chorus",
    },
    "발라드": {
        "tempo": "느리거나 중간 정도의 템포",
        "instruments": "피아노, 스트링, 어쿠스틱 기타, 부드러운 드럼",
        "structure": "Intro - Verse - Chorus - Verse - Chorus - Bridge - Final Chorus - Outro",
    },
    "힙합": {
        "tempo": "중간 템포의 그루브",
        "instruments": "808 베이스, 킥, 스네어, 하이햇, 신스",
        "structure": "Intro - Verse - Hook - Verse - Hook - Bridge - Final Hook",
    },
    "R&B": {
        "tempo": "느긋한 중간 템포",
        "instruments": "일렉트릭 피아노, 부드러운 베이스, 드럼, 패드 신스",
        "structure": "Intro - Verse - Pre-Chorus - Chorus - Verse - Chorus - Bridge - Outro",
    },
    "록": {
        "tempo": "중간 또는 빠른 템포",
        "instruments": "일렉트릭 기타, 베이스 기타, 드럼, 필요 시 신스",
        "structure": "Intro - Verse - Chorus - Verse - Chorus - Guitar Break - Final Chorus",
    },
    "인디 팝": {
        "tempo": "편안한 중간 템포",
        "instruments": "어쿠스틱 기타, 피아노, 가벼운 드럼, 따뜻한 신스",
        "structure": "Intro - Verse - Chorus - Verse - Chorus - Bridge - Outro",
    },
    "EDM": {
        "tempo": "빠른 템포",
        "instruments": "신스 리드, 서브 베이스, 전자 드럼, 효과음",
        "structure": "Intro - Build Up - Drop - Break - Build Up - Final Drop - Outro",
    },
    "재즈": {
        "tempo": "스윙감 있는 중간 템포",
        "instruments": "피아노, 콘트라베이스, 드럼, 색소폰 또는 트럼펫",
        "structure": "Intro - Theme - Verse - Instrumental Solo - Theme - Outro",
    },
    "어쿠스틱": {
        "tempo": "편안한 느린 템포 또는 중간 템포",
        "instruments": "어쿠스틱 기타, 피아노, 가벼운 퍼커션",
        "structure": "Intro - Verse - Chorus - Verse - Chorus - Bridge - Outro",
    },
    "시티 팝": {
        "tempo": "경쾌한 중간 템포",
        "instruments": "신스, 일렉트릭 피아노, 펑키한 베이스, 전자 드럼",
        "structure": "Intro - Verse - Pre-Chorus - Chorus - Verse - Chorus - Bridge - Final Chorus",
    },
}

MOOD_DETAILS = {
    "밝고 신나는": "밝은 장조 중심, 경쾌한 리듬, 기억하기 쉬운 후렴구",
    "따뜻하고 포근한": "부드러운 화성, 따뜻한 음색, 편안한 멜로디",
    "감성적이고 아련한": "서정적인 멜로디, 여운이 남는 코드 진행, 섬세한 감정 변화",
    "몽환적인": "공간감 있는 신스와 리버브, 반복적이고 신비로운 멜로디",
    "강렬하고 웅장한": "힘 있는 리듬, 넓은 음역, 점진적으로 고조되는 편곡",
    "차분하고 편안한": "단순하고 안정적인 리듬, 낮은 강도의 악기 구성",
    "슬프고 애절한": "단조 중심, 점차 높아지는 감정선, 호소력 있는 후렴구",
    "청량하고 희망찬": "맑은 음색, 상승하는 멜로디, 긍정적인 후렴구",
    "긴장감 있고 어두운": "낮은 음역, 불안정한 화성, 묵직한 베이스와 리듬",
    "귀엽고 사랑스러운": "통통 튀는 리듬, 밝은 악기 음색, 짧고 반복적인 훅",
}

LANGUAGE_GUIDES = {
    "한국어": "가사는 자연스러운 한국어로 작성하고, 발음하기 쉬운 문장과 기억하기 쉬운 후렴구를 사용한다.",
    "영어": "가사는 자연스러운 영어로 작성하고, 짧고 리듬감 있는 문장과 반복 가능한 훅을 사용한다.",
    "한국어 중심 + 영어 포인트": "가사는 한국어를 중심으로 작성하되, 후렴구나 핵심 표현에 짧은 영어 문구를 자연스럽게 넣는다.",
    "연주곡": "보컬과 가사 없이 악기만으로 감정과 장면을 표현한다.",
}


def clean_text(value, fallback):
    value = value.strip()
    return value if value else fallback


def make_prompt(
    concept,
    mood,
    genre,
    language,
    vocal,
    tempo,
    keywords,
    story,
    audience,
    duration,
    include_lyrics,
    include_notes,
):
    genre_info = GENRE_GUIDES[genre]
    mood_info = MOOD_DETAILS[mood]
    language_info = LANGUAGE_GUIDES[language]

    concept = clean_text(concept, "새로운 시작과 설렘")
    keywords = clean_text(keywords, "희망, 설렘, 성장")
    story = clean_text(
        story,
        "주인공이 어려움을 지나 자신의 가능성을 발견하고 한 걸음 앞으로 나아가는 이야기",
    )
    audience = clean_text(audience, "누구나 편안하게 들을 수 있는 대중")
    vocal_text = "보컬 없이 연주곡으로 구성" if language == "연주곡" else vocal
    tempo_text = genre_info["tempo"] if tempo == "장르에 맞게 자동" else tempo

    sections = [
        "[역할]",
        "당신은 대중음악 작곡가이자 작사가, 편곡가이다.",
        "",
        "[작곡 목표]",
        f"'{concept}'을 핵심 콘셉트로 하는 완성도 높은 {genre} 곡을 만든다.",
        f"곡의 전체 분위기는 '{mood}'이며, {mood_info}의 특징을 살린다.",
        f"주요 청자는 {audience}이다.",
        "",
        "[음악적 설정]",
        f"- 장르: {genre}",
        f"- 분위기: {mood}",
        f"- 템포: {tempo_text}",
        f"- 보컬: {vocal_text}",
        f"- 권장 악기: {genre_info['instruments']}",
        f"- 권장 구성: {genre_info['structure']}",
        f"- 예상 길이: 약 {duration}분",
        "- 멜로디는 한 번 들으면 기억할 수 있도록 명확한 핵심 동기를 만든다.",
        "- 후렴구는 가장 감정이 고조되며 반복해서 듣고 싶은 훅을 포함한다.",
        "- 각 구간이 자연스럽게 연결되도록 다이내믹과 악기 수를 단계적으로 변화시킨다.",
        "",
        "[가사 및 이야기]",
        f"- 핵심 이야기: {story}",
        f"- 반드시 반영할 키워드: {keywords}",
        f"- 언어 지침: {language_info}",
    ]

    if include_lyrics and language != "연주곡":
        sections.extend(
            [
                "- 가사는 Verse, Pre-Chorus, Chorus, Bridge 구분이 드러나도록 작성한다.",
                "- 추상적인 표현만 반복하지 말고 장면, 행동, 감정을 구체적으로 보여준다.",
                "- 후렴구에는 곡의 핵심 메시지를 담은 짧고 인상적인 문장을 반복한다.",
                "- 가창하기 어려운 지나치게 긴 문장은 피한다.",
            ]
        )
    elif language == "연주곡":
        sections.extend(
            [
                "- 가사를 작성하지 않는다.",
                "- 멜로디와 악기 변화만으로 이야기의 시작, 전개, 고조, 마무리를 표현한다.",
            ]
        )

    sections.extend(
        [
            "",
            "[출력 형식]",
            "1. 곡 제목 후보 3개",
            "2. 곡의 핵심 콘셉트 요약",
            "3. 장르, 분위기, 템포, 조성, 박자",
            "4. 사용 악기와 각 악기의 역할",
            "5. 전체 곡 구성과 구간별 분위기 변화",
        ]
    )

    if include_lyrics and language != "연주곡":
        sections.append("6. 구간 표시가 포함된 전체 가사")
        next_number = 7
    else:
        next_number = 6

    if include_notes:
        sections.extend(
            [
                f"{next_number}. 핵심 멜로디 가이드",
                "- 계이름 또는 음이름으로 4~8마디 분량의 메인 멜로디를 제시한다.",
                "- 예: C4, E4, G4처럼 옥타브를 포함한 음이름을 사용한다.",
                "- 각 음의 길이는 4분음표, 8분음표처럼 함께 표시한다.",
                "- 추천 코드 진행을 구간별로 제시한다.",
            ]
        )
        next_number += 1

    sections.extend(
        [
            f"{next_number}. 생성형 음악 도구에 입력할 수 있는 짧은 스타일 프롬프트",
            "",
            "[중요 조건]",
            "- 특정 가수나 기존 곡을 그대로 모방하지 않는다.",
            "- 기존 노래의 가사나 멜로디를 복제하지 않고 완전히 새롭게 만든다.",
            "- 결과물은 전체적으로 하나의 일관된 이야기와 음악적 색깔을 유지한다.",
        ]
    )

    return "\n".join(sections)


st.markdown(
    """
    <style>
    :root {
        --text-main: #2f3542;
        --text-sub: #5f6572;
        --pink: #e75480;
        --pink-deep: #cf3f72;
        --lavender: #7b70d6;
        --border: #efc2d4;
        --card: rgba(255, 255, 255, 0.96);
        --soft-yellow: #fff6d6;
    }

    html, body, .stApp {
        color: var(--text-main) !important;
    }

    .stApp {
        background:
            radial-gradient(circle at 12% 10%, rgba(255, 203, 224, 0.72), transparent 28%),
            radial-gradient(circle at 88% 8%, rgba(210, 211, 255, 0.70), transparent 28%),
            linear-gradient(180deg, #fff9fc 0%, #fff2f8 55%, #f8f7ff 100%);
    }

    .block-container {
        max-width: 920px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #6a3e56 !important;
        font-weight: 900 !important;
        letter-spacing: -0.025em;
    }

    p, label, li {
        color: var(--text-main) !important;
    }

    .hero {
        position: relative;
        overflow: hidden;
        text-align: center;
        padding: 2.5rem 1.3rem;
        border-radius: 30px;
        background: linear-gradient(135deg, rgba(255,255,255,0.97), rgba(255,247,252,0.97));
        border: 2px solid #f2bad0;
        box-shadow: 0 16px 42px rgba(172, 92, 139, 0.16);
        margin-bottom: 1.6rem;
    }

    .hero::before,
    .hero::after {
        content: "♪";
        position: absolute;
        font-size: 2.4rem;
        color: rgba(231, 84, 128, 0.22);
        animation: floatNote 4s ease-in-out infinite;
    }

    .hero::before {
        top: 18px;
        left: 28px;
    }

    .hero::after {
        content: "♫";
        right: 30px;
        bottom: 18px;
        animation-delay: 1.2s;
    }

    @keyframes floatNote {
        0%, 100% { transform: translateY(0) rotate(-5deg); }
        50% { transform: translateY(-10px) rotate(7deg); }
    }

    .hero-title {
        color: var(--pink-deep) !important;
        font-size: clamp(2.05rem, 6vw, 3.45rem);
        font-weight: 950;
        letter-spacing: -0.045em;
        text-shadow: 0 2px 0 rgba(255,255,255,0.8);
    }

    .hero-subtitle {
        color: #5b4f59 !important;
        line-height: 1.75;
        margin-top: 0.7rem;
        font-size: 1.02rem;
        font-weight: 650;
    }

    .tip {
        background: var(--soft-yellow);
        border: 1.5px dashed #d8aa36;
        color: #5e4812 !important;
        padding: 1rem 1.1rem;
        border-radius: 17px;
        line-height: 1.65;
        font-weight: 650;
        box-shadow: 0 6px 18px rgba(167, 129, 38, 0.08);
    }

    .tip * {
        color: #5e4812 !important;
    }

    /* 입력창 및 텍스트 영역 */
    div[data-testid="stTextInput"] input,
    div[data-testid="stTextArea"] textarea {
        background: #ffffff !important;
        color: #20242d !important;
        border: 2px solid var(--border) !important;
        border-radius: 15px !important;
        caret-color: var(--pink-deep) !important;
        box-shadow: 0 3px 10px rgba(123, 75, 101, 0.06);
    }

    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stTextArea"] textarea:focus {
        border-color: #df6f9b !important;
        box-shadow: 0 0 0 0.15rem rgba(223, 111, 155, 0.15) !important;
    }

    div[data-testid="stTextInput"] input::placeholder,
    div[data-testid="stTextArea"] textarea::placeholder {
        color: #8b8f99 !important;
        opacity: 1 !important;
    }

    /* selectbox */
    div[data-baseweb="select"] > div {
        background: #ffffff !important;
        color: #20242d !important;
        border: 2px solid var(--border) !important;
        border-radius: 15px !important;
        box-shadow: 0 3px 10px rgba(123, 75, 101, 0.06);
    }

    div[data-baseweb="select"] span,
    div[data-baseweb="select"] div {
        color: #20242d !important;
    }

    ul[role="listbox"] {
        background: #ffffff !important;
    }

    ul[role="listbox"] li,
    div[role="option"] {
        background: #ffffff !important;
        color: #20242d !important;
    }

    div[role="option"]:hover {
        background: #fff0f6 !important;
    }

    /* 숫자/슬라이더 */
    div[data-testid="stSlider"] * {
        color: #2f3542 !important;
    }

    div[data-baseweb="slider"] div[role="slider"] {
        background: var(--pink-deep) !important;
        border-color: var(--pink-deep) !important;
    }

    /* 체크박스 */
    div[data-testid="stCheckbox"] label,
    div[data-testid="stCheckbox"] span {
        color: #2f3542 !important;
        font-weight: 650;
    }

    /* 일반 버튼 */
    .stButton > button {
        width: 100%;
        border: none !important;
        border-radius: 16px !important;
        padding: 0.9rem 1rem !important;
        color: #ffffff !important;
        font-size: 1.07rem !important;
        font-weight: 900 !important;
        background: linear-gradient(90deg, #e95d91, #8175df) !important;
        box-shadow: 0 10px 24px rgba(159, 81, 145, 0.24) !important;
        transition: transform 0.18s ease, box-shadow 0.18s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        color: #ffffff !important;
        box-shadow: 0 13px 28px rgba(159, 81, 145, 0.30) !important;
    }

    .stButton > button * {
        color: #ffffff !important;
    }

    /* 다운로드 버튼 */
    .stDownloadButton > button {
        width: 100%;
        border: none !important;
        border-radius: 15px !important;
        background: linear-gradient(90deg, #6f67cf, #5b87d9) !important;
        color: #ffffff !important;
        font-weight: 850 !important;
        box-shadow: 0 8px 20px rgba(79, 91, 170, 0.20);
    }

    .stDownloadButton > button:hover {
        color: #ffffff !important;
        transform: translateY(-1px);
    }

    .stDownloadButton > button * {
        color: #ffffff !important;
    }

    /* 성공/경고 메시지 */
    div[data-testid="stAlert"] {
        border-radius: 16px !important;
        border: 1px solid #d8b548 !important;
        background: #fff8d9 !important;
    }

    div[data-testid="stAlert"] * {
        color: #554314 !important;
        font-weight: 650;
    }

    /* 결과 텍스트 영역 */
    div[data-testid="stTextArea"] textarea {
        line-height: 1.6 !important;
        font-size: 0.95rem !important;
    }

    /* 캡션 및 도움말 */
    div[data-testid="stCaptionContainer"],
    div[data-testid="InputInstructions"] {
        color: #616773 !important;
    }

    /* expander 및 기타 박스 */
    details {
        background: rgba(255, 255, 255, 0.92) !important;
        border: 1px solid #eac6d7 !important;
        border-radius: 15px !important;
    }

    /* 사이드바가 생길 경우 */
    section[data-testid="stSidebar"] {
        background: #fff5fa !important;
    }

    section[data-testid="stSidebar"] * {
        color: #2f3542 !important;
    }

    /* 하단 안내 문구 */
    .footer-note {
        text-align: center;
        color: #665d67 !important;
        font-size: 0.88rem;
        line-height: 1.65;
        margin-top: 2rem;
        font-weight: 600;
    }

    @media (max-width: 640px) {
        .block-container {
            padding-top: 1rem;
        }

        .hero {
            padding: 2rem 1rem;
            border-radius: 24px;
        }

        .hero-title {
            font-size: 2.15rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <div style="font-size:2.5rem;">🎵 💗 🎹</div>
        <div class="hero-title">멜로디 프롬프트 공방</div>
        <div class="hero-subtitle">
            노래의 콘셉트와 분위기를 입력하면<br>
            가사와 멜로디 생성을 위한 작곡 프롬프트를 만들어 드려요.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("### 🌷 1. 노래의 기본 설정")

concept = st.text_input(
    "노래의 콘셉트",
    placeholder="예: 시험을 마친 학생들의 자유와 설렘",
)

col1, col2 = st.columns(2)
with col1:
    genre = st.selectbox("장르", list(GENRE_GUIDES.keys()))
with col2:
    mood = st.selectbox("곡의 분위기", list(MOOD_DETAILS.keys()))

story = st.text_area(
    "노래에 담을 이야기",
    placeholder="예: 긴 시험 기간을 견딘 학생들이 교문을 나서며 친구들과 새로운 추억을 시작하는 이야기",
    height=110,
)

keywords = st.text_input(
    "꼭 포함하고 싶은 단어나 이미지",
    placeholder="예: 교문, 여름 바람, 운동장, 자유, 웃음",
)

st.markdown("### 🎤 2. 음악과 보컬 설정")

col3, col4 = st.columns(2)
with col3:
    language = st.selectbox(
        "가사 언어",
        ["한국어", "영어", "한국어 중심 + 영어 포인트", "연주곡"],
    )
with col4:
    vocal = st.selectbox(
        "보컬 스타일",
        [
            "맑고 청량한 여성 보컬",
            "따뜻하고 부드러운 여성 보컬",
            "힘 있고 시원한 여성 보컬",
            "맑고 청량한 남성 보컬",
            "따뜻하고 부드러운 남성 보컬",
            "힘 있고 깊은 남성 보컬",
            "남녀 혼성 보컬",
            "어린이 또는 청소년 합창",
            "랩 중심 보컬",
        ],
        disabled=language == "연주곡",
    )

col5, col6 = st.columns(2)
with col5:
    tempo = st.selectbox(
        "템포",
        [
            "장르에 맞게 자동",
            "느린 템포, 약 60~75 BPM",
            "중간 템포, 약 80~105 BPM",
            "경쾌한 템포, 약 110~125 BPM",
            "빠른 템포, 약 126~150 BPM",
        ],
    )
with col6:
    duration = st.slider("예상 곡 길이", 1.5, 5.0, 3.0, 0.5)

audience = st.text_input(
    "주요 청자",
    placeholder="예: 고등학생, 청소년, 가족, 일반 대중",
)

st.markdown("### ✨ 3. 생성 결과 설정")

col7, col8 = st.columns(2)
with col7:
    include_lyrics = st.checkbox(
        "전체 가사 생성 요청 포함",
        value=True,
        disabled=language == "연주곡",
    )
with col8:
    include_notes = st.checkbox(
        "음이름과 코드 진행 요청 포함",
        value=True,
    )

st.markdown(
    """
    <div class="tip">
        💡 완성된 프롬프트를 ChatGPT 같은 생성형 AI에 입력하면 가사, 곡 구성,
        코드 진행과 음이름을 만들 수 있어요. 음악 생성 도구에는 결과 중
        '짧은 스타일 프롬프트'를 활용하면 편리해요.
    </div>
    """,
    unsafe_allow_html=True,
)

generate = st.button("나만의 작곡 프롬프트 만들기 🎼")

if generate:
    prompt = make_prompt(
        concept=concept,
        mood=mood,
        genre=genre,
        language=language,
        vocal=vocal,
        tempo=tempo,
        keywords=keywords,
        story=story,
        audience=audience,
        duration=duration,
        include_lyrics=include_lyrics,
        include_notes=include_notes,
    )

    st.success("작곡 프롬프트가 완성되었습니다! 아래 내용을 복사해 사용해 보세요. 💕")
    st.text_area(
        "생성된 프롬프트",
        value=prompt,
        height=650,
    )

    st.download_button(
        "프롬프트를 TXT 파일로 저장하기 📥",
        data=prompt,
        file_name="music_generation_prompt.txt",
        mime="text/plain",
        use_container_width=True,
    )

st.markdown(
    """
    <div class="footer-note">
        생성형 AI의 결과는 도구마다 달라질 수 있어요.<br>
        특정 가수나 기존 노래를 그대로 모방하기보다 나만의 이야기와 분위기를 만들어 보세요.
    </div>
    """,
    unsafe_allow_html=True,
)
