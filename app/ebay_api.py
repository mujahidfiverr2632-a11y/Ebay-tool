from __future__ import annotations
import base64
from datetime import datetime, timedelta, timezone
from typing import Any
import httpx
from .config import settings
from .evidence import now_utc
from .models import Evidence, ProductCandidate

class EbayAPIError(RuntimeError):
    pass

class EbayClient:
    def __init__(self) -> None:
        self.base = "https://api.ebay.com" if settings.ebay_env == "production" else "https://api.sandbox.ebay.com"
        self._token: tuple[str, datetime] | None = None

    def available(self) -> bool:
        return bool(settings.ebay_client_id and settings.ebay_client_secret)

    async def app_token(self) -> str:
        if not self.available():
            raise EbayAPIError("eBay application credentials are not configured")
        if self._token and self._token[1] > datetime.now(timezone.utc) + timedelta(seconds=30):
            return self._token[0]
        raw = f"{settings.ebay_client_id}:{settings.ebay_client_secret}".encode()
        basic = base64.b64encode(raw).decode()
        async with httpx.AsyncClient(timeout=settings.http_timeout_seconds) as client:
            r = await client.post(
                f"{self.base}/identity/v1/oauth2/token",
                headers={"Authorization": f"Basic {basic}", "Content-Type": "application/x-www-form-urlencoded"},
                data={"grant_type": "client_credentials", "scope": "https://api.ebay.com/oauth/api_scope"},
            )
            if r.status_code >= 400:
                raise EbayAPIError(f"eBay OAuth failed: {r.status_code} {r.text[:1000]}")
            data = r.json()
        expires = int(data.get("expires_in", 7200))
        self._token = (data["access_token"], datetime.now(timezone.utc) + timedelta(seconds=expires))
        return self._token[0]

    async def search_items(self, marketplace_id: str, query: str, limit: int = 20) -> list[ProductCandidate]:
        token = await self.app_token()
        async with httpx.AsyncClient(timeout=settings.http_timeout_seconds) as client:
            r = await client.get(
                f"{self.base}/buy/browse/v1/item_summary/search",
                headers={"Authorization": f"Bearer {token}", "X-EBAY-C-MARKETPLACE-ID": marketplace_id, "Accept-Language": "en-US"},
                params={"q": query, "limit": min(max(limit, 1), 200)},
            )
            if r.status_code >= 400:
                raise EbayAPIError(f"eBay Browse search failed: {r.status_code} {r.text[:1000]}")
            data: dict[str, Any] = r.json()
        out: list[ProductCandidate] = []
        evidence = Evidence(title=f"eBay Browse API search: {query}", url="https://developer.ebay.com/api-docs/buy/browse/overview.html", source_type="ebay_api", checked_at_utc=now_utc(), excerpt="Live eBay Browse API response", status="VERIFIED", confidence="high")
        for item in data.get("itemSummaries", []):
            price = item.get("price") or {}
            shipping = item.get("shippingOptions", [{}])[0].get("shippingCost") or {} if item.get("shippingOptions") else {}
            out.append(ProductCandidate(
                title=item.get("title", ""), item_id=item.get("itemId"), marketplace_id=marketplace_id,
                price=float(price.get("value")) if price.get("value") is not None else None,
                currency=price.get("currency"), seller=(item.get("seller") or {}).get("username"),
                shipping_cost=float(shipping.get("value")) if shipping.get("value") is not None else None,
                item_url=item.get("itemWebUrl"), category_id=item.get("leafCategoryIds", [None])[0], evidence=[evidence],
            ))
        return out

ebay = EbayClient()
