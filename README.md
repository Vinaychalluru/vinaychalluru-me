# Vinay Challuru — Portfolio Website

Personal portfolio website for Vinay Challuru, Solution Architect & AI Engineer. Built with FastAPI and deployed on Azure Functions.

Live: [vinaychalluru.azurewebsites.net](https://vinaychalluru.azurewebsites.net)

## Tech Stack

- **Backend:** FastAPI (ASGI), Jinja2 templates
- **RAG chat:** Azure AI Search · Azure OpenAI (`text-embedding-3-small`) · Claude (Anthropic)
- **Frontend:** Bootstrap 5, Font Awesome, AOS (Animate on Scroll)
- **PDF generation:** ReportLab (`generate_resume.py`)
- **Deployment:** Azure Functions (ASGI wrapper via `function_app.py`)
- **CI/CD:** GitHub Actions

## Project Structure

```text
vinaychalluru-me/
├── app/
│   ├── config.py            # Paths, resume filename, profile metadata
│   ├── main.py              # FastAPI app — routes: /, /download-resume, /api/chat, /api/ingest
│   ├── templates/
│   │   └── profile.html     # Single-page portfolio (includes floating chat widget)
│   └── staticfiles/
│       └── about/
│           └── files/       # Resume PDF served at /download-resume
├── rag/                     # RAG pipeline (Azure-only, no Qdrant/Ollama)
│   ├── _math.py             # Shared cosine_sim()
│   ├── types.py             # Chunk dataclass
│   ├── embedder.py          # AzureEmbedder (text-embedding-3-small, 1536-dim)
│   ├── vector_store.py      # AzureSearchStore (HNSW, retrievable embeddings)
│   ├── mmr.py               # Maximum Marginal Relevance reranking
│   ├── llm.py               # ClaudeClient (async streaming)
│   ├── session.py           # In-memory session store (TTL-based)
│   └── ingestion/
│       ├── loader.py        # PDF fetch (httpx+pdfplumber) + site scraper (bs4)
│       ├── chunker.py       # Sliding-window token chunker (cl100k_base, 512t)
│       ├── deduplicator.py  # Cosine dedup (threshold 0.97, resume wins ties)
│       └── pipeline.py      # run_ingest() orchestrator
├── generate_resume.py       # ReportLab PDF generator
├── function_app.py          # Azure Functions ASGI entry point
├── host.json                # Azure Functions host config
├── local.settings.json      # Local dev settings — fill in credentials (git-ignored)
├── requirements.in          # Direct dependencies
└── requirements.txt         # Pinned lockfile (pip-compile generated)
```

---

## Local Development Setup

### Prerequisites

- Python 3.11+
- [Azure Functions Core Tools v4](https://learn.microsoft.com/azure/azure-functions/functions-run-local) (`npm install -g azure-functions-core-tools@4`)
- Active Azure resources: **Azure AI Search**, **Azure OpenAI** (with `text-embedding-3-small` deployed), **Anthropic API key**

### 1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS/Linux
.\.venv\Scripts\activate         # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure local settings

`local.settings.json` is git-ignored. It ships as a placeholder template on the branch — fill in your real credentials:

```json
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsStorage": "",
    "ENVIRONMENT": "development",
    "CLAUDE_API_KEY": "<your-anthropic-api-key>",
    "CLAUDE_MODEL": "claude-sonnet-4-6",
    "AZURE_SEARCH_ENDPOINT": "https://<name>.search.windows.net",
    "AZURE_SEARCH_KEY": "<admin-key>",
    "AZURE_SEARCH_INDEX": "vc-profile",
    "AZURE_OPENAI_ENDPOINT": "https://<name>.openai.azure.com",
    "AZURE_OPENAI_KEY": "<key>",
    "AZURE_OPENAI_EMBEDDING_DEPLOYMENT": "text-embedding-3-small",
    "INGEST_SECRET_KEY": "<any-random-string>",
    "SESSION_TTL_SECONDS": "3600"
  },
  "ConnectionStrings": {}
}
```

Prevent git from ever tracking this file after you populate it:

```bash
git update-index --skip-worktree local.settings.json
```

### 4. Start the app

Use the Azure Functions Core Tools — this is the only way that loads `local.settings.json` and routes `/api/chat` and `/api/ingest` correctly:

```bash
func start
```

The app will be available at **http://localhost:7071**.

> **Alternative (UI only, no RAG):** If you only need to check the portfolio page and don't need the chat endpoints, uvicorn is faster:
> ```bash
> python -m uvicorn app.main:app --reload --port 8000
> ```
> The chat widget will appear but `/api/chat` calls will fail because the RAG components need `local.settings.json` values injected by `func start`.

### 5. Search index

Ingest runs **automatically on every app startup** — the app reads the resume PDF and HTML template directly from disk (no HTTP round-trip), embeds them, and uploads to Azure AI Search. You'll see a log line like:

```
WARNING:app.main:Startup ingest complete: {'total_chunks': 87, 'resume_chunks': 42, ...}
```

This takes ~5 seconds. No manual trigger needed.

**Force re-ingest** (e.g. after updating the resume PDF):

```bash
curl -X POST http://localhost:7071/api/ingest \
  -H "Authorization: Bearer <your-INGEST_SECRET_KEY>"
```

### 6. Test the chat

Open **http://localhost:7071** in a browser. Click the purple chat button in the bottom-right corner and ask a question, e.g. *"What cloud platforms has Vinay worked with?"*

You should see tokens stream in word-by-word as the response is generated.

**Manual curl test:**

```bash
curl -X POST http://localhost:7071/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Vinay's experience with Azure?"}'
```

Expected: an `text/event-stream` response with `data: {"token": "..."}` lines ending in `data: [DONE]`.

---

## Regenerating the Resume PDF

```bash
pip install reportlab
python generate_resume.py
```

Output: `app/staticfiles/about/files/Vinay_AI_Architect_Resume.pdf` — commit the PDF after regenerating, then re-run ingest so the index reflects the new content.

---

## Deployment

Deployed to Azure Functions via GitHub Actions on push to `main`. The ASGI app is wrapped in `function_app.py` using `func.AsgiFunctionApp`.

**After deploying, add all `local.settings.json` keys as Application Settings** in the Azure Portal (Function App → Settings → Environment variables), except `AzureWebJobsStorage` (already set by Azure) and `ENVIRONMENT` (set to `production`).

Ingest runs automatically on every cold start, so no manual trigger is needed after the first deploy. Re-deploy any time the resume PDF or template changes — ingest will rebuild the index on the next startup.
