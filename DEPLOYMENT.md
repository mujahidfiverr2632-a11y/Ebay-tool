# Deployment and ChatGPT connection

## Free deployment option: Render

Render currently offers free web services for testing/hobby use. Free services can spin down after inactivity, so the first request can be slower.

1. Create a free Render account.
2. Connect your GitHub account.
3. Create a new Web Service from the `Ebay-tool` repository, or use the included `render.yaml` Blueprint.
4. Choose the Free plan.
5. Add these as secret environment variables:
   - `EBAY_CLIENT_ID`
   - `EBAY_CLIENT_SECRET`
   - `TAVILY_API_KEY`
   - `MCP_AUTH_TOKEN`
6. Deploy. Render will provide a URL such as `https://YOUR-SERVICE.onrender.com`.
7. Check `https://YOUR-SERVICE.onrender.com/health`.
8. The MCP endpoint is `https://YOUR-SERVICE.onrender.com/mcp`.

## ChatGPT

The MCP server must be reachable from the internet over HTTPS. Use the public `/mcp` endpoint as the MCP server URL. Availability of custom MCP connections and write permissions depends on the current ChatGPT plan and developer-mode access.

Never place API keys in GitHub files or commit `.env`.

Official references:
- https://developers.openai.com/plugins/build/mcp-server
- https://developers.openai.com/plugins/build/app-quickstart
- https://py.sdk.modelcontextprotocol.io/
- https://render.com/docs/free
