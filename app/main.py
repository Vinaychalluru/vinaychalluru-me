from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging
import uvicorn
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse

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

# Add Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:    
    logger.error(f"Unhandled exception occurred: {str(exc)}", exc_info=True)   
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred. Please try again later."}
    )


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    favicon_path = STATIC_DIR / 'about' / 'icons' / 'VinayChalluru.ico'
    if favicon_path.exists():
        return FileResponse(str(favicon_path))
    return JSONResponse(status_code=404, content={"detail": "Not Found"})

@app.get("/", response_class=HTMLResponse)
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
            "profile.html",
            {"request": request, "profile": PROFILE_DATA}
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
        logger.info(f"Looking for resume at: {RESUME_PATH}")
        # Check if file exists before attempting response
        if not RESUME_PATH.exists():
            logger.error(f"Resume file not found at path: {RESUME_PATH}")
            raise HTTPException(status_code=404, detail="Resume file not found.")
        
        logger.info(f"Serving resume file from: {RESUME_PATH}")
        return FileResponse(
            str(RESUME_PATH),
            media_type="application/pdf",
            filename=RESUME_FILENAME
        )
    except Exception as e:
        logger.error(f"Unexpected error serving resume: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not process resume download.")

if __name__ == "__main__":
    logging.info("Starting the application")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 