from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Dict, Any

app = FastAPI(
    title="MCP Temperature Server",
    description="Simple MCP server using FastAPI",
    version="1.0.0"
)

# -----------------------------
# Temperature logic
# -----------------------------

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
    return mock_data.get(city.strip().lower(), "20°C")


# -----------------------------
# MCP Tool definition
# -----------------------------

TOOL = {
    "name": "get_temperature",
    "description": "Get the current temperature of a city",
    "inputSchema": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string"
            }
        },
        "required": ["city"]
    }
}


# -----------------------------
# Health endpoint
# -----------------------------

@app.get("/health")
async def health():
    return {"status": "ok"}


# -----------------------------
# MCP JSON-RPC Endpoint
# -----------------------------

@app.post("/")
async def mcp_rpc(request: Request):

    body = await request.json()

    method = body.get("method")
    req_id = body.get("id")

    # Tool discovery
    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [TOOL]
            }
        }

    # Tool execution
    if method == "tools/call":

        params = body.get("params", {})
        name = params.get("name")
        arguments = params.get("arguments", {})

        if name == "get_temperature":

            city = arguments.get("city")
            temp = get_simulated_temperature(city)

            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"The temperature in {city} is {temp}"
                        }
                    ]
                }
            }

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {
            "code": -32601,
            "message": "Method not found"
        }
    }