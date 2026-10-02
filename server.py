"""Production MCP server using the official MCP Python SDK."""
from mcp.server import MCPServer
from app.engine import research_country,compare_business_models,research_suppliers,hunt_products,calculate_unit_economics,compare_fulfillment_options,check_product_compliance,generate_roadmap,full_market_research,research_marketplace_fees,research_fulfillment_providers
from app.evidence import fetch_page

mcp=MCPServer("eBay Cross-Border Intelligence",instructions="Evidence-first eBay research. Never invent missing fees, legal requirements, supplier terms, or account permissions.")

@mcp.tool()
async def full_market_research_tool(country:str,marketplace:str,model:str,niche:str,budget:float|None=None): return await full_market_research(country,marketplace,model,niche,budget)

@mcp.tool()
async def research_country_tool(country:str,marketplace:str|None=None,live:bool=True): return await research_country(country,marketplace,live)

@mcp.tool()
async def compare_business_models_tool(country:str,models:list[str]|None=None): return await compare_business_models(country,models)

@mcp.tool()
async def research_suppliers_tool(country:str,marketplace:str,model:str,niche:str,budget:float|None=None): return await research_suppliers(country,marketplace,model,niche,budget)

@mcp.tool()
async def research_marketplace_fees_tool(marketplace:str,seller_country:str,category:str|None=None): return await research_marketplace_fees(marketplace,seller_country,category)

@mcp.tool()
async def research_fulfillment_providers_tool(country:str,destination:str,niche:str|None=None,provider_type:str="3pl"): return await research_fulfillment_providers(country,destination,niche,provider_type)

@mcp.tool()
async def hunt_ebay_products_tool(marketplace:str,query:str,limit:int=20): return await hunt_products(marketplace,query,limit)

@mcp.tool()
def calculate_unit_economics_tool(sale_price:float,product_cost:float,shipping_cost:float=0,fulfillment_cost:float=0,eBay_fee:float|None=None,ad_cost:float=0,return_allowance:float=0,taxes:float=0,other_costs:float=0): return calculate_unit_economics(sale_price,product_cost,shipping_cost,fulfillment_cost,eBay_fee,ad_cost,return_allowance,taxes,other_costs)

@mcp.tool()
def compare_fulfillment_options_tool(options:list[dict]): return compare_fulfillment_options(options)

@mcp.tool()
def check_product_compliance_tool(marketplace:str,buyer_country:str,product:str,known_sources:list[str]|None=None): return check_product_compliance(marketplace,buyer_country,product,known_sources)

@mcp.tool()
def generate_execution_roadmap_tool(country:str,marketplace:str,model:str,operator_country:str="PK",target:str="new_store"): return generate_roadmap(country,marketplace,model,operator_country,target)

@mcp.tool()
async def fetch_evidence_tool(url:str): return (await fetch_page(url)).model_dump()

if __name__=="__main__":
    mcp.run(transport="streamable-http",host="0.0.0.0",port=8787,streamable_http_path="/mcp",json_response=True,stateless_http=True)
