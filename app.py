"""BookBuddy — AI-powered Goodreads reading history analyzer."""

from __future__ import annotations

import logging
import re
from typing import Any

import streamlit as st
from dotenv import load_dotenv

from src.logging_config import configure_logging

# ── Setup ──────────────────────────────────────────────────────────────────
load_dotenv()
configure_logging(level=logging.INFO)

logger = logging.getLogger("bookbuddy")

# ── Session State Initialization ───────────────────────────────────────────
DEFAULTS: dict[str, Any] = {
    "backend": "huggingface",
    "hf_model": "mistralai/Mistral-7B-Instruct-v0.3",
    "ollama_model": "mistral",
    "reader_dna": None,
    "recommendations_text": None,
}
for key, val in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BookBuddy — Your Reading DNA",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Imports (must come after set_page_config per Streamlit requirement) ─────
# ruff: noqa: E402
from src.charts import (
    books_per_year_chart,
    genre_pie_chart,
    rating_distribution_chart,
    top_authors_chart,
)
from src.data_processor import (
    compute_stats,
    extract_author_lastname,
    load_and_clean_csv,
)
from src.exceptions import (
    APIConnectionError,
    APIResponseError,
    DataError,
    LLMError,
    OllamaConnectionError,
    TokenMissingError,
)
from src.llm_client import call_llm
from src.prompts import (
    build_reader_dna_prompt,
    build_recommendations_prompt,
    get_reader_dna_system,
    get_recommendations_system,
)
from src.ui_components import (
    build_markdown_export,
    inject_custom_css,
    render_header,
    render_reader_dna,
    render_recommendation_card,
    render_sidebar,
    render_stat_cards,
)

# ── Inject Custom CSS ──────────────────────────────────────────────────────
inject_custom_css()

# ── Header ─────────────────────────────────────────────────────────────────
render_header()

# ── Sidebar ────────────────────────────────────────────────────────────────
uploaded_file = st.sidebar.file_uploader(
    "Upload CSV",
    type=["csv"],
    label_visibility="collapsed",
)
render_sidebar(uploaded_file)


# ── Error display helper ───────────────────────────────────────────────────
def _show_data_error(exc: DataError) -> None:
    """Display a user-friendly data error and stop execution."""
    st.error(f"❌ {exc}")
    st.info(
        "Make sure you uploaded a valid Goodreads export CSV. "
        "It should contain columns like 'Title', 'Author', 'My Rating', "
        "'Date Read', 'Bookshelves', etc. "
        "See the README for step-by-step export instructions."
    )


def _show_llm_error(exc: LLMError) -> None:
    """Display a user-friendly LLM error with actionable guidance."""
    if isinstance(exc, TokenMissingError):
        st.error(f"🔑 {exc}")
        st.info(
            "Create a free token at https://huggingface.co/settings/tokens, "
            "copy .env.example → .env, and paste your token as HF_TOKEN=..."
        )
    elif isinstance(exc, (APIConnectionError, APIResponseError)):
        st.error(f"☁️ {exc}")
        st.info(
            "Try a different model in the sidebar, or check your internet connection. "
            "The HuggingFace free tier may be busy — retrying usually helps."
        )
    elif isinstance(exc, OllamaConnectionError):
        st.error(f"🖥️ {exc}")
        st.info(
            "Make sure the Ollama app is running (check your menu bar / system tray). "
            "Install from https://ollama.com if you haven't already."
        )
    else:
        st.error(f"🤖 AI error: {exc}")


