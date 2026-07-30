import streamlit as st


# =========================================================
# 1. 페이지 설정
# =========================================================
st.set_page_config(
    page_title="Suno 음악 프롬프트 생성기",
    page_icon="🎵",
    layout="wide",
)


# =========================================================
# 2. 선택 항목
# =========================================================
GENRES = {
    "K-POP": "modern K-pop",
    "발라드": "emotional pop ballad",
    "힙합": "modern hip-hop",
    "R&B": "contemporary R&B",
    "록": "modern rock",
    "인디 팝": "indie pop",
    "시티 팝": "retro city pop",
    "EDM": "electronic dance music",
    "재즈": "modern jazz",
    "어쿠스틱 팝": "acoustic pop",
    "포크": "folk pop",
    "펑크 록": "pop punk",
    "메탈": "modern metal",
    "트로트": "Korean trot",
    "로파이": "lo-fi chill",
    "영화 OST": "cinematic soundtrack",
    "애니메이션 OST": "anime-inspired soundtrack",
    "게임 BGM": "video game soundtrack",
}

MOODS = {
    "밝고 신나는": "bright, energetic, uplifting",
    "따뜻하고 포근한": "warm, gentle, comforting",
    "감성적이고 아련한": "emotional, nostalgic, bittersweet",
    "몽환적인": "dreamy, ethereal, atmospheric",
    "강렬하고 웅장한": "powerful, epic, dramatic",
    "차분하고 편안한": "calm, peaceful, relaxing",
    "슬프고 애절한": "sad, heartfelt, deeply emotional",
    "청량하고 희망찬": "refreshing, hopeful, youthful",
    "긴장감 있고 어두운": "dark, tense, mysterious",
    "귀엽고 사랑스러운": "cute, playful, lovely",
    "세련되고 도시적인": "stylish, sleek, urban",
    "자유롭고 반항적인": "free-spirited, rebellious, bold",
}

TEMPOS = {
    "매우 느리게 (50~65 BPM)": "very slow tempo, around 50-65 BPM",
    "느리게 (66~80 BPM)": "slow tempo, around 66-80 BPM",
    "보통 (81~105 BPM)": "mid-tempo, around 81-105 BPM",
    "경쾌하게 (106~125 BPM)": "upbeat tempo, around 106-125 BPM",
    "빠르게 (126~145 BPM)": "fast tempo, around 126-145 BPM",
    "매우 빠르게 (146 BPM 이상)": "very fast tempo, above 146 BPM",
}

VOCALS = {
    "맑고 청량한 여성 보컬": "clear and refreshing female vocal",
    "따뜻하고 부드러운 여성 보컬": "warm and gentle female vocal",
    "힘 있고 시원한 여성 보컬": "powerful and soaring female vocal",
    "몽환적인 여성 보컬": "dreamy and airy female vocal",
    "맑고 청량한 남성 보컬": "clear and refreshing male vocal",
    "따뜻하고 부드러운 남성 보컬": "warm and gentle male vocal",
    "힘 있고 깊은 남성 보컬": "powerful and deep male vocal",
    "감성적인 남성 보컬": "emotional male vocal",
    "남녀 듀엣": "male and female duet vocals",
    "그룹 보컬": "layered group vocals",
    "랩 중심": "rhythmic rap-focused vocal",
    "보컬 없는 연주곡": "instrumental, no vocals",
}

INSTRUMENTS = {
    "피아노": "piano",
    "어쿠스틱 기타": "acoustic guitar",
    "일렉트릭 기타": "electric guitar",
    "베이스 기타": "bass guitar",
    "드럼": "live drums",
    "전자 드럼": "electronic drums",
    "스트링": "cinematic strings",
    "신시사이저": "synthesizers",
    "브라스": "brass section",
    "색소폰": "saxophone",
    "플루트": "flute",
    "808 베이스": "808 bass",
    "오케스트라": "full orchestra",
    "국악기": "Korean traditional instruments",
}

