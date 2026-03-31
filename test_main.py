import pytest
from fastapi.testclient import TestClient
from main import app
import os

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "service" in response.json()

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "MCP Temperature Server"
    assert "endpoints" in data

def test_mcp_initialize():
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize"
    }
    response = client.post("/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["jsonrpc"] == "2.0"
    assert data["id"] == 1
    assert "protocolVersion" in data["result"]

def test_mcp_tools_list():
    payload = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list"
    }
    response = client.post("/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data["result"]
    tools = {t["name"] for t in data["result"]["tools"]}
    assert "get_temperature" in tools
    assert "get_temperature_forecast" in tools
    assert "convert_temperature" in tools

def test_mcp_convert_temperature():
    payload = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "convert_temperature",
            "arguments": {
                "value": 100,
                "from_unit": "C",
                "to_unit": "F"
            }
        }
    }
    response = client.post("/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "content" in data["result"]
    assert "212.0°F" in data["result"]["content"][0]["text"]

@pytest.mark.asyncio
async def test_mcp_get_temperature():
    from main import get_live_temperature
    result = await get_live_temperature("London")
    assert isinstance(result, str)
    if os.getenv("OWM_API_KEY"):
        assert "°C" in result or "not found" in result or "Network error" in result or "Error" in result
    else:
        assert "Error: OWM_API_KEY environment variable not set." in result

@pytest.mark.asyncio
async def test_mcp_get_temperature_forecast():
    from main import get_live_forecast
    result = await get_live_forecast("London")
    assert isinstance(result, str)
    if os.getenv("OWM_API_KEY"):
        assert "°C" in result or "not found" in result or "Network error" in result or "Error" in result
    else:
        assert "Error: OWM_API_KEY environment variable not set." in result

def test_mcp_tools_call_get_temperature_endpoint():
    payload = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "get_temperature",
            "arguments": {
                "city": "London"
            }
        }
    }
    response = client.post("/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "content" in data["result"]
    assert isinstance(data["result"]["content"][0]["text"], str)

def test_mcp_tools_call_get_temperature_forecast_endpoint():
    payload = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "get_temperature_forecast",
            "arguments": {
                "city": "London"
            }
        }
    }
    response = client.post("/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "content" in data["result"]
    assert isinstance(data["result"]["content"][0]["text"], str)
