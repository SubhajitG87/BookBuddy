"""Plotly chart builders with Goodreads + Claude gradient color scheme."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Color Palette ──────────────────────────────────────────────────────────
# Goodreads brown/gold + Claude purple gradient

GR_BROWN: str = "#8B4513"
GR_GOLD: str = "#B8860B"
CLAUDE_PURPLE: str = "#663399"
CLAUDE_BLUE: str = "#16213E"
CARD_DARK: str = "#1A1A2E"
TEXT_LIGHT: str = "#F0E6D2"
TEXT_MUTED: str = "#A0907A"

GRADIENT_5: list[str] = [GR_BROWN, "#9B5B2A", "#C4861E", CLAUDE_PURPLE, CLAUDE_BLUE]
GRADIENT_FILL: list[str] = [GR_BROWN, GR_GOLD, "#D4A04A", CLAUDE_PURPLE, "#4A2060"]

# ── Theme helper ───────────────────────────────────────────────────────────


def _apply_theme(fig: go.Figure) -> go.Figure:
    """Apply the consistent BookBuddy dark theme to a Plotly figure."""
    fig.update_layout(
        plot_bgcolor=CARD_DARK,
        paper_bgcolor=CARD_DARK,
        font_color=TEXT_LIGHT,
        title_font_color=TEXT_LIGHT,
        xaxis={
            "gridcolor": "rgba(255,255,255,0.08)",
            "zerolinecolor": "rgba(255,255,255,0.1)",
        },
        yaxis={
            "gridcolor": "rgba(255,255,255,0.08)",
            "zerolinecolor": "rgba(255,255,255,0.1)",
        },
        margin={"l": 40, "r": 20, "t": 40, "b": 40},
    )
    return fig


def _empty_chart(message: str) -> go.Figure:
    """Create a placeholder chart with a centred message."""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font={"color": TEXT_MUTED, "size": 16},
    )
    return _apply_theme(fig)


# ── Chart builders ─────────────────────────────────────────────────────────


def books_per_year_chart(yearly_df: pd.DataFrame) -> go.Figure:
    """Bar chart: Number of books read per year.

    Args:
        yearly_df: DataFrame with columns ``Year Read`` (int) and ``count``.

    Returns:
        Plotly Figure (themed).
    """
    if yearly_df.empty:
        return _empty_chart("No year data available")

    fig = px.bar(
        yearly_df,
        x="Year Read",
        y="count",
        title="📚 Books Read per Year",
        labels={"Year Read": "Year", "count": "Books"},
        color_discrete_sequence=[GR_GOLD],
        text_auto=True,
    )
    fig.update_traces(
        marker={
            "color": GR_GOLD,
            "opacity": 0.85,
            "line": {"width": 0},
        },
        textfont_color=TEXT_LIGHT,
        textposition="outside",
    )
    return _apply_theme(fig)


def rating_distribution_chart(rating_dist: pd.Series) -> go.Figure:
    """Histogram: Distribution of ratings (1–5 stars).

    Args:
        rating_dist: Value-counts Series indexed by rating (1–5).

    Returns:
        Plotly Figure (themed).
    """
    if rating_dist.empty:
        return _empty_chart("No rating data available")

    # Ensure all ratings 1–5 are represented
    full_index: pd.Index = pd.Index([1, 2, 3, 4, 5], name="My Rating")
    rating_dist = rating_dist.reindex(full_index, fill_value=0)

    rating_colors: dict[int, str] = {
        1: "#3A1C0E",
        2: GR_BROWN,
        3: GR_GOLD,
        4: CLAUDE_PURPLE,
        5: "#8B2252",
    }

    fig = go.Figure()
    for rating in [1, 2, 3, 4, 5]:
        count_val: int = int(rating_dist.get(rating, 0))
        fig.add_trace(
            go.Bar(
                x=[f"{rating} ★"],
                y=[count_val],
                name=f"{rating} Star{'s' if rating > 1 else ''}",
                marker_color=rating_colors.get(rating, GR_GOLD),
                text=[str(count_val)],
                textposition="outside",
                textfont={"color": TEXT_LIGHT},
                showlegend=False,
            )
        )

    fig.update_layout(
        title="⭐ Rating Distribution",
        xaxis_title="Rating",
        yaxis_title="Number of Books",
        barmode="group",
    )
    return _apply_theme(fig)


def top_authors_chart(top_authors_df: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart: Top 10 authors by book count.

    Args:
        top_authors_df: DataFrame with columns ``Author`` and ``Count``.

    Returns:
        Plotly Figure (themed).
    """
    if top_authors_df.empty:
        return _empty_chart("No author data available")

    df_sorted: pd.DataFrame = top_authors_df.sort_values("Count", ascending=True)

    fig = go.Figure(
        go.Bar(
            x=df_sorted["Count"],
            y=df_sorted["Author"],
            orientation="h",
            marker={
                "color": df_sorted["Count"],
                "colorscale": [
                    [0.0, CLAUDE_BLUE],
                    [0.5, CLAUDE_PURPLE],
                    [1.0, GR_GOLD],
                ],
                "showscale": False,
            },
            text=df_sorted["Count"],
            textposition="outside",
            textfont={"color": TEXT_LIGHT},
        )
    )
    fig.update_layout(
        title="✍️ Top 10 Authors",
        xaxis_title="Books Read",
        yaxis={"autorange": "reversed"},
    )
    return _apply_theme(fig)


def genre_pie_chart(genre_breakdown: pd.Series) -> go.Figure:
    """Pie chart: Genre breakdown inferred from reading data.

    Small slices (< 3 % of total) are rolled up into ``"Other"``.

    Args:
        genre_breakdown: Value-counts Series indexed by genre label.

    Returns:
        Plotly Figure (themed).
    """
    if genre_breakdown.empty:
        return _empty_chart("No genre data available")

    # Roll up small slices
    threshold: float = 0.03
    total: int = genre_breakdown.sum()
    small_mask: pd.Series = genre_breakdown / total < threshold
    small_sum: int = genre_breakdown[small_mask].sum()

    if len(genre_breakdown[small_mask]) > 1:
        genre_breakdown = genre_breakdown[~small_mask].copy()
        genre_breakdown["Other"] = small_sum

    fig = px.pie(
        values=genre_breakdown.values,
        names=genre_breakdown.index,
        title="🎨 Genre Breakdown",
        color_discrete_sequence=GRADIENT_FILL,
        hole=0.4,
    )
    fig.update_traces(
        textinfo="percent+label",
        textfont_color=TEXT_LIGHT,
        pull=[0.05] * len(genre_breakdown),
    )
    return _apply_theme(fig)