# ── No File Uploaded State ─────────────────────────────────────────────────
if not uploaded_file:
    st.markdown(
        """
        <div style="text-align:center;padding:3rem 1rem;">
            <p style="color:#A0907A;font-size:1.1rem;">
                👈 Upload your Goodreads CSV export from the sidebar to get started
            </p>
            <p style="color:#6A5A4A;font-size:0.85rem;margin-top:1rem;">
                📖 My Books → Import/Export → Export Library → Download CSV
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

# ── Load and Process Data ─────────────────────────────────────────────────
try:
    df = load_and_clean_csv(uploaded_file)
    logger.info("Data loaded successfully: %d books", len(df))
except DataError as exc:
    _show_data_error(exc)
    st.stop()
except Exception as exc:
    logger.exception("Unexpected error during CSV loading")
    st.error(f"❌ Unexpected error reading CSV: {exc}")
    st.info("If this persists, please file an issue with the CSV file you're trying to upload.")
    st.stop()

stats = compute_stats(df)

# ── Tab Layout ─────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📊 My Stats", "🧬 Reader DNA", "📖 Recommendations"])

# ═══════════════════════════════════════════════════════════════════════════
# TAB 1 — My Stats
# ═══════════════════════════════════════════════════════════════════════════
with tab1:
    # Stat cards
    render_stat_cards(
        total_books=stats["total_books"],
        total_pages=stats["total_pages"],
        avg_rating=stats["avg_rating"],
    )

    # Charts grid
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(
            books_per_year_chart(stats["books_by_year"]),
            use_container_width=True,
        )
        st.plotly_chart(
            top_authors_chart(stats["top_authors"]),
            use_container_width=True,
        )
    with col2:
        st.plotly_chart(
            rating_distribution_chart(stats["rating_distribution"]),
            use_container_width=True,
        )
        st.plotly_chart(
            genre_pie_chart(stats["genre_breakdown"]),
            use_container_width=True,
        )

    # Data summary
    st.markdown(
        """
        <p style="color:#A0907A;font-size:0.8rem;text-align:center;margin-top:1rem;">
            📊 Charts powered by Plotly • Genres inferred from book metadata
        </p>
        """,
        unsafe_allow_html=True,
    )

# ═══════════════════════════════════════════════════════════════════════════
# TAB 2 — Reader DNA
# ═══════════════════════════════════════════════════════════════════════════
with tab2:
    highly_rated = stats["highly_rated"]

    if highly_rated.empty:
        st.warning(
            "No books rated 4-5 stars in your data. "
            "Upload a library with ratings to generate your Reader DNA."
        )
    else:
        # Build list of highly rated books
        highly_rated_list: list[str] = [
            f"{row['Title']} by {extract_author_lastname(row['Author'])}"
            for _, row in highly_rated.iterrows()
        ]

        st.markdown(
            f"""
            <p style="color:#A0907A;margin-bottom:1rem;">
                📊 Analyzing <strong>{len(highly_rated_list)}</strong> books rated 4–5 stars
                to decode your reading personality.
            </p>
            """,
            unsafe_allow_html=True,
        )

        if st.button("🔬 Generate My Reader DNA", type="primary"):
            with st.spinner("🧬 Decoding your literary DNA..."):
                try:
                    dna_text = call_llm(
                        system=get_reader_dna_system(),
                        user=build_reader_dna_prompt(highly_rated_list),
                    )
                    st.session_state["reader_dna"] = dna_text
                    logger.info("Reader DNA generated successfully")
                except TokenMissingError as exc:
                    _show_llm_error(exc)
                except APIConnectionError as exc:
                    _show_llm_error(exc)
                except APIResponseError as exc:
                    _show_llm_error(exc)
                except OllamaConnectionError as exc:
                    _show_llm_error(exc)
                except LLMError as exc:
                    _show_llm_error(exc)
                except Exception as exc:
                    logger.exception("Unexpected error generating Reader DNA")
                    st.error(f"❌ Unexpected error: {exc}")

        # Display cached DNA if available
        if st.session_state["reader_dna"]:
            render_reader_dna(st.session_state["reader_dna"])
            if st.button("🔄 Regenerate Reader DNA"):
                st.session_state["reader_dna"] = None
                st.rerun()

# ═══════════════════════════════════════════════════════════════════════════
# TAB 3 — Recommendations
# ═══════════════════════════════════════════════════════════════════════════
with tab3:
    if not st.session_state["reader_dna"]:
        st.info(
            "👈 Go to the **Reader DNA** tab first and generate your reading profile. "
            "Then come back here for personalized recommendations."
        )
    else:
        st.markdown(
            f"""
            <p style="color:#A0907A;margin-bottom:1rem;">
                📚 Using your Reader DNA and your full library of
                <strong>{len(stats['all_titles'])}</strong> read books to find hidden gems.
            </p>
            """,
            unsafe_allow_html=True,
        )

        if st.button("📖 Find My Next 5 Books", type="primary"):
            with st.spinner("🔍 Searching the literary universe for your perfect reads..."):
                try:
                    rec_text = call_llm(
                        system=get_recommendations_system(),
                        user=build_recommendations_prompt(
                            reader_dna=st.session_state["reader_dna"],
                            all_read_books=stats["all_titles"],
                        ),
                    )
                    st.session_state["recommendations_text"] = rec_text
                    logger.info("Recommendations generated successfully")
                except TokenMissingError as exc:
                    _show_llm_error(exc)
                except APIConnectionError as exc:
                    _show_llm_error(exc)
                except APIResponseError as exc:
                    _show_llm_error(exc)
                except OllamaConnectionError as exc:
                    _show_llm_error(exc)
                except LLMError as exc:
                    _show_llm_error(exc)
                except Exception as exc:
                    logger.exception("Unexpected error generating recommendations")
                    st.error(f"❌ Unexpected error: {exc}")

        # Display cached recommendations
        if st.session_state["recommendations_text"]:
            rec_text: str = st.session_state["recommendations_text"]

            # Parse individual recommendations from the LLM response
            # Pattern: **Title** by Author\n*Reason:* explanation
            rec_blocks: list[str] = re.split(r"\n(?=\*\*|\d\.)", rec_text.strip())

            if len(rec_blocks) < 5:
                # Try alternative parsing: numbered list
                rec_blocks = re.split(r"\n\d+\.\s", rec_text.strip())
                rec_blocks = [b for b in rec_blocks if b.strip()]

            for i, block in enumerate(rec_blocks[:5], 1):
                block = block.strip()
                if not block:
                    continue

                # Try to extract title and author
                title_match = re.search(r"\*\*(.+?)\*\*", block)
                author_match = re.search(r"by\s+(.+?)[\n\r]", block)

                title: str = title_match.group(1) if title_match else "Untitled"
                author: str = author_match.group(1).strip() if author_match else "Unknown"

                # Extract reason
                reason_match = re.search(
                    r"\*Reason:\*\s*(.+?)(?:\n\*\*|\Z)", block, re.DOTALL
                )
                reason: str = (
                    reason_match.group(1).strip()
                    if reason_match
                    else block.split("\n", 1)[-1] if "\n" in block else block
                )

                render_recommendation_card(i, title, author, reason)

            # Regenerate button
            if st.button("🔄 Get Different Recommendations"):
                st.session_state["recommendations_text"] = None
                st.rerun()

            # ── Save to Markdown ──
            st.divider()
            md_content: str = build_markdown_export(
                reader_dna=st.session_state["reader_dna"],
                recommendations_text=st.session_state["recommendations_text"],
            )

            st.download_button(
                label="💾 Save to Markdown (.md)",
                data=md_content,
                file_name="bookbuddy_reading_profile.md",
                mime="text/markdown",
            )

            st.markdown(
                """
                <p style="color:#6A5A4A;font-size:0.75rem;text-align:center;">
                    📝 Downloads a beautifully formatted Markdown file with your DNA + recommendations
                </p>
                """,
                unsafe_allow_html=True,
            )

# ── Footer ─────────────────────────────────────────────────────────────────
st.divider()

# Dynamic footer — show the active backend
backend_display: str = (
    "🖥️ Ollama (local, fully offline)"
    if st.session_state.get("backend") == "ollama"
    else "☁️ HuggingFace Inference API (free tier)"
)

st.markdown(
    f"""
    <p style="color:#4A3A2A;font-size:0.7rem;text-align:center;">
        📚 BookBuddy &nbsp;|&nbsp;
        🤖 Powered by {backend_display} &nbsp;|&nbsp;
        📊 Charts with Plotly &nbsp;|&nbsp;
        🧬 Built with Streamlit
    </p>
    """,
    unsafe_allow_html=True,
)
