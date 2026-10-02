# Cloudflare Free Deployment

This project is prepared for Cloudflare Python Workers.

## Why Cloudflare

Cloudflare Workers has a Free plan. Cloudflare's current documentation lists 100,000 requests/day for Workers Free. A Free Cloudflare account can be created directly from the dashboard; adding a payment method is for paid products/services, not for creating the Free account.

Cloudflare also supports Python Workers, FastAPI, GitHub repository integration, and Streamable HTTP MCP servers.

## What you will do

1. Create a free Cloudflare account.
2. Connect your GitHub account to Cloudflare Workers Builds.
3. Select the `mujahidfiverr2632-a11y/Ebay-tool` repository.
4. Use branch `main`.
5. Cloudflare will build and deploy the Worker from `wrangler.jsonc`.
6. After deployment, Cloudflare will give you a `workers.dev` URL.
7. The MCP endpoint will be:
   `https://YOUR-WORKER.YOUR-SUBDOMAIN.workers.dev/mcp`
8. Health endpoint:
   `https://YOUR-WORKER.YOUR-SUBDOMAIN.workers.dev/health`

## Runtime secrets

Do NOT put secrets in GitHub.

Add these in Cloudflare Worker -> Settings -> Variables and Secrets:

- `EBAY_CLIENT_ID`
- `EBAY_CLIENT_SECRET`
- `TAVILY_API_KEY`
- `MCP_AUTH_TOKEN`

The repo's Python Worker loads those secrets at request time.

## Important

The MCP endpoint is intentionally prepared for stateless Streamable HTTP. The current MCP Python SDK documentation recommends Streamable HTTP for remote servers and requires the ASGI host application's lifespan to start the MCP session manager when the MCP app is mounted.

The Cloudflare wrapper disables the SDK's localhost-only DNS-rebinding allowlist because Cloudflare is the public reverse-proxy layer. Before adding private account data or write capabilities, add a proper MCP OAuth/authentication layer rather than relying on an obscure URL.

## GitHub auto-deploy

Cloudflare Workers Builds can connect directly to GitHub. Every new commit to the selected production branch can trigger a build and deploy.

## ChatGPT

ChatGPT custom MCP support depends on the current ChatGPT plan. OpenAI's current documentation says full custom MCP support is available to Business/Enterprise/Edu, while Pro can connect read/fetch MCPs in developer mode; Free does not currently provide the custom-MCP developer connection needed for this workflow.

Once the server is live, the endpoint to use is the public HTTPS `/mcp` URL.