STRUCTURES = {
    "대중적인 구성": (
        "intro, verse, pre-chorus, chorus, verse, chorus, "
        "bridge, final chorus, outro"
    ),
    "후렴 중심 구성": (
        "short intro, verse, pre-chorus, big chorus, verse, "
        "chorus, bridge, repeated final chorus"
    ),
    "서사적인 구성": (
        "atmospheric intro, verse, gradual build, chorus, "
        "second verse, dramatic bridge, climactic final chorus, outro"
    ),
    "짧고 강한 구성": (
        "short intro, verse, chorus, verse, chorus, brief bridge, final chorus"
    ),
    "랩 중심 구성": (
        "intro, rap verse, hook, rap verse, hook, bridge, final hook"
    ),
    "연주곡 구성": (
        "intro, theme A, development, theme B, climax, reprise, outro"
    ),
}

LANGUAGES = [
    "한국어",
    "한국어 중심 + 영어 포인트",
    "영어",
    "가사 없는 연주곡",
]


# =========================================================
# 3. 프롬프트 생성 함수
# =========================================================
def use_default(text: str, default: str) -> str:
    """입력칸이 비어 있을 때 사용할 기본 문장을 반환합니다."""
    cleaned = text.strip()
    return cleaned if cleaned else default


def create_suno_prompt(
    genre: str,
    mood: str,
    tempo: str,
    vocal: str,
    instruments: list[str],
    structure: str,
    concept: str,
    production: str,
    era: str,
    extra_style: str,
) -> str:
    """Suno의 Style of Music 입력란에 사용할 영어 프롬프트를 만듭니다."""
    parts = [
        GENRES[genre],
        MOODS[mood],
        TEMPOS[tempo],
        VOCALS[vocal],
    ]

    if instruments:
        translated_instruments = ", ".join(
            INSTRUMENTS[instrument] for instrument in instruments
        )
        parts.append(f"featuring {translated_instruments}")

    parts.extend(
        [
            f"song structure: {STRUCTURES[structure]}",
            f"concept: {concept}",
            f"production style: {production}",
            f"era and texture: {era}",
            "memorable melodic hook",
            "clear emotional progression",
            "polished and balanced mix",
            "original composition",
        ]
    )

    if extra_style.strip():
        parts.append(extra_style.strip())

    return ", ".join(parts)


def create_lyrics_prompt(
    concept: str,
    story: str,
    keywords: str,
    message: str,
    genre: str,
    mood: str,
    tempo: str,
    vocal: str,
    structure: str,
    language: str,
    title_style: str,
    rhyme: str,
    repetition: str,
) -> str:
    """생성형 AI에 넣어 가사를 만들 수 있는 한국어 프롬프트를 만듭니다."""
    if language == "가사 없는 연주곡":
        return f"""당신은 전문 작곡가이자 편곡가입니다.

다음 조건을 반영하여 Suno에서 사용할 가사 없는 연주곡 구성안을 작성해 주세요.

[곡의 설정]
- 핵심 콘셉트: {concept}
- 이야기 또는 장면: {story}
- 장르: {genre}
- 분위기: {mood}
- 템포: {tempo}
- 핵심 메시지: {message}
- 핵심 이미지와 키워드: {keywords}
- 곡 구성: {structure}

[작성 조건]
1. 가사는 작성하지 않습니다.
2. 인트로부터 아웃트로까지 구간별 장면과 감정 변화를 설명합니다.
3. 각 구간에서 중심이 되는 악기와 멜로디의 특징을 제시합니다.
4. 곡 전체에 반복되는 핵심 멜로디 모티프를 설명합니다.
5. 후반부로 갈수록 감정이 자연스럽게 고조되도록 구성합니다.
6. 특정 음악가나 기존 곡을 모방하지 않고 독창적으로 작성합니다.

[출력 형식]
1. 제목 후보 3개
2. 곡의 한 문장 소개
3. 구간별 구성과 분위기
4. 핵심 멜로디 아이디어
5. 추천 악기와 역할
6. Suno에 넣을 수 있는 연주곡 설명 요약"""

    language_rule = {
        "한국어": "모든 가사를 자연스러운 한국어로 작성합니다.",
        "한국어 중심 + 영어 포인트": (
            "한국어를 중심으로 작성하되 후렴의 핵심 부분에 "
            "짧고 기억하기 쉬운 영어 표현을 자연스럽게 넣습니다."
        ),
        "영어": (
            "가사는 영어로 작성하되 제목 후보와 설명은 한국어로 작성합니다."
        ),
    }[language]

    return f"""당신은 대중음악 전문 작사가입니다.
아래 조건을 모두 반영하여 Suno에 입력할 수 있는 완성형 노래 가사를 작성해 주세요.

[곡의 기본 설정]
- 핵심 콘셉트: {concept}
- 담고 싶은 이야기: {story}
- 장르: {genre}
- 분위기: {mood}
- 템포: {tempo}
- 보컬 스타일: {vocal}
- 가사 언어: {language}
- 핵심 메시지: {message}
- 꼭 포함할 단어와 이미지: {keywords}
- 제목의 느낌: {title_style}
- 곡 구성: {structure}

[가사 작성 원칙]
1. {language_rule}
2. 전체 가사에 하나의 일관된 이야기와 감정 흐름이 있어야 합니다.
3. 감정만 나열하지 말고 인물의 행동, 장소, 시간, 장면을 구체적으로 보여 주세요.
4. Verse에서는 상황과 이야기를 전개합니다.
5. Pre-Chorus에서는 긴장과 기대를 높입니다.
6. Chorus에는 핵심 메시지를 담은 짧고 강한 훅을 넣습니다.
7. Bridge에서는 새로운 관점이나 감정의 전환을 보여 줍니다.
8. 한 줄이 지나치게 길지 않도록 노래하기 쉬운 길이로 작성합니다.
9. 운율과 라임은 '{rhyme}' 수준으로 구성합니다.
10. 후렴 반복은 '{repetition}' 수준으로 구성합니다.
11. 특정 가수나 기존 노래를 모방하지 않고 완전히 새롭게 작성합니다.

[출력 형식]
1. 곡 제목 후보 3개
2. 곡의 핵심 메시지 한 문장
3. 다음 구간 태그를 사용한 전체 가사
   [Intro]
   [Verse 1]
   [Pre-Chorus]
   [Chorus]
   [Verse 2]
   [Pre-Chorus]
   [Chorus]
   [Bridge]
   [Final Chorus]
   [Outro]
4. 가사에서 가장 중요한 한 줄
5. Suno의 Lyrics 입력란에 붙여 넣을 수 있도록 가사 부분만 다시 정리"""


