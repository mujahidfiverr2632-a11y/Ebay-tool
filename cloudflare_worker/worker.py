import os
import importlib
from contextlib import asynccontextmanager

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

from workers import asgi, WorkerEntrypoint


_APP = None


def _load_runtime_app():
    """
    Load the MCP server after Cloudflare secrets are copied into os.environ.
    This keeps the existing Python business logic reusable.
    """
    global _APP
    if _APP is not None:
        return _APP

    mcp_module = importlib.import_module("server")
    mcp = mcp_module.mcp

    from mcp.server.transport_security import TransportSecuritySettings

    security = TransportSecuritySettings(
        enable_dns_rebinding_protection=False
    )

    mcp_app = mcp.streamable_http_app(
        transport_security=security,
        json_response=True,
        stateless_http=True,
    )

    @asynccontextmanager
    async def lifespan(app):
        async with mcp.session_manager.run():
            yield

    async def health(request):
        return JSONResponse({
            "ok": True,
            "service": "eBay Cross-Border Intelligence",
            "transport": "Streamable HTTP",
            "endpoint": "/mcp",
        })

    _APP = Starlette(
        routes=[
            Route("/health", health, methods=["GET"]),
            Mount("/", app=mcp_app),
        ],
        lifespan=lifespan,
    )
    return _APP


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        # Cloudflare runtime secrets are exposed through self.env.
        # Copy only the secrets this project actually uses.
        for key in (
            "EBAY_ENV",
            "EBAY_CLIENT_ID",
            "EBAY_CLIENT_SECRET",
            "TAVILY_API_KEY",
            "MCP_AUTH_TOKEN",
            "HTTP_TIMEOUT_SECONDS",
            "MAX_EVIDENCE_CHARS",
            "APP_NAME",
            "APP_VERSION",
        ):
            value = getattr(self.env, key, None)
            if value is not None:
                os.environ[key] = str(value)

        app = _load_runtime_app()
        return await asgi.fetch(app, request, self.env)
