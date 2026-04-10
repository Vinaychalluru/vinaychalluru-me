import logging
from logging.handlers import MemoryHandler

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
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

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Implement MemoryHandler for buffering logs
handler = logging.StreamHandler()
formatter = logging.Formatter("%(levelname)s:%(name)s:%(message)s")
handler.setFormatter(formatter)
memory_handler = MemoryHandler(capacity=50, target=handler)

# Remove existing handlers and add the memory handler to the root logger
root_logger = logging.getLogger()
root_logger.handlers.clear()
root_logger.addHandler(memory_handler)

# Create FastAPI app
app = FastAPI(**APP_METADATA)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


# Add Global Exception Handler
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
    """
    Render the main profile page.

    Args:
        request: The incoming request object

    Returns:
        HTMLResponse: The rendered profile page
    """
    try:
        return templates.TemplateResponse(
            "profile.html", {"request": request, "profile": PROFILE_DATA}
        )
    except Exception as e:
        logger.error(f"Error rendering home page: {e}")
        raise HTTPException(status_code=500, detail="Error loading the profile page.")


@app.get("/download-resume")
async def download_resume() -> FileResponse:
    """
    Download the resume PDF file.

    Returns:
        FileResponse: The resume file
    """
    try:
        # Check if file exists before attempting response
        if not RESUME_PATH.exists():
            logger.error(f"Resume file not found at path: {RESUME_PATH}")
            raise HTTPException(status_code=404, detail="Resume file not found.")

        return FileResponse(
            str(RESUME_PATH), media_type="application/pdf", filename=RESUME_FILENAME
        )
    except Exception as e:
        logger.error(f"Unexpected error serving resume: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Could not process resume download."
        )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
