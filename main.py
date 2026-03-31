from fastapi import FastAPI, Request
from typing import Dict
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="MCP Temperature Server",
    description="Simple MCP server using FastAPI with live weather data",
    version="2.0.0"
)

# ==========================================
# Configuration
# ==========================================

OWM_API_KEY = os.getenv("OWM_API_KEY", "")
OWM_BASE_URL = "https://api.openweathermap.org/data/2.5"


# ==========================================
# Temperature Logic (Live Data)
# ==========================================

async def get_live_temperature(city: str) -> str:
    if not city:
        return "Unknown"

    if not OWM_API_KEY:
        return "Error: OWM_API_KEY environment variable not set."

    url = f"{OWM_BASE_URL}/weather"
    params = {
        "q": city,
        "appid": OWM_API_KEY,
        "units": "metric"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                temp = data["main"]["temp"]
                feels_like = data["main"]["feels_like"]
                description = data["weather"][0]["description"].capitalize()
                return f"{temp:.1f}°C (Feels like {feels_like:.1f}°C, {description})"
            elif response.status_code == 404:
                return f"City '{city}' not found."
            elif response.status_code == 401:
                return "Error: Invalid API key."
            else:
                return f"Error fetching data (HTTP {response.status_code})."
        except httpx.RequestError as e:
            return f"Network error: {str(e)}"


async def get_live_forecast(city: str) -> str:
    if not city:
        return "Unknown"

    if not OWM_API_KEY:
        return "Error: OWM_API_KEY environment variable not set."

    # /forecast returns 5-day forecast in 3-hour steps; we pick one reading per day
    url = f"{OWM_BASE_URL}/forecast"
    params = {
        "q": city,
        "appid": OWM_API_KEY,
        "units": "metric",
        "cnt": 24   # 24 × 3h = 72h (3 days)
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                entries = data["list"]

                # Pick one entry per calendar day (skip today)
                seen_dates = set()
                daily = []
                for entry in entries:
                    date = entry["dt_txt"].split(" ")[0]
                    if date not in seen_dates:
                        seen_dates.add(date)
                        temp = entry["main"]["temp"]
                        desc = entry["weather"][0]["description"].capitalize()
                        daily.append(f"{date}: {temp:.1f}°C ({desc})")
                    if len(daily) == 3:
                        break

                return "Next 3 days:\n" + "\n".join(daily) if daily else "No forecast data available."
            elif response.status_code == 404:
                return f"City '{city}' not found."
            elif response.status_code == 401:
                return "Error: Invalid API key."
            else:
                return f"Error fetching forecast (HTTP {response.status_code})."
        except httpx.RequestError as e:
            return f"Network error: {str(e)}"


def convert_temperature(value: float, from_unit: str, to_unit: str) -> str:
    from_unit = from_unit.strip().upper()
    to_unit = to_unit.strip().upper()

    if from_unit == "C" and to_unit == "F":
        return f"{(value * 9/5) + 32:.1f}°F"
    elif from_unit == "F" and to_unit == "C":
        return f"{(value - 32) * 5/9:.1f}°C"
    elif from_unit == to_unit:
        return f"{value}°{from_unit}"
    else:
        return "Invalid units. Use 'C' or 'F'."


# ==========================================
# MCP Tool Definitions
# ==========================================

TEMPERATURE_TOOL = {
    "name": "get_temperature",
    "description": "Get the current live temperature of a city using OpenWeatherMap",
    "inputSchema": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "Name of the city"
            }
        },
        "required": ["city"]
    }
}

FORECAST_TOOL = {
    "name": "get_temperature_forecast",
    "description": "Get the live temperature forecast for a city for the next 3 days",
    "inputSchema": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "Name of the city"
            }
        },
        "required": ["city"]
    }
}

CONVERT_TOOL = {
    "name": "convert_temperature",
    "description": "Convert a temperature between Celsius (°C) and Fahrenheit (°F)",
    "inputSchema": {
        "type": "object",
        "properties": {
            "value": {
                "type": "number",
                "description": "The temperature value to convert"
            },
            "from_unit": {
                "type": "string",
                "description": "The unit to convert from ('C' or 'F')"
            },
            "to_unit": {
                "type": "string",
                "description": "The unit to convert to ('C' or 'F')"
            }
        },
        "required": ["value", "from_unit", "to_unit"]
    }
}


# ==========================================
# Health Endpoint
# ==========================================

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "temperature-mcp",
        "live_data": bool(OWM_API_KEY)
    }


# ==========================================
# MCP JSON-RPC Endpoint
# ==========================================

@app.post("/")
async def mcp_rpc(request: Request):

    body: Dict = await request.json()
    method = body.get("method")
    request_id = body.get("id")

    # --------------------------
    # MCP Initialization
    # --------------------------
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "temperature-mcp",
                    "version": "2.0.0"
                }
            }
        }

    # --------------------------
    # List Available Tools
    # --------------------------
    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": [TEMPERATURE_TOOL, FORECAST_TOOL, CONVERT_TOOL]
            }
        }

    # --------------------------
    # Call Tool
    # --------------------------
    if method == "tools/call":

        params = body.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name == "get_temperature":
            city = arguments.get("city")
            temperature = await get_live_temperature(city)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [{"type": "text", "text": f"The temperature in {city} is {temperature}"}]
                }
            }

        elif tool_name == "get_temperature_forecast":
            city = arguments.get("city")
            forecast = await get_live_forecast(city)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [{"type": "text", "text": f"Temperature forecast for {city}:\n{forecast}"}]
                }
            }

        elif tool_name == "convert_temperature":
            value = arguments.get("value")
            from_unit = arguments.get("from_unit")
            to_unit = arguments.get("to_unit")
            result_temp = convert_temperature(value, from_unit, to_unit)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [{"type": "text", "text": f"The converted temperature is {result_temp}"}]
                }
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Tool not found"}
        }

    # --------------------------
    # Unknown Method
    # --------------------------
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": -32601, "message": "Method not found"}
    }


# ==========================================
# Local Development Runner
# ==========================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)