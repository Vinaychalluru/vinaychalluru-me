import asyncio
import io
import httpx
import pdfplumber
from bs4 import BeautifulSoup

_SECTION_SELECTORS: list[tuple[str, list[str]]] = [
    ("hero", ["#hero", ".hero", "section.hero"]),
    ("about", ["#about", ".about", "section#about"]),
    ("ai-practice", ["#ai-practice", ".ai-practice", "section#ai-practice"]),
    ("skills", ["#skills", "#expertise", ".skills", "section#skills"]),
    ("experience", ["#experience", ".experience", "#work", "section#experience"]),
    ("awards", ["#awards", ".awards", "#achievements", "section#awards"]),
    ("contact", ["#contact", ".contact", "section#contact"]),
]


async def fetch_pdf_text(url: str) -> str:
    async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
        response = await client.get(url)
        response.raise_for_status()

    def _parse(content: bytes) -> str:
        text_parts: list[str] = []
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text.strip())
        return "\n\n".join(text_parts)

    return await asyncio.to_thread(_parse, response.content)


async def scrape_website_sections(url: str) -> list[dict[str, str]]:
    async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
        response = await client.get(url)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
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
