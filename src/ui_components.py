"""Streamlit UI components with BookBuddy gradient theme styling."""

from __future__ import annotations

from typing import Any

import streamlit as st

# ── Color Palette ──────────────────────────────────────────────────────────
GR_BROWN: str = "#8B4513"
GR_GOLD: str = "#B8860B"
CLAUDE_PURPLE: str = "#663399"
CLAUDE_BLUE: str = "#16213E"
CARD_DARK: str = "#1A1A2E"
TEXT_LIGHT: str = "#F0E6D2"
TEXT_MUTED: str = "#A0907A"


# ── CSS Injection ──────────────────────────────────────────────────────────


def inject_custom_css() -> None:
    """Inject the BookBuddy gradient CSS theme into the Streamlit app."""
    st.markdown(
        f"""
        <style>
        /* ── Global Background ── */
        .stApp {{
            background: linear-gradient(160deg, {CARD_DARK} 0%, {CLAUDE_BLUE} 40%, #1a1020 100%);
        }}

        /* ── Header Gradient ── */
        .bookbuddy-header {{
            background: linear-gradient(135deg, {CLAUDE_PURPLE} 0%, {GR_GOLD} 60%, {GR_BROWN} 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 3rem;
            font-weight: 800;
            text-align: center;
            margin-bottom: 0.5rem;
        }}

        .bookbuddy-subtitle {{
            color: {TEXT_MUTED};
            text-align: center;
            font-size: 1.05rem;
            margin-bottom: 2rem;
            font-style: italic;
        }}

        /* ── Stat Metric Cards ── */
        .stat-row {{
            display: flex;
            gap: 1rem;
            justify-content: center;
            flex-wrap: wrap;
            margin: 1.5rem 0;
        }}
        .stat-card {{
            background: linear-gradient(145deg, rgba(26,26,46,0.9) 0%, rgba(22,33,62,0.8) 100%);
            border: 1px solid rgba({GR_GOLD.replace('#','')},0.2);
            border-radius: 16px;
            padding: 1.2rem 1.5rem;
            text-align: center;
            min-width: 130px;
            backdrop-filter: blur(10px);
        }}
        .stat-card .stat-value {{
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, {GR_GOLD} 0%, {CLAUDE_PURPLE} 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .stat-card .stat-label {{
            color: {TEXT_MUTED};
            font-size: 0.85rem;
            margin-top: 0.3rem;
        }}

        /* ── Reader DNA Card ── */
        .dna-card {{
            background: linear-gradient(145deg, rgba(26,26,46,0.95) 0%, rgba(102,51,153,0.15) 100%);
            border: 1px solid rgba(102,51,153,0.4);
            border-radius: 20px;
            padding: 2rem;
            margin: 1.5rem 0;
            position: relative;
            overflow: hidden;
        }}
        .dna-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, {CLAUDE_PURPLE}, {GR_GOLD}, {GR_BROWN});
            border-radius: 3px 3px 0 0;
        }}
        .dna-label {{
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.15em;
            color: {GR_GOLD};
            margin-bottom: 0.5rem;
            font-weight: 600;
        }}
        .dna-text {{
            color: {TEXT_LIGHT};
            font-size: 1.05rem;
            line-height: 1.8;
            font-style: italic;
        }}

        /* ── Recommendation Cards ── */
        .rec-card {{
            background: linear-gradient(145deg, rgba(26,26,46,0.9) 0%, rgba(139,69,19,0.1) 100%);
            border: 1px solid rgba({GR_BROWN.replace('#','')},0.25);
            border-radius: 16px;
            padding: 1.5rem;
            margin: 1rem 0;
            position: relative;
        }}
        .rec-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: linear-gradient(180deg, {GR_GOLD}, {CLAUDE_PURPLE});
            border-radius: 0 16px 16px 0;
        }}
        .rec-number {{
            font-size: 0.75rem;
            color: {GR_GOLD};
            text-transform: uppercase;
            letter-spacing: 0.1em;
            font-weight: 700;
        }}
        .rec-title {{
            color: {TEXT_LIGHT};
            font-size: 1.15rem;
            font-weight: 700;
            margin: 0.3rem 0;
        }}
        .rec-reason {{
            color: {TEXT_MUTED};
            font-size: 0.95rem;
            line-height: 1.6;
        }}

        /* ── Sidebar styling ── */
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {CARD_DARK} 0%, rgba(22,33,62,0.95) 100%);
            border-right: 1px solid rgba({GR_GOLD.replace('#','')},0.15);
        }}

        /* ── Tab styling ── */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 1rem;
        }}
        .stTabs [data-baseweb="tab"] {{
            background: transparent;
            color: {TEXT_MUTED};
            border-radius: 8px 8px 0 0;
        }}
        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, rgba(102,51,153,0.2) 0%, rgba(184,134,11,0.15) 100%) !important;
            color: {GR_GOLD} !important;
        }}

        /* ── Button styling ── */
        .stButton > button {{
            background: linear-gradient(135deg, {CLAUDE_PURPLE} 0%, {GR_GOLD} 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1.5rem;
            font-weight: 600;
            transition: opacity 0.2s;
        }}
        .stButton > button:hover {{
            opacity: 0.9;
        }}

        /* ── File uploader ── */
        .stFileUploader {{
            background: transparent;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ── Renderers ──────────────────────────────────────────────────────────────


def render_header() -> None:
    """Render the BookBuddy app header with gradient title."""
    st.markdown(
        """
        <h1 class="bookbuddy-header">BookBuddy</h1>
        <p class="bookbuddy-subtitle">
            📖 Upload your Goodreads library export and let AI decode your reading DNA
        </p>
        """,
        unsafe_allow_html=True,
    )


def render_stat_cards(
    total_books: int,
    total_pages: int,
    avg_rating: float,
) -> None:
    """Render a row of stat metric cards.

    Args:
        total_books: Total rated books read.
        total_pages: Estimated total pages.
        avg_rating: Average rating (0.0–5.0).
    """
    st.markdown(
        f"""
        <div class="stat-row">
            <div class="stat-card">
                <div class="stat-value">{total_books:,}</div>
                <div class="stat-label">📚 Books Read</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{total_pages:,}</div>
                <div class="stat-label">📄 Pages Turned</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{avg_rating:.1f}</div>
                <div class="stat-label">⭐ Avg Rating</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_reader_dna(dna_text: str) -> None:
    """Render the AI-generated Reader DNA in a styled card.

    Args:
        dna_text: The ~150-word Reader DNA paragraph from the LLM.
    """
    st.markdown(
        f"""
        <div class="dna-card">
            <div class="dna-label">🧬 Your Reader DNA</div>
            <p class="dna-text">{dna_text}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_recommendation_card(
    number: int,
    title: str,
    author: str,
    reason: str,
) -> None:
    """Render a single recommendation card.

    Args:
        number: Recommendation ordinal (1–5).
        title: Book title.
        author: Author name.
        reason: 2-sentence reason tied to the reader's taste.
    """
    st.markdown(
        f"""
        <div class="rec-card">
            <div class="rec-number">📖 RECOMMENDATION #{number}</div>
            <div class="rec-title">
                {title}<span style="font-weight:400;color:{TEXT_MUTED}"> by {author}</span>
            </div>
            <p class="rec-reason">{reason}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Markdown Export ────────────────────────────────────────────────────────


def build_markdown_export(reader_dna: str, recommendations_text: str) -> str:
    """Build a Markdown string for exporting DNA + recommendations.

    Args:
        reader_dna: The generated Reader DNA paragraph.
        recommendations_text: Raw recommendations from the LLM.

    Returns:
        Formatted Markdown string.
    """
    return f"""# 📚 BookBuddy — Your Reading Profile

---

## 🧬 Your Reader DNA

{reader_dna}

---

## 📖 Personalized Recommendations

{recommendations_text}

---
*Generated by BookBuddy — your AI-powered Goodreads companion*
"""


# ── Sidebar ────────────────────────────────────────────────────────────────


def render_sidebar(uploaded_file: Any) -> None:
    """Render the sidebar with backend selection, model picker, and file uploader.

    Stores ``backend``, ``hf_model``, and ``ollama_model`` in ``st.session_state``.

    Args:
        uploaded_file: The file-like object returned by ``st.file_uploader``.
    """
    from src.llm_client import get_available_hf_models, get_available_ollama_models

    with st.sidebar:
        st.markdown(
            f"""
            <h2 style="
                background: linear-gradient(135deg, {CLAUDE_PURPLE}, {GR_GOLD});
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-size: 1.6rem;
                font-weight: 700;
            ">⚙️ Configuration</h2>
            """,
            unsafe_allow_html=True,
        )

        # ── Backend selection ────────────────────────────────────────
        st.markdown("### 🔌 Inference Backend")
        backend_options: list[str] = ["huggingface", "ollama"]
        backend_labels: list[str] = [
            "☁️ HuggingFace Inference API (free)",
            "🖥️ Ollama (local, fully offline)",
        ]

        selected_backend_label: str = st.radio(
            "Choose your AI backend:",
            options=backend_labels,
            index=0,
            help=(
                "HuggingFace: runs on free cloud tier (needs HF_TOKEN in .env). "
                "Ollama: runs entirely on your machine, no internet required. "
                "Install Ollama first: https://ollama.com"
            ),
        )

        backend: str = backend_options[backend_labels.index(selected_backend_label)]
        st.session_state["backend"] = backend

        # ── Model picker (contextual) ────────────────────────────────
        st.markdown("### 🤖 Model")

        if backend == "ollama":
            ollama_models: dict[str, str] = get_available_ollama_models()
            ollama_labels: list[str] = list(ollama_models.keys())
            # Default to local Mistral
            default_ollama_idx: int = 0
            selected_ollama_label: str = st.selectbox(
                "Choose a local Ollama model:",
                options=ollama_labels,
                index=default_ollama_idx,
                help=(
                    "These models must already be pulled via `ollama pull <model>`. "
                    "If not available, pull the model in your terminal first."
                ),
            )
            st.session_state["ollama_model"] = ollama_models[selected_ollama_label]

            st.markdown(
                f"""<p style="color:{TEXT_MUTED};font-size:0.75rem;">
                🖥️ Running locally via Ollama<br>
                ⚡ Fully offline — no API key needed
                </p>""",
                unsafe_allow_html=True,
            )
        else:
            hf_models: dict[str, str] = get_available_hf_models()
            hf_labels: list[str] = list(hf_models.keys())
            # Default to Mistral-7B
            default_hf_idx: int = 0
            selected_hf_label: str = st.selectbox(
                "Choose a free HuggingFace model:",
                options=hf_labels,
                index=default_hf_idx,
                help="All models run on the free HuggingFace Inference API tier.",
            )
            st.session_state["hf_model"] = hf_models[selected_hf_label]

            st.markdown(
                f"""<p style="color:{TEXT_MUTED};font-size:0.75rem;">
                ☁️ Runs free on HuggingFace Inference API<br>
                🔑 Requires HF_TOKEN in .env file
                </p>""",
                unsafe_allow_html=True,
            )

        st.divider()

        # ── File upload ──────────────────────────────────────────────
        st.markdown("### 📂 Upload Goodreads Export")
        if not uploaded_file:
            st.info(
                "👆 Export your Goodreads library as CSV "
                "(My Books → Import/Export → Export Library), "
                "then upload it here."
            )
