import asyncio
from app.engine import calculate_unit_economics,compare_fulfillment_options,generate_roadmap,compare_business_models

def test_unit_economics():
    r=calculate_unit_economics(100,40,10,5,eBay_fee=12,ad_cost=3)
    assert r["total_cost_if_fee_supplied"]==70
    assert r["estimated_net_profit_if_fee_supplied"]==30

def test_fulfillment_sort():
    r=compare_fulfillment_options([{"name":"A","monthly_storage":100,"inbound":50,"pick_pack":5,"expected_orders":10},{"name":"B","monthly_storage":50,"inbound":25,"pick_pack":3,"expected_orders":10}])
    assert r["options"][0]["name"]=="B"

def test_roadmap():
    r=generate_roadmap("US","EBAY_US","wholesale_dropshipping","PK")
    assert len(r["steps"])>=10

def test_models():
    r=asyncio.run(compare_business_models("US",["wholesale_dropshipping"]))
    assert r["rows"][0]["status"]=="NEEDS_VERIFICATION"
