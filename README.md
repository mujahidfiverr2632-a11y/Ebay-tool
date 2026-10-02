# eBay Cross-Border Intelligence MCP

A real-time, evidence-first research engine for eBay cross-border selling. It exposes market research, business-model eligibility, supplier research, product hunting, fulfillment comparisons, unit economics, compliance checks, and execution roadmaps through an MCP-compatible HTTP server.

The repository distinguishes seller country, eBay marketplace, inventory location, buyer destination, and business model. Conclusions carry evidence and verification states rather than guessed facts.

## Implemented
- Country and marketplace research
- Wholesale dropshipping, retail arbitrage, wholesale reselling, private label
- Evidence-first compliance states
- eBay Browse API adapter
- Live supplier/web-search adapter
- Supplier normalization and scoring
- Unit economics calculator
- Fulfillment/3PL comparison framework
- Execution roadmap generator
- MCP endpoint at /mcp
- REST health/config endpoints

## Quick start
```bash
python -m venv .venv
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 8787
pytest -q
```

For live eBay data set EBAY_CLIENT_ID and EBAY_CLIENT_SECRET. For live web/supplier research set TAVILY_API_KEY. Secrets must stay in environment variables and never be committed.

## MCP tools
full_market_research, research_country, compare_business_models, research_suppliers, research_marketplace_fees, research_fulfillment_providers, hunt_ebay_products, calculate_unit_economics, compare_fulfillment_options, check_product_compliance, generate_execution_roadmap, fetch_evidence.

Production entry point: server.py (official MCP Python SDK, Streamable HTTP at /mcp).
