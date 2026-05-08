"""
Fetch Service — converts HTTP URLs to Markdown using html2text.

No API key required. Always enabled.
"""

import html2text
import requests
import urllib3
from urllib.parse import urlparse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from mcp.server.fastmcp import FastMCP

REQUIRED_ENV_VARS: list[str] = []  # Always enabled


def register_tools(mcp: FastMCP) -> bool:
    converter = html2text.HTML2Text()
    converter.ignore_links = False
    converter.body_width = 0  # no line wrapping

    @mcp.tool()
    def fetch_url_as_markdown(url: str, include_links: bool = True) -> str:
        """
        Fetch a webpage and return its content as Markdown (no API key required).

        Uses html2text for conversion. For better quality on JS-heavy sites or
        pages with ads/clutter, use scrape_with_firecrawl instead.

        Args:
            url: HTTP or HTTPS URL to fetch.
            include_links: Preserve hyperlinks as [text](url) (default: True).
        """
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            raise ValueError("Only http and https URLs are supported.")

        converter.ignore_links = not include_links
        resp = requests.get(url, timeout=15, headers={"User-Agent": "MCP-Fetch/1.0"}, verify=False)
        resp.raise_for_status()
        return converter.handle(resp.text)

    return True
