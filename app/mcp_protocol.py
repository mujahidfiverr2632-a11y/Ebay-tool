from __future__ import annotations
import json
from typing import Any
from fastapi import Request
from fastapi.responses import JSONResponse
from .engine import research_country,compare_business_models,research_suppliers,hunt_products,calculate_unit_economics,compare_fulfillment_options,check_product_compliance,generate_roadmap,full_market_research,research_marketplace_fees,research_fulfillment_providers
from .evidence import fetch_page

TOOLS={
"research_country":{"description":"Research a seller country and eBay marketplace with live official-source evidence.","inputSchema":{"type":"object","properties":{"country":{"type":"string"},"marketplace":{"type":"string"},"live":{"type":"boolean"}},"required":["country"]}},
"compare_business_models":{"description":"Compare wholesale dropshipping, retail arbitrage, wholesale, and private label.","inputSchema":{"type":"object","properties":{"country":{"type":"string"},"models":{"type":"array","items":{"type":"string"}}},"required":["country"]}},
"research_suppliers":{"description":"Find supplier candidates using live web search and preserve evidence.","inputSchema":{"type":"object","properties":{"country":{"type":"string"},"marketplace":{"type":"string"},"model":{"type":"string"},"niche":{"type":"string"},"budget":{"type":"number"}},"required":["country","marketplace","model","niche"]}},
"research_marketplace_fees":{"description":"Find current marketplace-fee evidence.","inputSchema":{"type":"object","properties":{"marketplace":{"type":"string"},"seller_country":{"type":"string"},"category":{"type":"string"}},"required":["marketplace","seller_country"]}},
"research_fulfillment_providers":{"description":"Find 3PL/fulfillment candidates.","inputSchema":{"type":"object","properties":{"country":{"type":"string"},"destination":{"type":"string"},"niche":{"type":"string"},"provider_type":{"type":"string"}},"required":["country","destination"]}},
"hunt_ebay_products":{"description":"Search live eBay listings through Browse API when configured.","inputSchema":{"type":"object","properties":{"marketplace":{"type":"string"},"query":{"type":"string"},"limit":{"type":"integer"}},"required":["marketplace","query"]}},
"calculate_unit_economics":{"description":"Calculate transparent unit economics without guessing fees.","inputSchema":{"type":"object","properties":{"sale_price":{"type":"number"},"product_cost":{"type":"number"},"shipping_cost":{"type":"number"},"fulfillment_cost":{"type":"number"},"eBay_fee":{"type":"number"},"ad_cost":{"type":"number"},"return_allowance":{"type":"number"},"taxes":{"type":"number"},"other_costs":{"type":"number"}},"required":["sale_price","product_cost"]}},
"compare_fulfillment_options":{"description":"Compare explicit fulfillment/3PL cost inputs.","inputSchema":{"type":"object","properties":{"options":{"type":"array"}},"required":["options"]}},
"check_product_compliance":{"description":"Create a compliance checklist; does not invent legal clearance.","inputSchema":{"type":"object","properties":{"marketplace":{"type":"string"},"buyer_country":{"type":"string"},"product":{"type":"string"},"known_sources":{"type":"array","items":{"type":"string"}}},"required":["marketplace","buyer_country","product"]}},
"generate_execution_roadmap":{"description":"Generate a beginner execution roadmap for a compliant client-owned eBay operation.","inputSchema":{"type":"object","properties":{"country":{"type":"string"},"marketplace":{"type":"string"},"model":{"type":"string"},"operator_country":{"type":"string"},"target":{"type":"string"}},"required":["country","marketplace","model"]}},
"full_market_research":{"description":"Run country, model, supplier, fee, fulfillment and roadmap research.","inputSchema":{"type":"object","properties":{"country":{"type":"string"},"marketplace":{"type":"string"},"model":{"type":"string"},"niche":{"type":"string"},"budget":{"type":"number"}},"required":["country","marketplace","model","niche"]}},
"fetch_evidence":{"description":"Fetch a public web page and return timestamped evidence.","inputSchema":{"type":"object","properties":{"url":{"type":"string"}},"required":["url"]}}
}

async def dispatch(name,args):
    funcs={"research_country":research_country,"compare_business_models":compare_business_models,"research_suppliers":research_suppliers,"research_marketplace_fees":research_marketplace_fees,"research_fulfillment_providers":research_fulfillment_providers,"hunt_ebay_products":hunt_products,"calculate_unit_economics":calculate_unit_economics,"compare_fulfillment_options":compare_fulfillment_options,"check_product_compliance":check_product_compliance,"generate_execution_roadmap":generate_roadmap,"full_market_research":full_market_research}
    if name=="fetch_evidence": return (await fetch_page(args["url"])).model_dump()
    return await funcs[name](**args)

async def handle_rpc(request:Request,payload:dict[str,Any]):
    method=payload.get("method"); req_id=payload.get("id")
    if method=="initialize": return JSONResponse({"jsonrpc":"2.0","id":req_id,"result":{"protocolVersion":"2025-11-25","capabilities":{"tools":{"listChanged":False}},"serverInfo":{"name":"ebay-cross-border-intelligence","version":"0.1.0"}}})
    if method=="tools/list": return JSONResponse({"jsonrpc":"2.0","id":req_id,"result":{"tools":[{"name":n,**m} for n,m in TOOLS.items()]}})
    if method=="tools/call":
        p=payload.get("params",{}); name=p.get("name")
        try: result=await dispatch(name,p.get("arguments",{}) or {}); return JSONResponse({"jsonrpc":"2.0","id":req_id,"result":{"content":[{"type":"text","text":json.dumps(result,ensure_ascii=False)}],"structuredContent":result}})
        except Exception as exc: return JSONResponse({"jsonrpc":"2.0","id":req_id,"result":{"isError":True,"content":[{"type":"text","text":f"{type(exc).__name__}: {exc}"}]}})
    if req_id is not None: return JSONResponse({"jsonrpc":"2.0","id":req_id,"error":{"code":-32601,"message":f"Method not found: {method}"}},status_code=404)
    return JSONResponse({},status_code=202)
