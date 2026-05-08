"""
Services registry — scalable pattern for registering third-party integrations.

Each service module must export:
  - REQUIRED_ENV_VARS: list[str]  — env vars needed to enable the service (empty = always on)
  - register_tools(mcp: FastMCP) -> bool  — registers tools, returns True on success

Adding a new service:
  1. Create `services/my_service.py` following the interface above.
  2. Import it here and add it to _SERVICE_REGISTRY.
"""

import os
from mcp.server.fastmcp import FastMCP

from . import fetch_tools

_SERVICE_REGISTRY = [
    fetch_tools,  # No API key — always on. Simple HTML → Markdown via html2text.
]


def register_all_services(mcp: FastMCP) -> dict[str, bool]:
    """Register all services that have their required env vars set."""
    results: dict[str, bool] = {}
    for module in _SERVICE_REGISTRY:
        name = module.__name__.split(".")[-1]
        missing = [v for v in module.REQUIRED_ENV_VARS if not os.getenv(v)]
        if missing:
            print(f"[services] {name}: skipped (missing env vars: {', '.join(missing)})")
            results[name] = False
        else:
            ok = module.register_tools(mcp)
            results[name] = ok
            print(f"[services] {name}: {'active' if ok else 'failed'}")
    return results
