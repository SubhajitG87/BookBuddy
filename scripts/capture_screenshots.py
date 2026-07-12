#!/usr/bin/env python3
"""Capture BookBuddy screenshots for the README.

Sets ``BOOKBUDDY_MOCK_MODE=true`` so the Streamlit process uses canned
AI responses (Reader DNA + Recommendations) without needing a real
HF_TOKEN or Ollama instance.

Also sets a dummy ``HF_TOKEN`` to prevent the token-missing error on
startup — the env var check passes, but the mock-mode short-circuit
in ``call_llm()`` fires before any real API call is attempted.

Text verification is done via ``page.inner_text("body")`` (pulls raw
text from the entire DOM), which catches content rendered via
``st.markdown(..., unsafe_allow_html=True)`` that Playwright's
``get_by_text()`` sometimes misses.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCREENSHOTS_DIR = PROJECT_ROOT / "docs" / "screenshots"
CSV_PATH = SCREENSHOTS_DIR / "goodreads_library_export.csv"
STREAMLIT_URL = "http://localhost:8501"


# ── Helpers ──────────────────────────────────────────────────────────


def wait_for_server(url: str, timeout: int = 30) -> bool:
    """Poll *url* until it responds 200 or *timeout* seconds elapse."""
    import urllib.error
    import urllib.request

    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(url, timeout=2)
            return True
        except (urllib.error.URLError, ConnectionRefusedError, OSError):
            time.sleep(1)
    return False


def kill_streamlit() -> None:
    """Kill any lingering streamlit process on port 8501."""
    try:
        result = subprocess.run(
            ["lsof", "-ti", ":8501"],
            capture_output=True, text=True, check=False,
        )
        if result.stdout.strip():
            for pid in result.stdout.strip().split("\n"):
                subprocess.run(["kill", pid], check=False)
    except FileNotFoundError:
        pass
    time.sleep(1)


def upload_csv(page) -> None:
    """Upload the Goodreads CSV export into Streamlit's file_uploader."""
    file_input = page.locator('input[type="file"]')
    file_input.set_input_files(str(CSV_PATH))
    time.sleep(5)  # wait for pandas parse + Plotly charts


def dismiss_dialogs(page) -> None:
    """Close any Streamlit dialogs/menus that block pointer events."""
    page.keyboard.press("Escape")
    time.sleep(0.5)

    dialog_close_btns = page.locator(
        '[data-testid="stDialog"] button[kind="secondary"], '
        '[data-testid="stDialog"] button[kind="tertiary"]'
    )
    if dialog_close_btns.count() > 0:
        try:
            dialog_close_btns.first.click(timeout=3000)
            time.sleep(0.5)
        except Exception:
            pass

    hamburger_btn = page.locator('button[data-testid="stMainMenu"]')
    if hamburger_btn.count() > 0:
        try:
            is_open = hamburger_btn.get_attribute("aria-expanded")
            if is_open == "true":
                page.keyboard.press("Escape")
                time.sleep(0.5)
        except Exception:
            pass


def click_tab(page, label: str) -> None:
    """Click a Streamlit tab button by visible label."""
    dismiss_dialogs(page)

    escaped = label.replace("'", "\\'")
    page.evaluate(f"""
    (() => {{
        const candidates = Array.from(
            document.querySelectorAll('button[role="tab"], p')
        );
        const el = candidates.find(
            e => e.textContent.includes('{escaped}')
        );
        if (el) {{
            el.scrollIntoView({{block: 'center'}});
            el.click();
        }}
    }})();
    """)
    time.sleep(2)


def wait_for_text(page, needle: str, max_wait: int = 15) -> bool:
    """Poll ``page.inner_text("body")`` for *needle* (case-insensitive substring).

    Returns True once found, False after *max_wait* seconds.
    """
    needle_lower = needle.lower()
    for _ in range(max_wait):
        time.sleep(1)
        body_text = page.inner_text("body")
        if needle_lower in body_text.lower():
            return True
    return False


# ── Main ─────────────────────────────────────────────────────────────


