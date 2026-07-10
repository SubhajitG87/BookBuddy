# 📚 BookBuddy

**AI-powered Goodreads reading history analyzer — decode your literary DNA.**

Upload your Goodreads library export and BookBuddy will:
- 📊 **Visualize your reading stats** — books per year, rating distribution, top authors, genre breakdown
- 🧬 **Generate your Reader DNA** — a 150-word AI profile of your reading personality
- 📖 **Recommend 5 new books** — tailored to your specific taste, with personalized explanations

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Get a HuggingFace token (free)
Visit [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) and create a free token.

### 3. Configure your token
```bash
cp .env.example .env
# Edit .env and paste your token:
# HF_TOKEN=hf_yourActualTokenHere
```

### 4. Run the app
```bash
streamlit run app.py
```

### 5. Export your Goodreads library
Go to Goodreads → **My Books** → **Import/Export** → **Export Library** → download the CSV.

Upload it in the sidebar and BookBuddy does the rest.

---

## 🤖 AI Backend

BookBuddy uses the **HuggingFace Inference API free tier** — no paid subscription needed. Select from three free models in the sidebar:

| Model | Description |
|-------|-------------|
| **Mistral-7B** | Fast, solid all-rounder |
| **Llama-3.1-8B** | Meta's flagship open model |
| **Gemma-2-9B** | Google's lightweight model |

> ⚡ **Runs free on the HuggingFace Inference API free tier.** Only a `HF_TOKEN` is required (free to create).

---

## 🧬 Sample Reader DNA

Here's what BookBuddy might say about a reader who devours epic fantasy, speculative thrillers, and literary fiction:

> *You're a reader who craves epic scope with intimate character work — the kind where a 700-page fantasy novel feels like a conversation with an old friend. You gravitate toward morally complex protagonists in richly built worlds (Gwynne, Abercrombie, Jemisin), but you'll equally devour a tight speculative thriller (Crouch, Weir) or literary fiction that plays with structure (Doerr, Zevin). Your 5-star shelf reveals a hunger for narratives that respect your intelligence: layered magic systems that feel earned, prose that sings without showing off, and endings that linger. You don't just read for plot — you read for voice, for the particular alchemy of an author who makes the impossible feel inevitable.*

---

## 📊 Features

### Tab 1 — My Stats (no AI)
- 📚 Books read per year (bar chart)
- ⭐ Rating distribution (histogram)
- ✍️ Top 10 authors by book count
- 🎨 Genre breakdown (pie chart, inferred from shelves+reviews)
- 📄 Total pages read

All charts powered by **Plotly** with a dark Goodreads+Claude gradient theme.

### Tab 2 — Reader DNA (AI-powered)
Filters your 4–5 star books and sends them to the LLM. The AI writes a 150-word paragraph profiling your reading personality — what themes you gravitate toward, what writing styles you love, what you seek in a book.

### Tab 3 — Recommendations (AI-powered)
Uses your Reader DNA + full reading history to recommend 5 books you haven't read but would love. Each recommendation comes with a 2-sentence reason tied to your specific taste. **Download everything as a Markdown file.**

---

## 📁 Project Structure

```
BookBuddy/
├── app.py                 # Streamlit entry point
├── requirements.txt       # Python dependencies
├── .env.example           # HF_TOKEN template
├── README.md
├── .gitignore
└── src/
    ├── __init__.py
    ├── llm_client.py      # HuggingFace Inference API abstraction
    ├── data_processor.py  # CSV parsing, stats, genre inference
    ├── charts.py          # Plotly visualizations (Goodreads+Claude theme)
    ├── prompts.py         # AI prompt templates
    └── ui_components.py   # Styled cards, sidebar, Markdown export
```

---

## 📦 Dependencies

| Package | License |
|---------|---------|
| streamlit | Apache 2.0 |
| pandas | BSD 3-Clause |
| plotly | MIT |
| huggingface_hub | MIT |
| python-dotenv | MIT |

All dependencies are MIT or Apache 2.0 licensed.

---

## 🔧 Requirements

- Python 3.10+
- HuggingFace API token (free tier)
- Goodreads CSV export

---

*Built with ❤️ using Streamlit, Plotly, and HuggingFace AI*