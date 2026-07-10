"""Unit tests for prompts.py — system/user prompt construction."""

from __future__ import annotations

from src.prompts import (
    build_reader_dna_prompt,
    build_recommendations_prompt,
    get_reader_dna_system,
    get_recommendations_system,
)


class TestReaderDnaPrompts:
    def test_system_prompt_non_empty(self) -> None:
        prompt = get_reader_dna_system()
        assert len(prompt) > 50
        assert "literary analyst" in prompt.lower()

    def test_user_prompt_contains_books(self) -> None:
        books = ["The Hobbit by Tolkien", "Dune by Herbert", "Foundation by Asimov"]
        prompt = build_reader_dna_prompt(books)
        assert "The Hobbit by Tolkien" in prompt
        assert "Dune by Herbert" in prompt
        assert "150-word" in prompt

    def test_user_prompt_truncation(self) -> None:
        """Ensure prompt builder caps at 50 books even if more provided."""
        books = [f"Book {i} by Author {i}" for i in range(100)]
        prompt = build_reader_dna_prompt(books)
        # Should only have up to 50 entries
        assert "Book 99" not in prompt
        assert "Book 49" in prompt

    def test_user_prompt_empty_list(self) -> None:
        """Empty book list should still produce a valid prompt."""
        prompt = build_reader_dna_prompt([])
        assert "150-word" in prompt
        assert "Books:" in prompt


class TestRecommendationsPrompts:
    def test_system_prompt_non_empty(self) -> None:
        prompt = get_recommendations_system()
        assert len(prompt) > 50
        assert "bookseller" in prompt.lower()

    def test_user_prompt_contains_dna_and_books(self) -> None:
        dna = "You love sweeping epics with morally complex protagonists."
        books = ["The Hobbit by Tolkien", "Dune by Herbert"]
        prompt = build_recommendations_prompt(dna, books)
        assert dna in prompt
        assert "The Hobbit by Tolkien" in prompt
        assert "already-read list" in prompt

    def test_user_prompt_truncation(self) -> None:
        """Read list capped at 200 books."""
        books = [f"Book {i} by Author {i}" for i in range(300)]
        prompt = build_recommendations_prompt("DNA here", books)
        assert "Book 250" not in prompt
        assert "Book 150" in prompt

    def test_format_instructions_present(self) -> None:
        prompt = build_recommendations_prompt("DNA", ["Book 1"])
        assert "**Title**" in prompt
        assert "*Reason:*" in prompt
        assert "2-sentence" in prompt

    def test_empty_read_list(self) -> None:
        prompt = build_recommendations_prompt("DNA text", [])
        assert "DNA text" in prompt
        assert "already-read list" in prompt