def capture() -> None:
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

    if not CSV_PATH.exists():
        print(f"ERROR: CSV not found at {CSV_PATH}")
        sys.exit(1)

    kill_streamlit()

    env = os.environ.copy()
    env["BOOKBUDDY_MOCK_MODE"] = "true"
    env["HF_TOKEN"] = "hf_dummy_screenshot_token"

    print("Starting Streamlit server (mock mode, dummy HF_TOKEN)...")
    streamlit_proc = subprocess.Popen(
        [
            sys.executable, "-m", "streamlit", "run",
            str(PROJECT_ROOT / "app.py"),
            "--server.headless=true",
            "--browser.gatherUsageStats=false",
            "--server.port=8501",
            "--theme.base=dark",
        ],
        cwd=str(PROJECT_ROOT),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        if not wait_for_server(STREAMLIT_URL, timeout=45):
            print("ERROR: Streamlit did not start within 45 s.")
            sys.exit(1)

        print("Streamlit is up.  Capturing screenshots ...")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 1440, "height": 900},
                device_scale_factor=1,
            )
            page = context.new_page()

            # ── Load app & upload CSV ─────────────────────────────
            page.goto(STREAMLIT_URL, wait_until="networkidle", timeout=30000)
            time.sleep(3)
            upload_csv(page)

            # ═══════════════════════════════════════════════════════
            # Screenshot 1 — Tab 1: My Stats (no AI needed)
            # ═══════════════════════════════════════════════════════
            page.screenshot(
                path=str(SCREENSHOTS_DIR / "tab1-stats.png"),
                full_page=True,
            )
            print("  ✓ tab1-stats.png")

            # ═══════════════════════════════════════════════════════
            # Screenshot 2 — Tab 2: Reader DNA (AI with mock)
            # ═══════════════════════════════════════════════════════
            click_tab(page, "🧬 Reader DNA")
            time.sleep(1)

            gen_btn = page.get_by_role("button").filter(
                has_text="Generate My Reader DNA"
            )
            if gen_btn.count() > 0:
                gen_btn.first.click()
                # Mock DNA mentions "Tolkien" — use inner_text for robustness
                ok = wait_for_text(page, "Tolkien", max_wait=20)
                if ok:
                    print("  (mock DNA text confirmed)")
                else:
                    print("  ⚠ Mock DNA text not detected after 20 s — capturing anyway")
                    time.sleep(3)
            else:
                print("  ⚠ 'Generate DNA' button not found — no 4-5 star books?")

            page.screenshot(
                path=str(SCREENSHOTS_DIR / "tab2-dna.png"),
                full_page=True,
            )
            print("  ✓ tab2-dna.png")

            # ═══════════════════════════════════════════════════════
            # Screenshot 3 — Tab 3: Recommendations (AI with mock)
            # ═══════════════════════════════════════════════════════
            click_tab(page, "📖 Recommendations")
            time.sleep(2)

            recs_btn = page.get_by_role("button").filter(
                has_text="Find My Next 5 Books"
            )
            if recs_btn.count() > 0:
                recs_btn.first.click()
                ok = wait_for_text(page, "Dispossessed", max_wait=20)
                if ok:
                    print("  (mock recommendations text confirmed)")
                else:
                    print("  ⚠ Mock recs text not detected after 20 s — capturing anyway")
                    time.sleep(3)
            else:
                print("  ⚠ 'Find books' button not found — DNA not generated?")

            page.screenshot(
                path=str(SCREENSHOTS_DIR / "tab3-recs.png"),
                full_page=True,
            )
            print("  ✓ tab3-recs.png")

            # ═══════════════════════════════════════════════════════
            # Screenshot 4 — Sidebar-focused (Tab 1, viewport only)
            # ═══════════════════════════════════════════════════════
            # Force-scroll to absolute top, then switch to tab 1.
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(0.5)
            click_tab(page, "📊 My Stats")
            time.sleep(1)
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(0.5)

            # Confirm we see "Books Read" stat-card text (tab 1 content)
            body = page.inner_text("body")
            if "Books Read" in body:
                print("  (sidebar: tab 1 active — confirmed)")
            else:
                print("  ⚠ Warning: 'Books Read' not found — sidebar may show wrong tab")

            page.screenshot(
                path=str(SCREENSHOTS_DIR / "sidebar.png"),
                full_page=False,  # viewport = sidebar + header + top stats
            )
            print("  ✓ sidebar.png")

            # ── Summary ───────────────────────────────────────────
            print("\n--- File sizes ---")
            for png_file in ["tab1-stats.png", "tab2-dna.png",
                             "tab3-recs.png", "sidebar.png"]:
                fp = SCREENSHOTS_DIR / png_file
                print(f"  {png_file}: {fp.stat().st_size:,} bytes")

            browser.close()

        print("\nAll screenshots captured successfully!")

    finally:
        streamlit_proc.terminate()
        try:
            streamlit_proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            streamlit_proc.kill()
        kill_streamlit()
        print("Streamlit server stopped.")


if __name__ == "__main__":
    capture()