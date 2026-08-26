# RAG POC

A minimal Retrieval-Augmented Generation proof of concept that ingests one `.xlsx` and one `.docx` file, stores embeddings in **FAISS**, and answers questions with **Google Gemini** via a **Streamlit** UI.

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager

## Setup

1. Install dependencies:

```bash
uv sync
```

2. Configure your API key:

```bash
copy .env.example .env
```

Edit `.env` and set:

```text
EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=your-openai-key-here
GEMINI_API_KEY=your-gemini-key-here
```

- **Embeddings** (default): OpenAI `text-embedding-3-small`
- **Answers**: Gemini `gemini-3.6-flash`

To use Gemini for embeddings instead, set `EMBEDDING_PROVIDER=gemini`.

## Run

```bash
uv run streamlit run src/rag_poc/app.py
```

## Usage

1. Open the Streamlit app in your browser.
2. Upload one `.xlsx` and/or one `.docx` file in the sidebar.
3. Click **Build index** to chunk, embed, and persist the FAISS index.
4. Ask questions in the chat box.
5. Expand **Sources** to see which document chunks were retrieved.

If a persisted index exists in `storage/`, the app auto-loads it on startup.

## Example questions

- "What products are listed in the Excel sheet?"
- "What is the refund policy mentioned in the Word document?"
- "What is the total revenue for Widget A?"

## Project structure

```text
src/rag_poc/
├── app.py          # Streamlit UI
├── config.py       # Settings and paths
├── loaders.py      # xlsx/docx parsing
├── chunking.py     # Text chunking
├── embeddings.py   # OpenAI or Gemini embeddings
├── vectorstore.py  # FAISS index
└── rag.py          # Retrieve + generate
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `OPENAI_API_KEY is not set` | Add your OpenAI key when `EMBEDDING_PROVIDER=openai` |
| `GEMINI_API_KEY is not set` | Add your Gemini key (required for chat answers) |
| Index not ready | Upload files and click **Build index** |
| Embedding provider mismatch | Rebuild index after changing `EMBEDDING_PROVIDER` |
| Empty answers | Ensure files contain readable text/tables |

## Smoke test (optional)

Generate sample files and run a local ingest test:

```bash
uv run python scripts/create_samples.py
uv run python scripts/smoke_test.py
```

The smoke test requires `OPENAI_API_KEY` and `GEMINI_API_KEY` in `.env` (with default `EMBEDDING_PROVIDER=openai`).
