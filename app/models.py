from typing import Any, Literal
from pydantic import BaseModel, Field

Confidence = Literal["high", "medium", "low", "unknown"]
Status = Literal["VERIFIED", "NEEDS_VERIFICATION", "NOT_VERIFIED"]

class Evidence(BaseModel):
    title: str
    url: str
    source_type: str
    checked_at_utc: str
    excerpt: str = ""
    status: Status = "VERIFIED"
    confidence: Confidence = "medium"

class ResearchResult(BaseModel):
    subject: str
    market: dict[str, Any]
    findings: list[dict[str, Any]]
    evidence: list[Evidence]
    warnings: list[str] = []

class SupplierCandidate(BaseModel):
    name: str
    url: str
    country: str | None = None
    warehouse_locations: list[str] = []
    business_models: list[str] = []
    notes: str = ""
    evidence: list[Evidence] = []
    score: float | None = None
    score_breakdown: dict[str, float] = {}

class ProductCandidate(BaseModel):
    title: str
    item_id: str | None = None
    marketplace_id: str
    price: float | None = None
    currency: str | None = None
    seller: str | None = None
    shipping_cost: float | None = None
    item_url: str | None = None
    category_id: str | None = None
    evidence: list[Evidence] = []
    risk_flags: list[str] = []

class MCPToolCall(BaseModel):
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
