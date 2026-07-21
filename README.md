# Vinay Challuru — Portfolio Website

Personal portfolio website for Vinay Challuru, Solution Architect & AI Engineer. Built with FastAPI and deployed on Azure Functions.

Live: [vinaychalluru.azurewebsites.net](https://vinaychalluru.azurewebsites.net)

## Tech Stack

- **Backend:** FastAPI (ASGI), Jinja2 templates
- **RAG chat:** Azure AI Search · Azure OpenAI (`text-embedding-3-small`) · Claude (Anthropic)
- **Frontend:** Bootstrap 5, Font Awesome, AOS (Animate on Scroll), marked.js (markdown rendering in chat)
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
│       ├── loader.py        # PDF + HTML reads from local filesystem (pdfplumber, bs4)
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

> **Suppressing the AzureWebJobsStorage warning:** You'll see an `Unhealthy` log every 30s because `AzureWebJobsStorage` is empty. This doesn't affect HTTP-trigger functions but is noisy. To silence it, install [Azurite](https://learn.microsoft.com/azure/storage/common/storage-use-azurite) and run it in a separate terminal before `func start`:
> ```bash
> npm install -g azurite
> azurite --location /tmp/azurite
> ```
> Then set `"AzureWebJobsStorage": "UseDevelopmentStorage=true"` in `local.settings.json`.

> **Alternative (UI only, no RAG):** If you only need to check the portfolio page and don't need the chat endpoints, uvicorn is faster:
> ```bash
> python -m uvicorn app.main:app --reload --port 8000
> ```
> The chat widget will appear but `/api/chat` calls will fail because the RAG components need `local.settings.json` values injected by `func start`.

### 5. Search index

Ingest is **not** triggered automatically — it used to run in the FastAPI lifespan on every cold start, but that meant every visitor after an idle period paid the ~5s+ ingest cost. It's now a manual/CI-triggered step (see [Deployment](#deployment) for how production handles this).

For local dev, trigger it once yourself after `func start` is up:

```bash
curl -X POST http://localhost:7071/api/ingest \
  -H "Authorization: Bearer <your-INGEST_SECRET_KEY>"
```

The app reads the resume PDF and HTML template directly from disk, embeds them, and uploads to Azure AI Search. You'll see log lines like:

```
WARNING:rag.ingestion.pipeline:Ingest started
WARNING:rag.ingestion.pipeline:Ingest complete: {'total_chunks': 87, 'resume_chunks': 42, ...}
```

Re-run this any time you update the resume PDF or the HTML template's content.

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

The GitHub Actions workflow (`.github/workflows/main_vinaychalluru.yml`) triggers ingest automatically once per deploy — after `deploy-to-function` succeeds, it calls `POST /api/ingest` with retries (the app may still be provisioning right after deploy). This requires an `INGEST_SECRET_KEY` GitHub Actions secret matching the value set as an Azure Function App setting. No manual step is needed for normal deploys; re-deploying after a resume PDF or template change rebuilds the index automatically as part of that same deploy.
