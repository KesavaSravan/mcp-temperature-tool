from fastapi import FastAPI, Request
from typing import Dict

app = FastAPI(
    title="MCP Temperature Server",
    description="Simple MCP server using FastAPI",
    version="1.0.0"
)

# ==========================================
# Temperature Logic
# ==========================================

def get_simulated_temperature(city: str) -> str:
    mock_data = {
        "hyderabad": "32°C",
        "london": "15°C",
        "new york": "22°C",
        "tokyo": "18°C",
        "sydney": "25°C",
        "paris": "16°C",
        "delhi": "30°C"
    }

    if not city:
        return "Unknown"

    return mock_data.get(city.strip().lower(), "20°C")


def get_temperature_forecast(city: str) -> str:
    mock_data = {
        "hyderabad": ["32°C", "33°C", "34°C"],
        "london": ["15°C", "14°C", "15°C"],
        "new york": ["22°C", "23°C", "20°C"],
        "tokyo": ["18°C", "19°C", "21°C"],
        "sydney": ["25°C", "26°C", "24°C"],
        "paris": ["16°C", "15°C", "17°C"],
        "delhi": ["30°C", "32°C", "33°C"]
    }

    if not city:
        return "Unknown"

    forecast = mock_data.get(city.strip().lower(), ["20°C", "21°C", "20°C"])
    return f"Next 3 days: {', '.join(forecast)}"


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
# MCP Tool Definition
# ==========================================

TEMPERATURE_TOOL = {
    "name": "get_temperature",
    "description": "Get the current temperature of a city",
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
    "description": "Get the temperature forecast for a city for the next 3 days",
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
        "service": "temperature-mcp"
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
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "temperature-mcp",
                    "version": "1.0.0"
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
            temperature = get_simulated_temperature(city)

            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"The temperature in {city} is {temperature}"
                        }
                    ]
                }
            }

        elif tool_name == "get_temperature_forecast":

            city = arguments.get("city")
            forecast = get_temperature_forecast(city)

            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"The temperature forecast for {city} is: {forecast}"
                        }
                    ]
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
                    "content": [
                        {
                            "type": "text",
                            "text": f"The converted temperature is {result_temp}"
                        }
                    ]
                }
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32601,
                "message": "Tool not found"
            }
        }

    # --------------------------
    # Unknown Method
    # --------------------------
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": -32601,
            "message": "Method not found"
        }
    }


# ==========================================
# Local Development Runner
# ==========================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )