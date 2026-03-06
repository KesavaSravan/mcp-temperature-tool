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
                "tools": [TEMPERATURE_TOOL]
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