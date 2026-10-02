from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from .config import settings
from .mcp_protocol import handle_rpc

app=FastAPI(title=settings.app_name,version=settings.app_version)

@app.get("/health")
def health(): return {"ok":True,"service":settings.app_name,"version":settings.app_version}

@app.get("/config")
def config_status(): return {"ebay_configured":bool(settings.ebay_client_id and settings.ebay_client_secret),"supplier_search_configured":bool(settings.tavily_api_key),"mcp_auth_enabled":bool(settings.mcp_auth_token)}

@app.post("/mcp")
async def mcp(request:Request):
    if settings.mcp_auth_token and request.headers.get("authorization","") != f"Bearer {settings.mcp_auth_token}": return JSONResponse({"error":"Unauthorized"},status_code=401)
    return await handle_rpc(request,await request.json())
