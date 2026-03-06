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

class ToolDescription(BaseModel):
    name: str
    description: str
    input_schema: dict

# ==========================================
# Tool Logic & Data
# ==========================================

def get_simulated_temperature(city: str) -> str:
    """
    Simulates fetching temperature data for a given city.
    In a real-world scenario, you would call an external WEATHER API here.
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
    # Return a simulated default if city is not found in mock data
    return mock_data.get(city.strip().lower(), "20°C")

# MCP Tool Definition
GET_TEMPERATURE_TOOL = {
    "name": "get_temperature",
    "description": "Get the current temperature of a given city.",
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "The name of the city, e.g., Hyderabad"
            }
        },
        "required": ["city"]
    }
}

# ==========================================
# API Endpoints
# ==========================================

@app.get("/health", tags=["System"])
async def health_check():
    """
    Returns the server status.
    """
    return {"status": "ok", "message": "MCP Server is running properly."}

@app.post("/mcp/tools", response_model=List[ToolDescription], tags=["MCP"])
async def list_tools():
    """
    Returns the list of available MCP tools exposed by this server.
    """
    return [GET_TEMPERATURE_TOOL]

@app.post("/mcp/run", tags=["MCP"])
async def run_tool(request: RunToolRequest):
    """
    Runs an MCP tool with the provided input.
    """
    if request.tool != "get_temperature":
        raise HTTPException(status_code=404, detail=f"Tool '{request.tool}' not found.")
    
    # Extract the city from the input payload
    city = request.input.get("city")
    if not city:
        raise HTTPException(status_code=400, detail="Missing required input: 'city'")
    
    # Process the request using our tool logic
    temperature = get_simulated_temperature(city)
    
    # Return the expected JSON response
    return {
        "city": city,
        "temperature": temperature
    }

if __name__ == "__main__":
    import uvicorn
    # Run the server using uvicorn when executing the script directly
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
