from pathlib import Path

# Get the base directory
BASE_DIR = Path(__file__).resolve().parent

# Static files and templates directories
STATIC_DIR = BASE_DIR / "staticfiles"
TEMPLATES_DIR = BASE_DIR / "templates"

# Resume file
RESUME_FILENAME = "Vinay_12Y_Solution_Architect.pdf"
RESUME_PATH = STATIC_DIR / "about" / "files" / RESUME_FILENAME

# Profile data
PROFILE_DATA = {
    "name": "Vinay Challuru",
    "title": "Software Engineer",
    "bio": "Passionate about building innovative solutions and learning new technologies.",
    "email": "challuru.vinay@gmail.com",
    "github": "https://github.com/vinaychalluru",
    "linkedin": "https://linkedin.com/in/vinaychalluru"
}

# Application metadata
APP_METADATA = {
    "title": "Vinay Challuru Portfolio",
    "description": "Personal portfolio website showcasing professional experience and skills",
    "version": "1.0.0"
} 