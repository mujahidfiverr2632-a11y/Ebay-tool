import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "ebay-cross-border-intelligence")
    app_version: str = os.getenv("APP_VERSION", "0.1.0")
    ebay_env: str = os.getenv("EBAY_ENV", "production")
    ebay_client_id: str | None = os.getenv("EBAY_CLIENT_ID") or None
    ebay_client_secret: str | None = os.getenv("EBAY_CLIENT_SECRET") or None
    tavily_api_key: str | None = os.getenv("TAVILY_API_KEY") or None
    mcp_auth_token: str | None = os.getenv("MCP_AUTH_TOKEN") or None
    http_timeout_seconds: float = float(os.getenv("HTTP_TIMEOUT_SECONDS", "20"))
    max_evidence_chars: int = int(os.getenv("MAX_EVIDENCE_CHARS", "6000"))

settings = Settings()
