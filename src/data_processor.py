"""Parse, validate, and analyze Goodreads CSV export files."""

from __future__ import annotations

import logging
import re
from typing import Any

import pandas as pd
import streamlit as st

from src.exceptions import (
    CSVLoadError,
    EmptyDatasetError,
    MissingColumnsError,
)

logger = logging.getLogger(__name__)

# ── Required / optional Goodreads export columns ─────────────────────

REQUIRED_COLUMNS: list[str] = [
    "Title",
    "Author",
    "My Rating",
]

OPTIONAL_COLUMNS: list[str] = [
    "ISBN",
    "ISBN13",
    "Number of Pages",
    "Date Read",
    "Bookshelves",
    "My Review",
    "Exclusive Shelf",
    "Read Count",
]

ALL_EXPECTED_COLUMNS: set[str] = set(REQUIRED_COLUMNS + OPTIONAL_COLUMNS)

# ── Genre keyword map ────────────────────────────────────────────────

GENRE_KEYWORDS: dict[str, list[str]] = {
    "Fantasy": [
        "magic", "dragon", "sword", "kingdom", "throne", "wizard", "sorcerer",
        "mage", "fae", "elf", "dwarf", "orc", "quest", "dark lord",
        "fantasy", "grimdark", "myth", "legend", "god", "goddess",
        "necromancer", "spell", "enchant", "crown", "warrior",
    ],
    "Science Fiction": [
        "space", "planet", "starship", "alien", "galaxy", "mars", "robot",
        "cyborg", "ai", "artificial", "dystopian", "utopian", "colony",
        "space opera", "sci-fi", "interstellar", "cosmic", "quantum",
        "futuristic", "android", "cyber", "hacker", "upload",
    ],
    "Mystery & Thriller": [
        "murder", "detective", "crime", "killer", "mystery", "thriller",
        "suspense", "whodunit", "investigation", "serial killer",
        "police", "fbi", "cia", "spy", "espionage", "conspiracy",
        "disappearance", "missing", "cold case", "body", "corpse",
        "forensic", "evidence", "witness", "suspect", "agent",
    ],
    "Historical Fiction": [
        "historical", "history", "medieval", "victorian", "renaissance",
        "ancient", "roman", "war", "wwii", "world war", "century",
        "18th", "19th", "1800s", "1900s", "nazi", "holocaust",
        "colonial", "revolution", "civil war", "king", "queen", "empire",
    ],
    "Literary Fiction": [
        "literary", "literature", "contemporary", "family saga",
        "coming of age", "generational", "character study",
    ],
    "Romance": [
        "romance", "love story", "love", "romantic", "heart",
        "passion", "relationship", "dating",
    ],
    "Horror": [
        "horror", "haunted", "ghost", "monster", "vampire", "zombie",
        "supernatural", "terror", "nightmare", "fear", "creepy",
        "gothic", "eldritch", "cosmic horror",
    ],
    "Non-Fiction": [
        "non-fiction", "memoir", "biography", "history", "science",
        "philosophy", "essay", "true story", "journalism",
    ],
    "Comics & Graphic Novels": [
        "comic", "graphic novel", "batman", "superman", "marvel",
        "thor", "hawkeye", "superhero", "manga",
    ],
    "Adventure": [
        "adventure", "exploration", "expedition", "survival",
        "treasure", "pirate", "journey",
    ],
    "Young Adult": [
        "young adult", "ya", "teen", "adolescent", "high school",
    ],
}


# ── CSV loading ──────────────────────────────────────────────────────


@st.cache_data
def load_and_clean_csv(file: Any) -> pd.DataFrame:
    """Load a Goodreads CSV export, validate columns, and clean/normalize.

    Args:
        file: Uploaded file object from ``st.file_uploader``.

    Returns:
        Cleaned DataFrame with only completed+rated books.

    Raises:
        CSVLoadError: File is unreadable.
        MissingColumnsError: Required Goodreads columns absent.
        EmptyDatasetError: Zero rows remain after filtering.
    """
    try:
        df: pd.DataFrame = pd.read_csv(file, encoding="utf-8")
    except Exception as exc:
        raise CSVLoadError(f"Could not parse uploaded CSV: {exc}") from exc

    # Normalize column names
    df.columns = df.columns.str.strip()

    # Check required columns
    missing: list[str] = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise MissingColumnsError(
            f"CSV is missing required Goodreads columns: {', '.join(missing)}. "
            "Make sure you exported 'My Rating' and other default fields from Goodreads."
        )

    logger.info("Loaded CSV: %d rows, %d columns", len(df), len(df.columns))

    # ── Parse dates ──────────────────────────────────────────────────
    if "Date Read" in df.columns:
        df["Date Read"] = pd.to_datetime(
            df["Date Read"], format="%Y/%m/%d", errors="coerce"
        )
        df["Year Read"] = df["Date Read"].dt.year

    # ── Clean ISBN fields ────────────────────────────────────────────
    for col in ("ISBN", "ISBN13"):
        if col in df.columns:
            df[col] = (
                df[col].astype(str).str.replace('"', "").str.replace("=", "").str.strip()
            )

    # ── Numeric coercion ─────────────────────────────────────────────
    if "Number of Pages" in df.columns:
        df["Number of Pages"] = (
            pd.to_numeric(df["Number of Pages"], errors="coerce").fillna(0).astype(int)
        )

    if "My Rating" in df.columns:
        df["My Rating"] = (
            pd.to_numeric(df["My Rating"], errors="coerce").fillna(0).astype(int)
        )

    if "Read Count" in df.columns:
        df["Read Count"] = (
            pd.to_numeric(df["Read Count"], errors="coerce").fillna(0).astype(int)
        )

    # ── Filter to completed reads ────────────────────────────────────
    if "Exclusive Shelf" in df.columns:
        before: int = len(df)
        df = df[df["Exclusive Shelf"] == "read"].copy()
        logger.info("Filtered Exclusive Shelf: %d → %d rows", before, len(df))

    # Remove unrated books
    before = len(df)
    df = df[df["My Rating"] > 0].copy()
    logger.info("Removed unrated books: %d → %d rows", before, len(df))

    if len(df) == 0:
        raise EmptyDatasetError(
            "No rated books found in the CSV. "
            "Make sure your Goodreads export includes books you've rated and marked as 'read'."
        )

    return df


