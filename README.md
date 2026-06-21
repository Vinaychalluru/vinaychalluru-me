# Vinay Challuru — Portfolio Website

Personal portfolio website for Vinay Challuru, Solution Architect & AI Engineer. Built with FastAPI and deployed on Azure Functions.

Live: [vinaychalluru.azurewebsites.net](https://vinaychalluru.azurewebsites.net)

## Tech Stack

- **Backend:** FastAPI (ASGI), Jinja2 templates
- **Frontend:** Bootstrap 5, Font Awesome, AOS (Animate on Scroll)
- **PDF generation:** ReportLab (`generate_resume.py`)
- **Deployment:** Azure Functions (ASGI wrapper via `function_app.py`)
- **CI/CD:** GitHub Actions

## Project Structure

```text
vinaychalluru-me/
├── app/
│   ├── config.py            # Paths, resume filename, profile metadata
│   ├── main.py              # FastAPI app — routes: /, /download-resume, /favicon.ico
│   ├── templates/
│   │   └── profile.html     # Single-page portfolio template
│   └── staticfiles/
│       └── about/
│           ├── css/
│           ├── js/
│           ├── icons/
│           ├── images/
│           └── files/       # Resume PDF served at /download-resume
├── generate_resume.py       # ReportLab PDF generator — run to rebuild the PDF
├── function_app.py          # Azure Functions ASGI entry point
├── host.json                # Azure Functions host config
├── local.settings.json      # Local Azure Functions settings (not committed)
├── requirements.in          # Direct dependencies
└── requirements.txt         # Pinned lockfile
```

## Development Setup

1. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv_fastapi
   source .venv_fastapi/bin/activate   # macOS/Linux
   .\.venv_fastapi\Scripts\activate    # Windows
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.in
   ```

3. Run the dev server:

   ```bash
   python -m uvicorn app.main:app --reload --port 8000
   ```

   > Use `python -m uvicorn` (not the `uvicorn` script directly) to avoid venv shebang issues.

4. Visit [http://localhost:8000](http://localhost:8000)

## Regenerating the Resume PDF

The PDF is committed to the repo and served statically. To rebuild it after editing `generate_resume.py`:

```bash
# Install reportlab if not already present
pip install reportlab

# Regenerate
python generate_resume.py
```

Output path: `app/staticfiles/about/files/Vinay_AI_Architect_Resume.pdf`

Always `git add` the PDF after regenerating before committing.

## Deployment

Deployed to Azure Functions via GitHub Actions on push to `main`. The ASGI app is wrapped in `function_app.py` using `func.AsgiFunctionApp`.
