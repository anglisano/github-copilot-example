"""
MCP Proxy Loader — expose any third-party MCP server as tools in this server.

Each entry in PROXIED_SERVERS launches an external MCP server as a subprocess
(via npx, uvx, etc.) and automatically re-registers ALL its tools here.
Azure AD auth is enforced at this server layer, so clients only need one
authenticated connection regardless of how many services are proxied.

Adding a new service
--------------------
Append one ProxiedServer entry to PROXIED_SERVERS below. That's it.
No other code changes are required.

Find MCP servers at: https://mcp.so / https://smithery.ai
"""

import contextlib
import logging
import os
import shutil
from dataclasses import dataclass, field

from mcp import StdioServerParameters
from mcp.client.session_group import ClientSessionGroup
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.utilities.func_metadata import ArgModelBase
from pydantic import ConfigDict

logger = logging.getLogger(__name__)


class _ProxyArgModel(ArgModelBase):
    """Pydantic model that passes all arguments through without schema validation.

    Used internally so FastMCP's call machinery forwards any kwargs to the
    upstream MCP server unchanged.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="allow",
    )

    def model_dump_one_level(self) -> dict:
        result = super().model_dump_one_level()
        if self.model_extra:
            result.update(self.model_extra)
        return result


# ─────────────────────────────────────────────────────────────────────────────
# ADD NEW SERVICES HERE
#
# Fields:
#   name         — display name used in logs
#   command      — full command to launch the MCP server (first item is the executable)
#   required_env — env vars that must be set; if any are missing the service is skipped
#
# Examples:
#   ProxiedServer("github",   ["npx", "-y", "@modelcontextprotocol/server-github"], ["GITHUB_TOKEN"])
#   ProxiedServer("slack",    ["npx", "-y", "@modelcontextprotocol/server-slack"],  ["SLACK_BOT_TOKEN"])
#   ProxiedServer("postgres", ["npx", "-y", "@modelcontextprotocol/server-postgres"], ["DATABASE_URL"])
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ProxiedServer:
    """Configuration for a third-party MCP server to proxy."""

    name: str
    command: list[str]
    required_env: list[str] = field(default_factory=list)


PROXIED_SERVERS: list[ProxiedServer] = [
    ProxiedServer(
        name="context7",
        command=["npx", "-y", "@upstash/context7-mcp", "--api-key", "$CONTEXT7_API_KEY"],
        required_env=["CONTEXT7_API_KEY"],
    )
]


async def setup_proxied_servers(
    mcp: FastMCP,
    exit_stack: contextlib.AsyncExitStack,
) -> None:
    """Connect to all configured MCP servers and register their tools in FastMCP.

    Called once at server startup. Each external server runs as a subprocess
    and stays alive for the lifetime of the Starlette app.
    """
    group = await exit_stack.enter_async_context(ClientSessionGroup())

    for server_cfg in PROXIED_SERVERS:
        missing = [v for v in server_cfg.required_env if not os.getenv(v)]
        if missing:
            logger.info(
                "[proxy] %s: skipped (missing env vars: %s)",
                server_cfg.name,
                ", ".join(missing),
            )
            continue

        # On Windows npx/node commands are .cmd files — resolve to full path
        cmd = shutil.which(server_cfg.command[0]) or server_cfg.command[0]
        expanded_args = [os.path.expandvars(a) for a in server_cfg.command[1:]]
        params = StdioServerParameters(
            command=cmd,
            args=expanded_args,
            env=dict(os.environ),  # pass current env
        )

        tools_before = set(group.tools)
        try:
            await group.connect_to_server(params)
        except Exception as exc:
            logger.warning("[proxy] %s: failed to connect — %s", server_cfg.name, exc)
            continue

        new_tools = {k: v for k, v in group.tools.items() if k not in tools_before}
        logger.info(
            "[proxy] %s: connected — %d tools registered",
            server_cfg.name,
            len(new_tools),
        )

        for tool_name, remote_tool in new_tools.items():
            _register_proxy_tool(mcp, group, tool_name, remote_tool)


def _register_proxy_tool(
    mcp: FastMCP,
    group: ClientSessionGroup,
    tool_name: str,
    remote_tool,
) -> None:
    """Register one remote MCP tool as a proxied tool in FastMCP."""
    description = remote_tool.description or ""
    input_schema = remote_tool.inputSchema  # real JSON schema from the upstream server

    async def proxy_fn(**kwargs):
        result = await group.call_tool(tool_name, arguments=kwargs)
        parts = []
        for item in result.content:
            if hasattr(item, "text"):
                parts.append(item.text)
            else:
                parts.append(str(item))
        return "\n".join(parts) if parts else ""

    proxy_fn.__name__ = tool_name
    proxy_fn.__doc__ = description

    mcp.add_tool(proxy_fn, name=tool_name, description=description)

    # Patch the registered Tool so the LLM sees the real parameter schema and
    # FastMCP's argument validation passes all kwargs through unchanged.
    registered = mcp._tool_manager._tools.get(tool_name)
    if registered:
        if input_schema:
            registered.parameters = input_schema
        registered.fn_metadata.arg_model = _ProxyArgModel
