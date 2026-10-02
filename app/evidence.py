from __future__ import annotations
from datetime import datetime, timezone
import re
import httpx
from bs4 import BeautifulSoup
from .config import settings
from .models import Evidence

def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()

def _clean(text: str) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    return text[: settings.max_evidence_chars]

async def fetch_page(url: str, source_type: str = "web") -> Evidence:
    checked = now_utc()
    try:
        async with httpx.AsyncClient(timeout=settings.http_timeout_seconds, follow_redirects=True, headers={"User-Agent": "eBay-Cross-Border-Intelligence/0.1"}) as client:
            r = await client.get(url)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            title = _clean(soup.title.get_text(" ", strip=True) if soup.title else url)
            for tag in soup(["script", "style", "noscript"]):
                tag.decompose()
            body = _clean(soup.get_text(" ", strip=True))
            return Evidence(title=title or url, url=str(r.url), source_type=source_type, checked_at_utc=checked, excerpt=body, status="VERIFIED", confidence="high")
    except Exception as exc:
        return Evidence(title=url, url=url, source_type=source_type, checked_at_utc=checked, excerpt=f"Fetch failed: {type(exc).__name__}: {exc}", status="NOT_VERIFIED", confidence="unknown")
