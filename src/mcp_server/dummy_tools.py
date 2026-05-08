"""
Dummy MCP Tools

Simple placeholder tools for demonstration and testing purposes.
"""

from datetime import datetime
import hashlib
from mcp.server.fastmcp import FastMCP

_WEATHER_DATA: dict[str, dict] = {
    "london":       {"temperature": 15.0, "humidity": 75, "condition": "Cloudy",         "wind_speed": 20},
    "new york":     {"temperature": 20.0, "humidity": 60, "condition": "Partly cloudy",  "wind_speed": 15},
    "paris":        {"temperature": 18.5, "humidity": 70, "condition": "Overcast",       "wind_speed": 12},
    "tokyo":        {"temperature": 22.0, "humidity": 65, "condition": "Sunny",          "wind_speed": 8},
    "sydney":       {"temperature": 25.0, "humidity": 55, "condition": "Clear",          "wind_speed": 18},
    "berlin":       {"temperature": 14.0, "humidity": 80, "condition": "Rainy",          "wind_speed": 25},
    "madrid":       {"temperature": 28.0, "humidity": 40, "condition": "Sunny",          "wind_speed": 10},
    "amsterdam":    {"temperature": 13.0, "humidity": 82, "condition": "Drizzle",        "wind_speed": 22},
    "barcelona":    {"temperature": 26.0, "humidity": 50, "condition": "Sunny",          "wind_speed": 11},
    "rome":         {"temperature": 24.0, "humidity": 55, "condition": "Clear",          "wind_speed": 9},
    "moscow":       {"temperature": -2.0, "humidity": 87, "condition": "Snow",           "wind_speed": 30},
    "beijing":      {"temperature": 17.0, "humidity": 58, "condition": "Hazy",           "wind_speed": 14},
    "dubai":        {"temperature": 38.0, "humidity": 45, "condition": "Sunny",          "wind_speed": 7},
    "singapore":    {"temperature": 31.0, "humidity": 85, "condition": "Thunderstorm",   "wind_speed": 16},
    "buenos aires": {"temperature": 19.0, "humidity": 68, "condition": "Partly cloudy",  "wind_speed": 13},
}


def register_dummy_tools(mcp: FastMCP) -> None:
    """Register dummy/demo tools with MCP server."""

    @mcp.tool()
    def get_weather(city: str) -> dict:
        """
        Get current weather conditions for a city (dummy data).

        Returns temperature (°C), humidity (%), weather condition, and wind speed (km/h).
        Supported cities: London, New York, Paris, Tokyo, Sydney, Berlin, Madrid,
        Amsterdam, Barcelona, Rome, Moscow, Beijing, Dubai, Singapore, Buenos Aires.

        Args:
            city: City name (case-insensitive).
        """
        data = _WEATHER_DATA.get(city.lower())
        if data is None:
            available = ", ".join(c.title() for c in _WEATHER_DATA)
            return {"error": f"City '{city}' not found. Available: {available}"}
        return {
            "city": city.title(),
            "temperature_c": data["temperature"],
            "humidity_pct": data["humidity"],
            "condition": data["condition"],
            "wind_speed_kmh": data["wind_speed"],
        }

    @mcp.tool()
    def get_server_time() -> str:
        """Get the current server time in ISO 8601 format (UTC)."""
        return datetime.utcnow().isoformat() + "Z"

    @mcp.tool()
    def calculate_checksum(text: str) -> str:
        """Calculate SHA256 checksum of provided text."""
        return hashlib.sha256(text.encode()).hexdigest()

    @mcp.tool()
    def echo_message(message: str, prefix: str = "") -> str:
        """Echo back a message with optional prefix."""
        if prefix:
            return f"{prefix}: {message}"
        return f"Echo: {message}"

    @mcp.tool()
    def hello_world(name: str = "World") -> str:
        """Simple greeting tool."""
        return f"Hello, {name}! This is the Helm MCP Server."

    @mcp.tool()
    def string_length(text: str) -> int:
        """Return the length of a string."""
        return len(text)
