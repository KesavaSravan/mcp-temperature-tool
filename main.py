from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List

# Initialize FastAPI application
app = FastAPI(
    title="MCP Temperature Server",
    description="A simple Model Context Protocol (MCP) tool running via FastAPI.",
    version="1.0.0"
)

# ==========================================
# Pydantic Schemas for Request Validation
# ==========================================

class RunToolRequest(BaseModel):
    tool: str = Field(..., description="The name of the MCP tool to run.")
    input: Dict[str, Any] = Field(..., description="The input arguments for the tool.")

# ==========================================
# Tool Logic & Data
# ==========================================

def get_simulated_temperature(city: str) -> str:
    """
    Simulates fetching temperature data for a given city.
    """
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

# MCP Tool Definition
GET_TEMPERATURE_TOOL = {
    "name": "get_temperature",
    "description": "Get the current temperature of a city",
    "inputSchema": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "City name"
            }
        },
        "required": ["city"]
    }
}

# ==========================================
# API Endpoints
# ==========================================

@app.get("/", tags=["System"])
async def root():
    """
    Base URL returning service status and available endpoints.
    """
    return {
        "service": "MCP Temperature Server",
        "status": "running",
        "endpoints": [
            "/health",
            "/mcp/tools",
            "/mcp/run"
        ]
    }

@app.get("/health", tags=["System"])
async def health_check():
    """
    Returns the server status.
    """
    return {
        "status": "ok",
        "message": "MCP Server is running properly."
    }

@app.get("/mcp/tools", tags=["MCP"])
async def list_tools():
    """
    Returns the list of available MCP tools exposed by this server.
    """
    return {"tools": [GET_TEMPERATURE_TOOL]}

@app.post("/mcp/run", tags=["MCP"])
async def run_tool(request: RunToolRequest):
    """
    Runs an MCP tool with the provided input.
    """
    if request.tool != "get_temperature":
        raise HTTPException(status_code=404, detail=f"Tool '{request.tool}' not found.")
    
    city = request.input.get("city")
    if not city:
        raise HTTPException(status_code=400, detail="Missing required input: 'city'")
    
    temperature = get_simulated_temperature(city)
    
    return {
        "city": city,
        "temperature": temperature
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
