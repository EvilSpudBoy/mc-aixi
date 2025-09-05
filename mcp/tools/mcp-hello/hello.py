from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP


# Initialize FastMCP server
mcp = FastMCP("hello")


@mcp.tool()
def hello(name: str) -> str:
	"""Return a friendly greeting for the provided name."""
	return f"Hello, {name}!"


@mcp.tool()
def add(a: float, b: float) -> float:
	"""Add two numbers and return the sum."""
	return a + b


# --- Weather helpers ---
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "mcp-hello/1.0"


async def make_nws_request(url: str) -> dict[str, Any] | None:
	"""Make a request to the NWS API with basic error handling."""
	headers = {
		"User-Agent": USER_AGENT,
		"Accept": "application/geo+json",
	}
	async with httpx.AsyncClient(timeout=30.0) as client:
		try:
			resp = await client.get(url, headers=headers)
			resp.raise_for_status()
			return resp.json()
		except Exception:
			return None


def format_alert(feature: dict) -> str:
	"""Format an alert feature into a readable string."""
	props = feature.get("properties", {})
	return (
		f"Event: {props.get('event', 'Unknown')}\n"
		f"Area: {props.get('areaDesc', 'Unknown')}\n"
		f"Severity: {props.get('severity', 'Unknown')}\n"
		f"Description: {props.get('description', 'No description available')}\n"
		f"Instructions: {props.get('instruction', 'No specific instructions provided')}"
	)


@mcp.tool()
async def get_alerts(state: str) -> str:
	"""Get active weather alerts for a US state (two-letter code).

	Args:
		state: Two-letter US state code (e.g., CA, NY)
	"""
	if not state or len(state.strip()) != 2:
		return "Please provide a two-letter US state code (e.g., CA, NY)."
	state = state.strip().upper()
	url = f"{NWS_API_BASE}/alerts/active/area/{state}"
	data = await make_nws_request(url)
	if not data or "features" not in data:
		return "Unable to fetch alerts or no alerts found."
	features = data.get("features", [])
	if not features:
		return "No active alerts for this state."
	alerts = [format_alert(f) for f in features]
	return "\n---\n".join(alerts)


@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
	"""Get the weather forecast for a latitude/longitude in the US.

	Args:
		latitude: Latitude of the location
		longitude: Longitude of the location
	"""
	points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
	points_data = await make_nws_request(points_url)
	if not points_data or "properties" not in points_data:
		return "Unable to fetch forecast data for this location."
	forecast_url = points_data["properties"].get("forecast")
	if not forecast_url:
		return "Forecast URL not found for this location."
	forecast_data = await make_nws_request(forecast_url)
	if not forecast_data or "properties" not in forecast_data:
		return "Unable to fetch detailed forecast."
	periods = forecast_data["properties"].get("periods", [])
	if not periods:
		return "No forecast periods available."
	forecasts: list[str] = []
	for period in periods[:5]:  # show next 5 periods
		forecasts.append(
			(
				f"{period.get('name', 'Period')}:\n"
				f"  Temperature: {period.get('temperature', '?')}°{period.get('temperatureUnit', '')}\n"
				f"  Wind: {period.get('windSpeed', '?')} {period.get('windDirection', '')}\n"
				f"  Forecast: {period.get('detailedForecast', 'N/A')}"
			)
		)
	return "\n---\n".join(forecasts)


if __name__ == "__main__":
	# Start the MCP server using stdio transport.
	# Avoid printing to stdout; FastMCP handles protocol I/O.
	mcp.run(transport="stdio")
