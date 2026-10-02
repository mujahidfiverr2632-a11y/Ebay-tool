from __future__ import annotations
from typing import Any
import httpx
from .config import settings
from .evidence import now_utc
from .models import Evidence

class SearchUnavailable(RuntimeError):
    pass

async def tavily_search(query: str, max_results: int = 10) -> list[Evidence]:
    if not settings.tavily_api_key:
        raise SearchUnavailable("TAVILY_API_KEY is not configured")
    async with httpx.AsyncClient(timeout=settings.http_timeout_seconds) as client:
        r = await client.post("https://api.tavily.com/search", json={"api_key": settings.tavily_api_key, "query": query, "max_results": max_results, "search_depth": "advanced"})
        if r.status_code >= 400:
            raise SearchUnavailable(f"Tavily search failed: {r.status_code}")
        data: dict[str, Any] = r.json()
    out = []
    for item in data.get("results", []):
        out.append(Evidence(title=item.get("title", item.get("url", "")), url=item.get("url", ""), source_type="web_search", checked_at_utc=now_utc(), excerpt=(item.get("content") or "")[:settings.max_evidence_chars], status="VERIFIED", confidence="medium"))
    return out
