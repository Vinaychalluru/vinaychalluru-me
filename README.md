# Vinay Challuru Portfolio

A personal portfolio website built with FastAPI, showcasing professional experience, skills, and achievements.

## Features

- Responsive design
- Interactive UI with smooth scrolling
- Resume download functionality
- Static file serving
- Azure Functions deployment ready

## Tech Stack

- FastAPI
- Jinja2 Templates
- Bootstrap
- Font Awesome
- Azure Functions

## Development Setup

1. Create a virtual environment:
   ```bash
   python -m venv .venv_fastapi
   ```

2. Activate the virtual environment:
   - Windows:
     ```bash
     .\.venv_fastapi\Scripts\activate
     ```
   - Unix/MacOS:
     ```bash
     source .venv_fastapi/bin/activate
     ```

3. Install dependencies:
   ```bash
   pip install -r requirements.in
   ```

4. Run the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

5. Visit [http://localhost:8000](http://localhost:8000)

## Project Structure

```
vinaychalluru-me/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   ├── static/          # Static files (CSS, JS, images)
│   └── templates/       # Jinja2 templates
├── tests/              # Test files
├── requirements.in     # Project dependencies
└── README.md          # This file
```

## Deployment

The application is configured for deployment on Azure Functions. The deployment process is handled through GitHub Actions.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 