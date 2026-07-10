"""Unit tests for charts.py — all Plotly figures render without errors."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import pytest

from src.charts import (
    CARD_DARK,
    TEXT_LIGHT,
    TEXT_MUTED,
    books_per_year_chart,
    genre_pie_chart,
    rating_distribution_chart,
    top_authors_chart,
)

# ── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def yearly_df() -> pd.DataFrame:
    return pd.DataFrame(
        {"Year Read": [2024, 2025], "count": [10, 15]}
    )


@pytest.fixture
def rating_dist() -> pd.Series:
    return pd.Series(
        {1: 1, 2: 3, 3: 5, 4: 8, 5: 12},
        name="My Rating",
    )


@pytest.fixture
def top_authors_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Author": [
                "Kuang, R.F.",
                "Tolkien, J.R.R.",
                "Herbert, Frank",
                "Christie, Agatha",
                "Orwell, George",
            ],
            "Count": [5, 4, 3, 3, 2],
        }
    )


@pytest.fixture
def genre_breakdown() -> pd.Series:
    return pd.Series(
        {"Fantasy": 8, "Science Fiction": 5, "Mystery": 4, "Historical": 2, "Other": 1}
    )


# ── Books per year ──────────────────────────────────────────────────────────


class TestBooksPerYearChart:
    def test_returns_figure(self, yearly_df: pd.DataFrame) -> None:
        fig = books_per_year_chart(yearly_df)
        assert isinstance(fig, go.Figure)

    def test_has_theme(self, yearly_df: pd.DataFrame) -> None:
        fig = books_per_year_chart(yearly_df)
        assert fig.layout.plot_bgcolor == CARD_DARK
        assert fig.layout.paper_bgcolor == CARD_DARK

    def test_empty_dataframe(self) -> None:
        fig = books_per_year_chart(pd.DataFrame(columns=["Year Read", "count"]))
        assert isinstance(fig, go.Figure)
        # Should contain the "No year data" annotation
        assert len(fig.layout.annotations) > 0

    def test_title_present(self, yearly_df: pd.DataFrame) -> None:
        fig = books_per_year_chart(yearly_df)
        assert "Books Read per Year" in fig.layout.title.text


# ── Rating distribution ─────────────────────────────────────────────────────


class TestRatingDistributionChart:
    def test_returns_figure(self, rating_dist: pd.Series) -> None:
        fig = rating_distribution_chart(rating_dist)
        assert isinstance(fig, go.Figure)

    def test_all_five_bars_present(self, rating_dist: pd.Series) -> None:
        fig = rating_distribution_chart(rating_dist)
        assert len(fig.data) == 5

    def test_empty_series_returns_empty_chart(self) -> None:
        """Empty Series triggers _empty_chart with annotation, 0 traces."""
        fig = rating_distribution_chart(pd.Series(dtype=int))
        assert isinstance(fig, go.Figure)
        # Empty chart has annotations but 0 data traces
        assert len(fig.layout.annotations) > 0

    def test_has_theme(self, rating_dist: pd.Series) -> None:
        fig = rating_distribution_chart(rating_dist)
        assert fig.layout.plot_bgcolor == CARD_DARK

    def test_title_present(self, rating_dist: pd.Series) -> None:
        fig = rating_distribution_chart(rating_dist)
        assert "Rating Distribution" in fig.layout.title.text


# ── Top authors ─────────────────────────────────────────────────────────────


class TestTopAuthorsChart:
    def test_returns_figure(self, top_authors_df: pd.DataFrame) -> None:
        fig = top_authors_chart(top_authors_df)
        assert isinstance(fig, go.Figure)

    def test_horizontal_orientation(self, top_authors_df: pd.DataFrame) -> None:
        fig = top_authors_chart(top_authors_df)
        assert fig.data[0].orientation == "h"

    def test_empty_dataframe(self) -> None:
        fig = top_authors_chart(pd.DataFrame(columns=["Author", "Count"]))
        assert len(fig.layout.annotations) > 0  # empty message

    def test_sorted_ascending(self, top_authors_df: pd.DataFrame) -> None:
        fig = top_authors_chart(top_authors_df)
        # y values should be in ascending order of count
        y_vals = list(fig.data[0].y)
        assert y_vals[0] == "Orwell, George"
        assert y_vals[-1] == "Kuang, R.F."

    def test_has_theme(self, top_authors_df: pd.DataFrame) -> None:
        fig = top_authors_chart(top_authors_df)
        assert fig.layout.plot_bgcolor == CARD_DARK


# ── Genre pie chart ─────────────────────────────────────────────────────────


class TestGenrePieChart:
    def test_returns_figure(self, genre_breakdown: pd.Series) -> None:
        fig = genre_pie_chart(genre_breakdown)
        assert isinstance(fig, go.Figure)

    def test_donut_hole(self, genre_breakdown: pd.Series) -> None:
        """Pie chart should have hole=0.4 (donut style)."""
        fig = genre_pie_chart(genre_breakdown)
        assert fig.data[0].hole == 0.4

    def test_empty_series(self) -> None:
        fig = genre_pie_chart(pd.Series(dtype=int))
        assert len(fig.layout.annotations) > 0  # empty message

    def test_small_slices_rolled_up(self) -> None:
        """Tiny slices (<3%) should merge into 'Other'."""
        breakdown = pd.Series(
            {"Big1": 50, "Big2": 30, "Tiny1": 1, "Tiny2": 1}
        )
        fig = genre_pie_chart(breakdown)
        labels = list(fig.data[0].labels)
        assert "Other" in labels
        assert "Tiny1" not in labels
        assert "Tiny2" not in labels

    def test_single_small_slice_preserved(self) -> None:
        """A single small slice + one big slice requires >1 tiny to trigger rollup."""
        breakdown = pd.Series({"Big": 95, "Tiny": 5})
        fig = genre_pie_chart(breakdown)
        labels = list(fig.data[0].labels)
        # 5% is >3%, so it stays regardless of rollup threshold
        assert "Tiny" in labels

    def test_has_theme(self, genre_breakdown: pd.Series) -> None:
        fig = genre_pie_chart(genre_breakdown)
        assert fig.layout.plot_bgcolor == CARD_DARK


# ── Color palette ───────────────────────────────────────────────────────────


class TestColorPalette:
    def test_colors_are_valid_hex(self) -> None:
        for color in [CARD_DARK, TEXT_LIGHT, TEXT_MUTED]:
            assert color.startswith("#")
            assert len(color) == 7
