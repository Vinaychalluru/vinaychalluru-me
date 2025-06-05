from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging
import uvicorn
from pathlib import Path

from .config import (
    STATIC_DIR,
    TEMPLATES_DIR,
    RESUME_PATH,
    RESUME_FILENAME,
    PROFILE_DATA,
    APP_METADATA
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(**APP_METADATA)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    """
    Render the main profile page.
    
    Args:
        request: The incoming request object
        
    Returns:
        HTMLResponse: The rendered profile page
    """
    return templates.TemplateResponse(
        "profile.html",
        {"request": request, "profile": PROFILE_DATA}
    )

@app.get("/download-resume")
async def download_resume() -> FileResponse:
    """
    Download the resume PDF file.
    
    Returns:
        FileResponse: The resume file
    """
    try:
        logger.info(f"Looking for resume at: {RESUME_PATH}")
        
        if not RESUME_PATH.exists():
            logger.error(f"Resume file not found at path: {RESUME_PATH}")
            raise FileNotFoundError(f"Resume file not found at path: {RESUME_PATH}")
            
        logger.info(f"Found resume file at: {RESUME_PATH}")
        return FileResponse(
            str(RESUME_PATH),
            media_type="application/pdf",
            filename=RESUME_FILENAME
        )
    except Exception as e:
        logger.error(f"Error downloading resume: {str(e)}")
        raise

if __name__ == "__main__":
    logging.info("Starting the application")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 