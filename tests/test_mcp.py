from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)

def test_health():
    r=client.get("/health"); assert r.status_code==200; assert r.json()["ok"] is True

def test_tools_list():
    r=client.post("/mcp",json={"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}})
    assert r.status_code==200
    names=[x["name"] for x in r.json()["result"]["tools"]]
    assert "full_market_research" in names
    assert "hunt_ebay_products" in names