# ── Author helpers ───────────────────────────────────────────────────


def extract_author_lastname(author: object) -> str:
    """Extract surname from Goodreads author format (``Lastname, Firstname``).

    Args:
        author: Raw author string from CSV.

    Returns:
        Last name, or ``"Unknown"`` if not parseable.
    """
    if pd.isna(author):
        return "Unknown"
    parts: list[str] = str(author).split(",")
    return parts[0].strip()


# ── Genre inference ──────────────────────────────────────────────────


def infer_genres(df: pd.DataFrame) -> pd.Series:
    """Infer primary genre per book via keyword matching.

    Searches ``Bookshelves``, ``Title``, and ``My Review`` columns (when
    available) against ``GENRE_KEYWORDS``. Falls back to ``"Other"``.

    Args:
        df: Cleaned DataFrame.

    Returns:
        Series indexed by DataFrame row, genre label per row.
    """
    genres: pd.Series = pd.Series("Other", index=df.index, dtype=str)

    # Build searchable text per book
    texts: pd.Series = pd.Series("", index=df.index, dtype=str)
    if "Bookshelves" in df.columns:
        texts += df["Bookshelves"].fillna("").astype(str)
    if "Title" in df.columns:
        texts += " " + df["Title"].fillna("").astype(str)
    if "My Review" in df.columns:
        texts += " " + df["My Review"].fillna("").astype(str)

    texts_lower: pd.Series = texts.str.lower()

    for genre, keywords in GENRE_KEYWORDS.items():
        pattern: str = r"\b(?:" + "|".join(re.escape(kw.lower()) for kw in keywords) + r")\b"
        matches: pd.Series = texts_lower.str.contains(
            pattern, regex=True, na=False
        )
        genres.loc[matches & (genres == "Other")] = genre

    return genres


# ── Stat computation ─────────────────────────────────────────────────


@st.cache_data
def compute_stats(df: pd.DataFrame) -> dict[str, Any]:
    """Aggregate all statistics from the cleaned DataFrame.

    Returns a dict with keys:
        ``total_books``, ``total_pages``, ``avg_rating``,
        ``books_by_year``, ``rating_distribution``, ``top_authors``,
        ``genre_breakdown``, ``highly_rated``, ``all_titles``.
    """
    stats: dict[str, Any] = {}

    stats["total_books"] = len(df)
    stats["total_pages"] = (
        int(df["Number of Pages"].sum()) if "Number of Pages" in df.columns else 0
    )
    stats["avg_rating"] = (
        round(float(df["My Rating"].mean()), 2)
        if "My Rating" in df.columns
        else 0.0
    )

    # Books per year
    if "Year Read" in df.columns:
        yearly: pd.DataFrame = (
            df.groupby("Year Read").size().reset_index(name="count").dropna()
        )
        yearly["Year Read"] = yearly["Year Read"].astype(int)
        stats["books_by_year"] = yearly
    else:
        stats["books_by_year"] = pd.DataFrame(columns=["Year Read", "count"])

    # Rating distribution
    if "My Rating" in df.columns:
        rating_dist: pd.Series = df["My Rating"].value_counts().sort_index()
        stats["rating_distribution"] = rating_dist
    else:
        stats["rating_distribution"] = pd.Series(dtype=int)

    # Top 10 authors
    if "Author" in df.columns:
        top_authors_df: pd.DataFrame = (
            df["Author"].value_counts().head(10).reset_index()
        )
        top_authors_df.columns = ["Author", "Count"]
        stats["top_authors"] = top_authors_df
    else:
        stats["top_authors"] = pd.DataFrame(columns=["Author", "Count"])

    # Genre breakdown
    genres: pd.Series = infer_genres(df)
    genre_counts: pd.Series = genres.value_counts()
    stats["genre_breakdown"] = genre_counts

    # 4–5 star reads for Reader DNA
    stats["highly_rated"] = df[df["My Rating"] >= 4].copy()

    # All title+author strings for recommendation context
    stats["all_titles"] = []
    if "Title" in df.columns and "Author" in df.columns:
        stats["all_titles"] = [
            f"{row['Title']} by {extract_author_lastname(row['Author'])}"
            for _, row in df.iterrows()
        ]

    logger.info("Stats computed: %d books, %d pages", stats["total_books"], stats["total_pages"])
    return stats
