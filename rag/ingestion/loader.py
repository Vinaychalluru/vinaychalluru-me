"""
Ingestion loaders — filesystem-direct reads.

The original standalone rag_app fetched the resume PDF and website over HTTP
because it was a separate process with no access to the portfolio's filesystem.
Now that the RAG code lives inside the same Azure Functions app, there is no
reason to go over the network: the PDF is already on disk and the HTML template
is a local file. Reading directly:

  - eliminates the circular HTTP dependency (ingest calling the same process
    that is handling the ingest request)
  - works before the app is publicly reachable (fresh deploys, local dev)
  - removes httpx from the ingest hot-path entirely

All blocking I/O (pdfplumber, file reads) is offloaded to asyncio.to_thread
so it does not stall the event loop.
"""

import asyncio
from pathlib import Path

import pdfplumber
from bs4 import BeautifulSoup

_SECTION_SELECTORS: list[tuple[str, list[str]]] = [
    ("navigation",  ["nav",          ".navbar",      "header"]),
    ("hero",        ["#hero",        ".hero",        "section.hero"]),
    ("about",       ["#about",       ".about",       "section#about"]),
    ("ai-practice", ["#ai-practice", ".ai-practice", "section#ai-practice"]),
    ("skills",      ["#skills",      "#expertise",   ".skills",      "section#skills"]),
    ("experience",  ["#experience",  ".experience",  "#work",        "section#experience"]),
    ("awards",      ["#awards",      ".awards",      "#achievements", "section#awards"]),
    ("contact",     ["#contact",     ".contact",     "section#contact"]),
]


async def fetch_pdf_text(pdf_path: Path) -> str:
    """Extract plain text from the resume PDF on disk."""
    def _parse() -> str:
        text_parts: list[str] = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text.strip())
        return "\n\n".join(text_parts)

    return await asyncio.to_thread(_parse)


async def scrape_website_sections(html_path: Path) -> list[dict[str, str]]:
    """
    Extract labelled text sections from the portfolio HTML template.

    Reads the Jinja2 template file directly. All {{ }} expressions in the
    template are inside href/src attributes, never inside text nodes, so
    BeautifulSoup's get_text() returns clean content with no template noise.
    """
    def _parse() -> list[dict[str, str]]:
        html = html_path.read_text(encoding="utf-8")
        soup = BeautifulSoup(html, "html.parser")
        sections: list[dict[str, str]] = []

        for section_name, selectors in _SECTION_SELECTORS:
            for selector in selectors:
                el = soup.select_one(selector)
                if el:
                    text = el.get_text(separator=" ", strip=True)
                    if text:
                        sections.append({"section": section_name, "text": text})
                    break

        if not sections:
            body = soup.find("body")
            text = body.get_text(separator="\n", strip=True) if body else soup.get_text(separator="\n", strip=True)
            sections.append({"section": "general", "text": text})

        return sections

    return await asyncio.to_thread(_parse)
