import asyncio
import contextlib
import secrets
import sys
import time
import uvicorn
from contextlib import asynccontextmanager
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse
from starlette.routing import Mount, Route
from mcp.server.fastmcp import FastMCP

from .auth import (
    AzureOAuthProvider,
    _AUTH_ENABLED,
    _auth_codes,
    _auth_meta,
    get_auth_settings,
    AuthorizationCode,
    construct_redirect_uri,
)
from .dummy_tools import register_dummy_tools
from .services import register_all_services
from .services.proxy_loader import setup_proxied_servers

_azure_provider = AzureOAuthProvider() if _AUTH_ENABLED else None

if _AUTH_ENABLED:
    mcp = FastMCP(
        "Helm MCP Server",
        auth=get_auth_settings(),
        auth_server_provider=_azure_provider,
    )
else:
    mcp = FastMCP("Helm MCP Server")

register_dummy_tools(mcp)
register_all_services(mcp)

if not _AUTH_ENABLED:
    print("WARNING: Azure AD not configured — running in anonymous mode.")


async def _health_endpoint(_request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok"})


async def _callback_endpoint(request: Request):
    """
    Azure AD redirects here after the user authenticates.
    We swap the Azure auth code for our own MCP auth code and redirect
    back to the original redirect_uri that the MCP client provided.
    """
    az_code = request.query_params.get("code")
    state_token = request.query_params.get("state")
    error = request.query_params.get("error")

    if error:
        error_desc = request.query_params.get("error_description", error)
        # Try to relay the error back to the MCP client redirect_uri if we have state
        if state_token:
            pending_key = f"state:{state_token}"
            pending = _auth_codes.pop(pending_key, None)
            state_meta = _auth_meta.pop(state_token, {})
            if pending:
                original_state = state_meta.get("original_state")
                redirect_params: dict[str, str] = {"error": error, "error_description": error_desc}
                if original_state:
                    redirect_params["state"] = original_state
                return RedirectResponse(
                    url=construct_redirect_uri(str(pending.redirect_uri), **redirect_params),
                    status_code=302,
                )
        return JSONResponse({"error": error, "error_description": error_desc}, status_code=400)

    if not az_code or not state_token:
        return JSONResponse({"error": "missing code or state"}, status_code=400)

    # Retrieve the pending auth request we stored in AzureOAuthProvider.authorize()
    pending_key = f"state:{state_token}"
    pending = _auth_codes.pop(pending_key, None)
    if pending is None:
        return JSONResponse({"error": "invalid state"}, status_code=400)

    # Generate our own MCP authorization code and store the Azure code inside it
    mcp_code_str = secrets.token_urlsafe(32)
    mcp_auth_code = AuthorizationCode(
        code=mcp_code_str,
        client_id=pending.client_id,
        scopes=pending.scopes,
        expires_at=time.time() + 300,
        code_challenge=pending.code_challenge,
        redirect_uri=pending.redirect_uri,
        redirect_uri_provided_explicitly=pending.redirect_uri_provided_explicitly,
        resource=pending.resource,
    )
    # Carry over the PKCE verifier and original state from the authorize() side-channel
    state_meta = _auth_meta.pop(state_token, {})
    original_state = state_meta.get("original_state")
    az_code_verifier = state_meta.get("az_code_verifier")

    # Side-channel: store the Azure code + verifier so exchange_authorization_code() can use them
    _auth_meta[f"az:{mcp_code_str}"] = {"azure_code": az_code, "az_code_verifier": az_code_verifier}
    _auth_codes[f"code:{mcp_code_str}"] = mcp_auth_code
    redirect_params: dict[str, str] = {"code": mcp_code_str}
    if original_state:
        redirect_params["state"] = original_state
    redirect_url = construct_redirect_uri(str(pending.redirect_uri), **redirect_params)
    return RedirectResponse(url=redirect_url, status_code=302)


@asynccontextmanager
async def lifespan(_app):
    async with contextlib.AsyncExitStack() as stack:
        await setup_proxied_servers(mcp, stack)
        yield


sse_app = mcp.sse_app()

app = Starlette(
    lifespan=lifespan,
    routes=[
        Route("/health", endpoint=_health_endpoint, methods=["GET"]),
        Route("/callback", endpoint=_callback_endpoint, methods=["GET"]),
        Mount("/", app=sse_app),
    ]
)


if __name__ == "__main__":
    if "stdio" in sys.argv:
        print("Running in stdio mode (no auth)")

        async def _run_stdio():
            async with contextlib.AsyncExitStack() as stack:
                await setup_proxied_servers(mcp, stack)
                await mcp.run_stdio_async()

        asyncio.run(_run_stdio())
    else:
        uvicorn.run("src.mcp_server.server:app", host="0.0.0.0", port=8000)
