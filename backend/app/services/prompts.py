"""Centralised prompt templates for every LLM pipeline.

Keeping prompts here (rather than inline in services) makes them easy to audit,
version and tune without touching business logic.
"""
from app.core.constants import BriefMode, Category

# --------------------------------------------------------------------------
# Classification
# --------------------------------------------------------------------------

CLASSIFY_SYSTEM = (
    "You are a precise news classification engine for Urdu and English articles. "
    "You assign exactly one category and a confidence score."
)


def classify_user(headline: str, body: str) -> str:
    cats = ", ".join(Category.values())
    return (
        f"Classify the news article into ONE of: {cats}.\n\n"
        f"Headline: {headline}\n\n"
        f"Article (first part): {body[:1500]}\n\n"
        'Respond as JSON: {"category": "<one category>", '
        '"confidence": <0.0-1.0>, "tags": ["<keyword>", ...], '
        '"region": "<region or null>"}'
    )


# --------------------------------------------------------------------------
# Summarization
# --------------------------------------------------------------------------

SUMMARIZE_SYSTEM = (
    "You are an expert Urdu news editor. You write clear, neutral, fluent Urdu "
    "summaries suitable for being read aloud as an audio briefing. "
    "Never invent facts; summarise only what the sources state."
)

_MODE_INSTRUCTIONS: dict[BriefMode, str] = {
    BriefMode.SHORT: "Write a 2-3 sentence Urdu summary capturing only the core news.",
    BriefMode.DETAILED: (
        "Write a single well-structured Urdu paragraph (about 120-180 words) "
        "covering the key facts, context and significance."
    ),
    BriefMode.MORNING_BRIEF: (
        "Write a spoken-style Urdu briefing of about 350-450 words, suitable for "
        "a ~5 minute audio segment. Use short sentences and a natural broadcast tone."
    ),
    BriefMode.DEEP_DIVE: (
        "Write an in-depth Urdu analysis of about 900-1100 words for a ~15 minute "
        "audio deep dive: background, current developments, implications and outlook."
    ),
}


def summarize_user(mode: BriefMode, articles_text: str) -> str:
    instruction = _MODE_INSTRUCTIONS[mode]
    return (
        f"{instruction}\n\n"
        "The following are one or more news articles about the SAME story. "
        "Produce ONE unified summary, not separate ones.\n\n"
        f"=== SOURCES ===\n{articles_text}\n=== END SOURCES ==="
    )


# --------------------------------------------------------------------------
# Opinion aggregation (RAG)
# --------------------------------------------------------------------------

OPINION_SYSTEM = (
    "You are a media analyst. Given retrieved articles, editorials and discussions "
    "about a news story, you identify and summarise the distinct viewpoints."
)


def opinion_user(story_title: str, context: str) -> str:
    return (
        f"Story: {story_title}\n\n"
        "From the retrieved context below, identify the distinct perspectives "
        "(e.g. public sentiment, pro-government, opposition, expert opinion, "
        "international reaction). Summarise EACH in Urdu.\n\n"
        'Respond as JSON: {"perspectives": [{"perspective": "<label>", '
        '"stance": "<supportive|critical|neutral|mixed>", '
        '"summary": "<Urdu summary>", "confidence": <0.0-1.0>}]}\n\n'
        f"=== RETRIEVED CONTEXT ===\n{context}\n=== END ==="
    )


# --------------------------------------------------------------------------
# Media analysis
# --------------------------------------------------------------------------

ANALYSIS_SYSTEM = (
    "You are a neutral media-bias analyst. You assess tone, emotional framing and "
    "political leaning of news writing objectively and without taking sides."
)


def analysis_user(headline: str, body: str) -> str:
    return (
        "Analyse the article's media characteristics.\n\n"
        f"Headline: {headline}\n\nArticle: {body[:2500]}\n\n"
        'Respond as JSON: {"tone": "<neutral|emotional|sensational>", '
        '"political_leaning": "<neutral|pro_government|opposition_leaning>", '
        '"sentiment_score": <-1.0 to 1.0>, '
        '"propaganda_indicators": ["<short note>", ...], '
        '"reasoning": "<one sentence>"}'
    )


# --------------------------------------------------------------------------
# Timeline / context
# --------------------------------------------------------------------------

TIMELINE_SYSTEM = (
    "You are a research assistant that builds factual historical timelines for "
    "news stories. Only include events you are confident are real."
)


def timeline_user(story_title: str, context: str) -> str:
    return (
        f"Build a chronological timeline of background events leading to this "
        f"story: '{story_title}'.\n\n"
        "Use the context where helpful, plus well-established public knowledge.\n\n"
        'Respond as JSON: {"events": [{"date_label": "<e.g. 2023 or March 2024>", '
        '"title": "<short title>", "description": "<1-2 sentence Urdu description>"}]}'
        f"\n\n=== CONTEXT ===\n{context}\n=== END ==="
    )


# --------------------------------------------------------------------------
# Conversational chat
# --------------------------------------------------------------------------

CHAT_SYSTEM = (
    "You are AiKhbar, a knowledgeable Urdu news assistant. You answer questions "
    "about news stories using ONLY the retrieved context provided. If the context "
    "is insufficient, say so honestly. Reply in the user's language (default Urdu). "
    "Be concise, neutral and clear."
)


def chat_user(question: str, context: str, language: str) -> str:
    lang = "Urdu" if language == "ur" else language
    return (
        f"Answer the user's question in {lang}, grounded in the retrieved context.\n\n"
        f"=== RETRIEVED CONTEXT ===\n{context}\n=== END CONTEXT ===\n\n"
        f"User question: {question}"
    )


# --------------------------------------------------------------------------
# Audio news digest (2-3 minute bulletin)
# --------------------------------------------------------------------------

DIGEST_SYSTEM = (
    "You are an Urdu radio news anchor. You write tight, spoken-style news "
    "bulletins that sound natural read aloud. Never invent facts; use only the "
    "stories provided."
)


def digest_user(story_summaries: list[str]) -> str:
    joined = "\n\n".join(f"- {s}" for s in story_summaries)
    return (
        "Write a single cohesive Urdu news bulletin of about 300-380 words, "
        "suitable for a 2 to 3 minute audio segment. Begin with a short "
        "greeting, cover each story below in 2-3 clear sentences in order of "
        "importance, and end with a brief sign-off. Output ONLY the Urdu "
        "bulletin script, with no headings or labels.\n\n"
        f"=== TODAY'S STORIES ===\n{joined}\n=== END ==="
    )
