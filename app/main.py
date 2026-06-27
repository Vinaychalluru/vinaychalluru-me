import asyncio
import json
import logging
import os
import uuid
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import (
    APP_METADATA,
    FAVICON_EXISTS,
    FAVICON_PATH,
    PROFILE_DATA,
    RESUME_FILENAME,
    RESUME_PATH,
    STATIC_DIR,
    TEMPLATES_DIR,
)

logging.basicConfig(level=logging.WARNING, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)

MAX_MESSAGE_CHARS = 2000

SYSTEM_PROMPT_TEMPLATE = """\
You are Vinay Kumar Challuru's professional AI assistant. Answer questions about Vinay naturally and directly, as if you know him well. Be accurate, concise, and professional. Only use the information below — if a question cannot be answered from it, say so honestly without guessing.

{context}"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    from rag.embedder import make_embedder
    from rag.vector_store import make_vector_store
    from rag.llm import make_llm
    from rag.session import SessionStore

    app.state.embedder = make_embedder()
    app.state.vector_store = make_vector_store(vector_size=app.state.embedder.dimension)
    app.state.llm = make_llm()
    app.state.session_store = SessionStore(
        ttl_seconds=int(os.environ.get("SESSION_TTL_SECONDS", "3600"))
    )
    yield


app = FastAPI(**APP_METADATA, lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Unhandled exception occurred: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred. Please try again later."},
    )


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    if FAVICON_EXISTS:
        return FileResponse(str(FAVICON_PATH))
    return JSONResponse(status_code=404, content={"detail": "Not Found"})


@app.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    try:
        return templates.TemplateResponse(
            "profile.html", {"request": request, "profile": PROFILE_DATA}
        )
    except Exception as e:
        logger.error(f"Error rendering home page: {e}")
        raise HTTPException(status_code=500, detail="Error loading the profile page.")


@app.get("/download-resume")
async def download_resume() -> FileResponse:
    try:
        if not RESUME_PATH.exists():
            logger.error(f"Resume file not found at path: {RESUME_PATH}")
            raise HTTPException(status_code=404, detail="Resume file not found.")
        return FileResponse(
            str(RESUME_PATH), media_type="application/pdf", filename=RESUME_FILENAME
        )
    except Exception as e:
        logger.error(f"Unexpected error serving resume: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not process resume download.")


@app.post("/api/chat")
async def chat(request: Request):
    from rag.mmr import mmr_select

    body = await request.json()
    message: str = body.get("message", "")
    if not message.strip():
        raise HTTPException(status_code=400, detail="message must not be empty")

    if len(message) > MAX_MESSAGE_CHARS:
        raise HTTPException(status_code=400, detail=f"message too long (max {MAX_MESSAGE_CHARS} chars)")

    embedder = request.app.state.embedder
    vector_store = request.app.state.vector_store
    llm = request.app.state.llm
    session_store = request.app.state.session_store

    session_id = request.cookies.get("session_id")
    if session_id is None:
        session_id = str(uuid.uuid4())

    history = await session_store.get_messages(session_id)

    query_embedding = await asyncio.to_thread(embedder.embed_texts, [message])
    query_embedding = query_embedding[0]

    top_k = 5
    candidates = await vector_store.search(query_embedding, top_k * 3)

    async def generate():
        if not candidates:
            yield 'data: {"token": "I don\'t have enough context to answer that question."}\n\n'
            yield "data: [DONE]\n\n"
            await session_store.append_messages(session_id, [
                {"role": "user", "content": message},
                {"role": "assistant", "content": "I don't have enough context to answer that question."},
            ])
            return

        candidate_pairs = [(chunk, score) for chunk, score, _ in candidates]
        candidate_embeddings = [emb for _, _, emb in candidates]

        selected_chunks = mmr_select(
            query_embedding=query_embedding,
            candidates=candidate_pairs,
            candidate_embeddings=candidate_embeddings,
            k=top_k,
            lambda_=0.5,
        )

        context = "\n\n".join(
            f"[{chunk.source}] {chunk.section}:\n{chunk.text}" for chunk in selected_chunks
        )
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(context=context)
        messages = (
            [{"role": "system", "content": system_prompt}]
            + history[-10:]
            + [{"role": "user", "content": message}]
        )

        full_response = ""
        try:
            async for token in llm.stream(messages):
                full_response += token
                yield f"data: {json.dumps({'token': token})}\n\n"
        except Exception as exc:
            logger.error("LLM streaming error: %s", exc)
            yield 'data: {"error": "LLM unavailable, please try again"}\n\n'
            yield "data: [DONE]\n\n"
            return

        yield "data: [DONE]\n\n"

        await session_store.append_messages(session_id, [
            {"role": "user", "content": message},
            {"role": "assistant", "content": full_response},
        ])

    is_dev = os.environ.get("ENVIRONMENT", "production") == "development"
    response = StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
    response.set_cookie(
        "session_id", session_id,
        httponly=True,
        samesite="lax",
        secure=not is_dev,
    )
    return response


@app.post("/api/ingest")
async def ingest(request: Request):
    from rag.ingestion.pipeline import run_ingest

    secret = os.environ.get("INGEST_SECRET_KEY", "")
    auth_header = request.headers.get("Authorization", "")
    if not secret or auth_header != f"Bearer {secret}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    resume_url = os.environ.get("RESUME_URL", "")
    website_url = os.environ.get("WEBSITE_URL", "https://vinaychalluru.azurewebsites.net/")

    if not resume_url:
        raise HTTPException(status_code=500, detail="RESUME_URL not configured")

    embedder = request.app.state.embedder
    store = request.app.state.vector_store

    # run_ingest blocks until PDF fetch + scrape + embed + upload complete.
    # Azure Functions HTTP trigger has a ~230s front-door timeout.
    # For large corpora, move ingest to a Durable Function or trigger it
    # outside the HTTP path. For a personal resume this is safe in practice.
    result = await run_ingest(
        resume_url=resume_url,
        website_url=website_url,
        embedder=embedder,
        store=store,
    )
    return JSONResponse(content=result)


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