# =========================================================
# 4. 화면 디자인
# =========================================================
st.markdown(
    """
    <style>
    :root {
        --main-text: #253047;
        --sub-text: #59657a;
        --pink: #cf467d;
        --purple: #6e62c9;
        --border: #e7c3d3;
    }

    .stApp {
        background:
            radial-gradient(circle at 10% 7%, rgba(255, 206, 226, 0.75), transparent 28%),
            radial-gradient(circle at 90% 5%, rgba(213, 215, 255, 0.75), transparent 28%),
            linear-gradient(180deg, #fff9fc 0%, #f6f6ff 100%);
        color: var(--main-text);
    }

    .block-container {
        max-width: 1160px;
        padding-top: 1.6rem;
        padding-bottom: 4rem;
    }

    .hero {
        text-align: center;
        padding: 2.25rem 1.1rem;
        margin-bottom: 1.4rem;
        border: 2px solid #efbdd1;
        border-radius: 28px;
        background: rgba(255, 255, 255, 0.96);
        box-shadow: 0 15px 38px rgba(104, 74, 113, 0.14);
    }

    .hero-title {
        color: #c83e75 !important;
        font-size: clamp(2rem, 5vw, 3.25rem);
        font-weight: 950;
        letter-spacing: -0.045em;
    }

    .hero-subtitle {
        color: #4d586c !important;
        margin-top: 0.7rem;
        line-height: 1.75;
        font-weight: 650;
    }

    h1, h2, h3, h4 {
        color: #5e4052 !important;
    }

    p, label, li {
        color: var(--main-text) !important;
    }

    div[data-testid="stTextInput"] input,
    div[data-testid="stTextArea"] textarea {
        color: #202632 !important;
        background: #ffffff !important;
        border: 2px solid var(--border) !important;
        border-radius: 14px !important;
        caret-color: var(--pink) !important;
    }

    div[data-testid="stTextInput"] input::placeholder,
    div[data-testid="stTextArea"] textarea::placeholder {
        color: #858b98 !important;
        opacity: 1 !important;
    }

    div[data-baseweb="select"] > div {
        color: #202632 !important;
        background: #ffffff !important;
        border: 2px solid var(--border) !important;
        border-radius: 14px !important;
    }

    div[data-baseweb="select"] span,
    div[data-baseweb="select"] div,
    ul[role="listbox"],
    div[role="option"] {
        color: #202632 !important;
    }

    ul[role="listbox"],
    div[role="option"] {
        background: #ffffff !important;
    }

    div[role="option"]:hover {
        background: #fff0f6 !important;
    }

    div[data-testid="stRadio"] label,
    div[data-testid="stRadio"] span,
    div[data-testid="stCheckbox"] label,
    div[data-testid="stCheckbox"] span {
        color: #283142 !important;
    }

    .stButton > button {
        width: 100%;
        padding: 0.88rem 1rem;
        border: none !important;
        border-radius: 15px !important;
        color: #ffffff !important;
        font-size: 1.06rem;
        font-weight: 900;
        background: linear-gradient(90deg, #dc568b, #7064cf) !important;
        box-shadow: 0 9px 23px rgba(117, 76, 142, 0.24);
    }

    .stButton > button:hover {
        color: #ffffff !important;
        transform: translateY(-1px);
    }

    .stButton > button * {
        color: #ffffff !important;
    }

    .stDownloadButton > button {
        width: 100%;
        border: none !important;
        border-radius: 14px !important;
        color: #ffffff !important;
        background: #6676c6 !important;
        font-weight: 800;
    }

    .stDownloadButton > button * {
        color: #ffffff !important;
    }

    .guide {
        margin: 1rem 0;
        padding: 1rem 1.1rem;
        border: 1px solid #d8bd58;
        border-radius: 15px;
        background: #fff8d8;
        color: #554415 !important;
        line-height: 1.7;
        font-weight: 620;
    }

    div[data-testid="stTabs"] button {
        color: #465168 !important;
        font-weight: 800;
    }

    div[data-testid="stTabs"] button[aria-selected="true"] {
        color: #c83e75 !important;
    }

    @media (max-width: 700px) {
        .block-container {
            padding-top: 1rem;
        }

        .hero {
            padding: 1.8rem 0.9rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 5. 화면 구성
# =========================================================
st.markdown(
    """
    <div class="hero">
        <div style="font-size:2.4rem;">🎵 ✨ 🎤</div>
        <div class="hero-title">Suno 음악 프롬프트 생성기</div>
        <div class="hero-subtitle">
            원하는 음악 스타일을 선택하면<br>
            Suno용 영어 프롬프트와 가사 생성용 한국어 프롬프트를 만들어 드립니다.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("## 1. 노래의 주제")

concept = st.text_input(
    "노래의 핵심 콘셉트",
    placeholder="예: 시험이 끝난 뒤 친구들과 맞이하는 자유로운 여름",
)

story = st.text_area(
    "노래에 담을 이야기",
    placeholder=(
        "예: 긴 시험 기간을 견딘 학생들이 교문을 나서며 "
        "친구들과 새로운 추억을 시작하는 이야기"
    ),
    height=120,
)

col1, col2 = st.columns(2)

with col1:
    keywords = st.text_input(
        "꼭 포함하고 싶은 단어 또는 이미지",
        placeholder="예: 여름 바람, 교문, 운동장, 노을, 웃음",
    )

with col2:
    message = st.text_input(
        "노래가 전할 핵심 메시지",
        placeholder="예: 힘든 시간이 지나면 새로운 시작이 찾아온다",
    )

st.markdown("## 2. 음악 스타일")

col3, col4, col5 = st.columns(3)

with col3:
    genre = st.selectbox("장르", list(GENRES.keys()))

with col4:
    mood = st.selectbox("분위기", list(MOODS.keys()))

with col5:
    tempo = st.selectbox("템포", list(TEMPOS.keys()), index=2)

col6, col7 = st.columns(2)

with col6:
    vocal = st.selectbox("보컬 스타일", list(VOCALS.keys()))

with col7:
    structure = st.selectbox("곡 구성", list(STRUCTURES.keys()))

instruments = st.multiselect(
    "중심 악기",
    list(INSTRUMENTS.keys()),
    default=["피아노", "신시사이저", "드럼"],
    help="여러 악기를 선택할 수 있습니다.",
)

col8, col9 = st.columns(2)

with col8:
    production = st.selectbox(
        "프로덕션 스타일",
        [
            "clean and polished studio production",
            "warm analog texture",
            "wide cinematic sound",
            "minimal and intimate production",
            "punchy and energetic production",
            "spacious and atmospheric production",
        ],
    )

with col9:
    era = st.selectbox(
        "시대와 질감",
        [
            "modern and contemporary",
            "retro 1980s-inspired",
            "nostalgic 1990s-inspired",
            "early 2000s pop-inspired",
            "timeless and classic",
            "futuristic and experimental",
        ],
    )

extra_style = st.text_input(
    "추가 음악 스타일",
    placeholder="예: explosive final chorus, soft piano intro, layered harmonies",
)

st.markdown("## 3. 가사 설정")

col10, col11, col12 = st.columns(3)

with col10:
    language = st.selectbox("가사 언어", LANGUAGES)

with col11:
    rhyme = st.selectbox(
        "운율과 라임",
        ["자연스럽게", "약하게", "적당히", "강하게"],
    )

with col12:
    repetition = st.selectbox(
        "후렴 반복",
        ["적당히", "적게", "강하게"],
    )

title_style = st.text_input(
    "제목의 느낌",
    placeholder="예: 짧고 시적인 제목, 청춘 영화 같은 제목",
)

st.markdown(
    """
    <div class="guide">
        💡 <b>사용 방법</b><br>
        영어 프롬프트는 Suno의 <b>Style of Music</b> 입력란에 붙여 넣습니다.<br>
        한국어 프롬프트는 ChatGPT와 같은 생성형 AI에 입력해 가사를 만든 뒤,
        완성된 가사를 Suno의 <b>Lyrics</b> 입력란에 붙여 넣습니다.
    </div>
    """,
    unsafe_allow_html=True,
)

if st.button("프롬프트 만들기 🎼"):
    concept_value = use_default(
        concept,
        "a hopeful story about a new beginning",
    )
    story_value = use_default(
        story,
        "어려운 시간을 지나 새로운 시작을 맞이하는 사람의 이야기",
    )
    keywords_value = use_default(
        keywords,
        "빛, 바람, 새로운 시작, 희망",
    )
    message_value = use_default(
        message,
        "어려움을 지나면 다시 시작할 수 있다",
    )
    title_value = use_default(
        title_style,
        "짧고 기억하기 쉬우며 곡의 이미지를 담은 제목",
    )

    suno_prompt = create_suno_prompt(
        genre=genre,
        mood=mood,
        tempo=tempo,
        vocal=vocal,
        instruments=instruments,
        structure=structure,
        concept=concept_value,
        production=production,
        era=era,
        extra_style=extra_style,
    )

    lyrics_prompt = create_lyrics_prompt(
        concept=concept_value,
        story=story_value,
        keywords=keywords_value,
        message=message_value,
        genre=genre,
        mood=mood,
        tempo=tempo,
        vocal=vocal,
        structure=structure,
        language=language,
        title_style=title_value,
        rhyme=rhyme,
        repetition=repetition,
    )

    st.success("프롬프트가 완성되었습니다.")

    tab1, tab2 = st.tabs(
        [
            "🎧 Suno 영어 프롬프트",
            "✍️ 가사 생성 한국어 프롬프트",
        ]
    )

    with tab1:
        st.markdown("### Suno Style of Music 프롬프트")
        st.text_area(
            "영어 프롬프트",
            value=suno_prompt,
            height=270,
        )

        st.download_button(
            "영어 프롬프트 저장",
            data=suno_prompt,
            file_name="suno_style_prompt.txt",
            mime="text/plain",
            use_container_width=True,
        )

    with tab2:
        st.markdown("### 가사 생성용 한국어 프롬프트")
        st.text_area(
            "한국어 프롬프트",
            value=lyrics_prompt,
            height=650,
        )

        st.download_button(
            "한국어 프롬프트 저장",
            data=lyrics_prompt,
            file_name="lyrics_prompt.txt",
            mime="text/plain",
            use_container_width=True,
        )

    combined = (
        "[SUNO STYLE PROMPT]\n"
        + suno_prompt
        + "\n\n"
        + "[가사 생성 프롬프트]\n"
        + lyrics_prompt
    )

    st.download_button(
        "두 프롬프트를 한 파일로 저장",
        data=combined,
        file_name="suno_prompt_package.txt",
        mime="text/plain",
        use_container_width=True,
    )

st.markdown("---")
st.caption(
    "특정 가수나 기존 노래를 그대로 모방하지 않고 음악적 특징을 조합해 "
    "새로운 곡을 만들 수 있도록 설계된 웹앱입니다."
)
