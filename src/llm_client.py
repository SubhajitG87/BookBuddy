"""LLM client abstraction — HuggingFace Inference API and Ollama.

Provides a unified ``call_llm(system, user) -> str`` interface that routes
to the selected backend based on ``st.session_state["backend"]``.
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any

import streamlit as st
from huggingface_hub import InferenceClient

from src.exceptions import (
    APIConnectionError,
    OllamaConnectionError,
    TokenMissingError,
)

logger = logging.getLogger(__name__)

# ── Model catalog ────────────────────────────────────────────────────

# Free models on the HuggingFace Inference API (no credit card needed)

HF_FREE_MODELS: dict[str, str] = {
    "Mistral-7B (fast, solid all-rounder)": "mistralai/Mistral-7B-Instruct-v0.3",
    "Llama-3.1-8B (Meta's flagship)": "meta-llama/Llama-3.1-8B-Instruct",
    "Gemma-2-9B (Google's lightweight)": "google/gemma-2-9b-it",
}

# Local Ollama models (assumed pulled; mistral:7b is the 4.1 GB default)

OLLAMA_MODELS: dict[str, str] = {
    "Mistral (local)": "mistral",
    "Llama-3.1 (local)": "llama3.1:8b",
    "Gemma-2 (local)": "gemma2:9b",
}

MAX_RETRIES = 3
RETRY_BACKOFF = 2.0  # seconds — exponential: 2, 4, 8


# ── Public helpers ───────────────────────────────────────────────────


def get_available_hf_models() -> dict[str, str]:
    """Return dict of free HF Inference API models."""
    return dict(HF_FREE_MODELS)


def get_available_ollama_models() -> dict[str, str]:
    """Return dict of local Ollama models."""
    return dict(OLLAMA_MODELS)


# ── Core dispatch ────────────────────────────────────────────────────


def call_llm(system: str, user: str) -> str:
    """Send a chat completion request, routing to the active backend.

    Reads ``st.session_state`` for:
        - ``backend``: ``"huggingface"`` or ``"ollama"``
        - ``hf_model``: key into ``HF_FREE_MODELS`` (HF mode)
        - ``ollama_model``: key into ``OLLAMA_MODELS`` (Ollama mode)

    Args:
        system: System prompt.
        user: User message.

    Returns:
        The model's text response.

    Raises:
        TokenMissingError: HF_TOKEN not set (HF mode).
        APIConnectionError: Network/auth/timeout from HF.
        APIResponseError: Bad HF response.
        OllamaConnectionError: Local Ollama unreachable.
    """
    backend: str = st.session_state.get("backend", "huggingface")

    if backend == "ollama":
        return _call_ollama(system, user)
    return _call_huggingface(system, user)


# ── HuggingFace path ─────────────────────────────────────────────────


def _call_huggingface(system: str, user: str) -> str:
    """Call HuggingFace Inference API with retry/backoff."""
    token = os.environ.get("HF_TOKEN")
    if not token:
        raise TokenMissingError(
            "HF_TOKEN environment variable is not set. "
            "Copy .env.example → .env and paste your HuggingFace token "
            "(free tier from https://huggingface.co/settings/tokens)."
        )

    model_display: str = st.session_state.get(
        "hf_model",
        list(HF_FREE_MODELS.keys())[0],
    )
    model_id: str = HF_FREE_MODELS.get(model_display, list(HF_FREE_MODELS.values())[0])
    client = InferenceClient(model=model_id, token=token)
    messages: list[dict[str, str]] = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]

    last_exc: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(
                "HF API call (attempt %d/%d, model=%s)",
                attempt,
                MAX_RETRIES,
                model_id,
            )
            result = client.chat_completion(messages=messages, max_tokens=500)
            content: str = result.choices[0].message.content
            return content
        except Exception as exc:
            last_exc = exc
            logger.warning(
                "HF API attempt %d failed: %s",
                attempt,
                exc,
            )
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF ** attempt)

    raise APIConnectionError(
        f"HuggingFace API call failed after {MAX_RETRIES} retries: {last_exc}"
    )


# ── Ollama path ──────────────────────────────────────────────────────


def _call_ollama(system: str, user: str) -> str:
    """Call local Ollama server."""
    try:
        import ollama  # type: ignore[import-untyped]
    except ImportError:
        raise OllamaConnectionError(
            "Ollama Python library not installed. "
            "Run: pip install ollama && ollama pull mistral"
        )

    model_display: str = st.session_state.get(
        "ollama_model",
        list(OLLAMA_MODELS.keys())[0],
    )
    model_name: str = OLLAMA_MODELS.get(model_display, list(OLLAMA_MODELS.values())[0])

    messages: list[dict[str, str]] = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]

    try:
        logger.info("Ollama call (model=%s)", model_name)
        response: dict[str, Any] = ollama.chat(model=model_name, messages=messages)
        return response["message"]["content"]
    except Exception as exc:
        raise OllamaConnectionError(
            f"Ollama call failed. Is the Ollama server running? ({exc})"
        ) from exc
