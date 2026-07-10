"""Custom exception hierarchy for BookBuddy.

All application-specific exceptions inherit from ``BookBuddyError``,
making it easy to catch any BookBuddy-related failure in a single ``except`` clause.
"""

from __future__ import annotations


class BookBuddyError(Exception):
    """Base class for all BookBuddy exceptions."""


# ── Data / CSV errors ───────────────────────────────────────────────


class DataError(BookBuddyError):
    """Errors related to data loading, parsing, or validation."""


class CSVLoadError(DataError):
    """Failed to load or parse the uploaded CSV file."""


class MissingColumnsError(DataError):
    """The CSV is missing one or more required Goodreads columns."""


class EmptyDatasetError(DataError):
    """The CSV contains zero usable rows after cleaning."""


class InvalidValueError(DataError):
    """A specific column value failed validation (e.g. non-numeric Pages)."""


# ── LLM / inference errors ───────────────────────────────────────────


class LLMError(BookBuddyError):
    """Errors from the language-model inference layer."""


class TokenMissingError(LLMError):
    """HF_TOKEN environment variable is not set (HuggingFace mode)."""


class APIConnectionError(LLMError):
    """Could not reach the inference endpoint (network / auth / timeout)."""


class APIResponseError(LLMError):
    """The API returned an error status or an invalid response body."""


class OllamaConnectionError(LLMError):
    """Could not reach the local Ollama server."""


# ── Configuration errors ─────────────────────────────────────────────


class ConfigError(BookBuddyError):
    """Errors from misconfiguration (missing env vars, invalid backends)."""
