from __future__ import annotations
from typing import Any
from .marketplaces import MARKETPLACES, BUSINESS_MODELS, EBAY_OFFICIAL_SOURCES
from .models import Evidence, SupplierCandidate
from .evidence import fetch_page, now_utc
from .search import tavily_search, SearchUnavailable
from .ebay_api import ebay, EbayAPIError

COUNTRY_OFFICIAL_DOMAINS = {
    "US": ["irs.gov", "cbp.gov", "ftc.gov", "cpsc.gov"],
    "GB": ["gov.uk", "hmrc.gov.uk"],
    "DE": ["bund.de", "zoll.de", "bafin.de"],
    "FR": ["service-public.fr", "douane.gouv.fr", "economie.gouv.fr"],
    "IT": ["gov.it", "agenziaentrate.gov.it", "adm.gov.it"],
    "ES": ["administracion.gob.es", "agenciatributaria.es", "aeat.es"],
    "NL": ["government.nl", "belastingdienst.nl"],
    "AE": ["u.ae", "tax.gov.ae", "moec.gov.ae"],
    "SA": ["gov.sa", "zatca.gov.sa"],
    "CA": ["canada.ca", "cbsa-asfc.gc.ca"],
    "AU": ["ato.gov.au", "abf.gov.au", "accc.gov.au"],
}

def _market(value: str) -> dict[str, Any]:
    key = value.upper()
    if key in MARKETPLACES:
        return MARKETPLACES[key]
    for v in MARKETPLACES.values():
        if key in {v["marketplace_id"], v["site"], v["country"]}:
            return v
    return {"country": value, "marketplace_id": None, "currency": None, "site": None}

async def research_country(country: str, marketplace: str | None = None, live: bool = True) -> dict[str, Any]:
    m = _market(marketplace or country)
    evidence: list[Evidence] = []
    if live:
        for url in EBAY_OFFICIAL_SOURCES:
            evidence.append(await fetch_page(url, "ebay_official"))
        domains = COUNTRY_OFFICIAL_DOMAINS.get(country.upper(), [])
        if domains:
            try:
                results = await tavily_search(f"ecommerce seller tax import consumer product rules {country}", 12)
                for e in results:
                    if any(d in e.url for d in domains):
                        e.source_type = "government_search"; e.confidence = "high"; evidence.append(e)
            except SearchUnavailable:
                pass
    return {
        "subject": country, "market": m, "seller_country": country.upper(),
        "marketplace": marketplace or m.get("marketplace_id"),
        "business_models": list(BUSINESS_MODELS),
        "baseline": [{"model": k, "label": v["label"], "baseline": v["policy_baseline"], "status": "NEEDS_VERIFICATION"} for k,v in BUSINESS_MODELS.items()],
        "evidence": [e.model_dump() for e in evidence], "checked_at_utc": now_utc(),
        "warnings": ["Country-specific legal/tax status cannot be concluded from marketplace eligibility alone.", "Account-specific permissions require authenticated seller data."]
    }

async def compare_business_models(country: str, models: list[str] | None = None) -> dict[str, Any]:
    selected = models or list(BUSINESS_MODELS)
    rows = []
    for model in selected:
        if model not in BUSINESS_MODELS:
            rows.append({"model": model, "status": "NOT_VERIFIED", "reason": "Unknown model"}); continue
        rows.append({"model": model, "label": BUSINESS_MODELS[model]["label"], "baseline": BUSINESS_MODELS[model]["policy_baseline"], "status": "NEEDS_VERIFICATION", "what_to_verify": ["eBay marketplace policy","product/category restrictions","country tax/import rules","supplier agreement and fulfillment terms"]})
    return {"country": country, "rows": rows, "checked_at_utc": now_utc()}

async def research_suppliers(country: str, marketplace: str, model: str, niche: str, budget: float | None = None) -> dict[str, Any]:
    queries = [f"wholesale supplier {niche} {country} dropship {marketplace}", f"manufacturer {niche} {country} wholesale private label", f"{niche} distributor {country} wholesale reseller"]
    evidence: list[Evidence] = []
    for q in queries:
        try: evidence.extend(await tavily_search(q, 8))
        except SearchUnavailable as exc:
            return {"status":"NEEDS_VERIFICATION","country":country,"marketplace":marketplace,"model":model,"suppliers":[],"warnings":[str(exc)],"checked_at_utc":now_utc()}
    unique = {e.url:e for e in evidence if e.url}
    suppliers = [SupplierCandidate(name=e.title.split("|")[0].strip()[:120], url=e.url, country=country, business_models=[model], evidence=[e]) for e in list(unique.values())[:20]]
    return {"status":"VERIFIED","country":country,"marketplace":marketplace,"model":model,"niche":niche,"suppliers":[s.model_dump() for s in suppliers],"checked_at_utc":now_utc(),"warnings":["Search results are candidates, not proof of current wholesale terms. Verify supplier terms directly before contracting."]}

async def hunt_products(marketplace: str, query: str, limit: int = 20) -> dict[str, Any]:
    if not ebay.available(): return {"status":"NEEDS_VERIFICATION","products":[],"warnings":["eBay application credentials are not configured."],"checked_at_utc":now_utc()}
    try:
        products = await ebay.search_items(marketplace, query, limit)
        return {"status":"VERIFIED","marketplace":marketplace,"query":query,"products":[p.model_dump() for p in products],"checked_at_utc":now_utc()}
    except EbayAPIError as exc: return {"status":"NOT_VERIFIED","products":[],"warnings":[str(exc)],"checked_at_utc":now_utc()}

