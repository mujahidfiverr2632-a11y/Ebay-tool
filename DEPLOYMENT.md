# Deployment and ChatGPT connection

1. Install dependencies and run python server.py locally.
2. Deploy the server to a public HTTPS host for remote ChatGPT access.
3. Set EBAY_CLIENT_ID, EBAY_CLIENT_SECRET, TAVILY_API_KEY, and MCP_AUTH_TOKEN as host secrets.
4. Use the public /mcp endpoint as the remote MCP server URL.
5. Never commit .env or credentials.

Official references:
- https://developers.openai.com/plugins/build/mcp-server
- https://developers.openai.com/plugins/build/app-quickstart
- https://developer.ebay.com/api-docs/buy/browse/overview.html