def calculate_unit_economics(sale_price: float, product_cost: float, shipping_cost: float=0, fulfillment_cost: float=0, eBay_fee: float|None=None, ad_cost: float=0, return_allowance: float=0, taxes: float=0, other_costs: float=0) -> dict[str, Any]:
    if sale_price <= 0: raise ValueError("sale_price must be > 0")
    known = product_cost+shipping_cost+fulfillment_cost+ad_cost+return_allowance+taxes+other_costs
    total = known+(eBay_fee or 0); net=sale_price-total
    return {"sale_price":sale_price,"product_cost":product_cost,"shipping_cost":shipping_cost,"fulfillment_cost":fulfillment_cost,"ebay_fee":eBay_fee,"advertising_cost":ad_cost,"return_allowance":return_allowance,"taxes":taxes,"other_costs":other_costs,"known_total_cost":known,"total_cost_if_fee_supplied":total if eBay_fee is not None else None,"estimated_net_profit_if_fee_supplied":net if eBay_fee is not None else None,"net_margin_if_fee_supplied":(net/sale_price*100) if eBay_fee is not None else None,"note":"Fee was not guessed. Supply the current marketplace fee or connect a fee-data source."}

def compare_fulfillment_options(options: list[dict[str,Any]]) -> dict[str,Any]:
    ranked=[]
    for item in options:
        storage=float(item.get("monthly_storage",0) or 0); pick=float(item.get("pick_pack",0) or 0); inbound=float(item.get("inbound",0) or 0); minimum=float(item.get("monthly_minimum",0) or 0); orders=int(item.get("expected_orders",0) or 0)
        ranked.append({**item,"estimated_monthly_cost":round(max(storage+inbound+pick*orders,minimum),2)})
    ranked.sort(key=lambda x:x["estimated_monthly_cost"])
    return {"options":ranked,"ranking_note":"Sorted only by the explicit cost formula provided; no hidden assumptions."}

def check_product_compliance(marketplace: str,buyer_country: str,product: str,known_sources:list[str]|None=None)->dict[str,Any]:
    return {"status":"NEEDS_VERIFICATION","marketplace":marketplace,"buyer_country":buyer_country,"product":product,"checks":["eBay prohibited/restricted categories","brand/IP restrictions","product safety","destination-country import rules","labeling/certification","tax/consumer-protection rules"],"sources":known_sources or [],"conclusion":"No legal or policy clearance is asserted without current source evidence.","checked_at_utc":now_utc()}

def generate_roadmap(country:str,marketplace:str,model:str,operator_country:str="PK",target:str="new_store")->dict[str,Any]:
    steps=["Confirm client legal ownership, identity and payout details.","Use delegated account access/Team Access where supported; do not share credentials unnecessarily.","Confirm seller eligibility and marketplace registration requirements.","Confirm product/category restrictions before sourcing inventory.","Select and document the supplier relationship and fulfillment SLA.","Select warehouse/3PL/fulfillment route and obtain current pricing in writing.","Research demand and competition using current eBay data where API access allows.","Build listing economics using current fees and landed cost.","Run compliance/IP/product-safety checks.","List a controlled test set and monitor dispatch, tracking, returns and account health.","Scale only after the test cohort is operationally stable."]
    return {"country":country,"marketplace":marketplace,"model":model,"operator_country":operator_country,"target":target,"steps":[{"step":i+1,"task":s,"status":"PENDING"} for i,s in enumerate(steps)],"checked_at_utc":now_utc()}

async def research_marketplace_fees(marketplace:str,seller_country:str,category:str|None=None)->dict[str,Any]:
    queries=[f"eBay {marketplace} selling fees seller {seller_country}",f"eBay {marketplace} international selling fee {seller_country}"] + ([f"eBay {marketplace} selling fees {category}"] if category else [])
    try:
        evidence=[] 
        for q in queries: evidence.extend(await tavily_search(q,8))
        return {"status":"VERIFIED","marketplace":marketplace,"seller_country":seller_country,"category":category,"evidence":[e.model_dump() for e in evidence],"checked_at_utc":now_utc(),"warning":"Fee values must be cross-checked against the current official eBay fee page before financial decisions."}
    except SearchUnavailable as exc: return {"status":"NEEDS_VERIFICATION","marketplace":marketplace,"seller_country":seller_country,"category":category,"evidence":[],"warnings":[str(exc)],"checked_at_utc":now_utc()}

async def research_fulfillment_providers(country:str,destination:str,niche:str|None=None,provider_type:str="3pl")->dict[str,Any]:
    q=f"{provider_type} fulfillment warehouse {country} {destination}"+(f" {niche}" if niche else "")
    try:
        evidence=await tavily_search(q,15)
        return {"status":"VERIFIED","country":country,"destination":destination,"provider_type":provider_type,"niche":niche,"providers":[e.model_dump() for e in evidence],"checked_at_utc":now_utc(),"warning":"Provider candidates require current rate cards for receiving, storage, pick/pack, shipping, returns, minimums and surcharges."}
    except SearchUnavailable as exc: return {"status":"NEEDS_VERIFICATION","country":country,"destination":destination,"provider_type":provider_type,"providers":[],"warnings":[str(exc)],"checked_at_utc":now_utc()}

async def full_market_research(country:str,marketplace:str,model:str,niche:str,budget:float|None=None)->dict[str,Any]:
    return {"country_research":await research_country(country,marketplace,True),"business_model":await compare_business_models(country,[model]),"suppliers":await research_suppliers(country,marketplace,model,niche,budget),"fees":await research_marketplace_fees(marketplace,country),"fulfillment":await research_fulfillment_providers(country,country,niche),"roadmap":generate_roadmap(country,marketplace,model),"limitations":["Product-level compliance, taxes and exact fee amounts require current source retrieval and, where relevant, authenticated account context."]}
