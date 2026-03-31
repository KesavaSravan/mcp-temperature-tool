# MCP Temperature Tool Server

A Model Context Protocol (MCP) tool server built with Python and FastAPI, designed to be deployed on cloud platforms like Render, Vercel, and Railway.

## Tool Details

**1. `get_temperature`**
* **Description**: Get the current live temperature of a city (requires `OWM_API_KEY`).
* **Input**: JSON with a `city` string property.

**2. `get_temperature_forecast`**
* **Description**: Get the live temperature forecast for a city for the next 3 days (requires `OWM_API_KEY`).
* **Input**: JSON with a `city` string property.

**3. `convert_temperature`**
* **Description**: Convert a temperature between Celsius (°C) and Fahrenheit (°F).
* **Input**: JSON with `value` (number), `from_unit` (string: 'C' or 'F'), and `to_unit` (string: 'C' or 'F').

## Endpoints

* `GET /health` - HTTP health check endpoint.
* `POST /` - Standard MCP JSON-RPC endpoint. Standard payload methods supported:
  * `initialize`
  * `tools/list`
  * `tools/call`

## Local Setup

**1. Create a virtual environment**
```bash
python -m venv venv
```

**2. Activate it**
* Windows (CMD): `venv\Scripts\activate.bat`
* Windows (PowerShell): `.\venv\Scripts\Activate.ps1`
* Linux/macOS: `source venv/bin/activate`

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure Environment Variables**
Create a `.env` file in the root directory and add your OpenWeatherMap API key:
```ini
OWM_API_KEY=your_api_key_here
```

**5. Run the server**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Cloud Deployment (Vercel, Render, Railway)

This server relies on standard `FastAPI` and `uvicorn`, making it natively compatible with platforms such as Render, Railway, or Vercel (via `vercel.json`).

* **Render / Railway**: These platforms will automatically detect Python due to `requirements.txt` and you can use the start command `uvicorn main:app --host 0.0.0.0 --port $PORT` (Render/Railway use the `$PORT` environment variable).
* **Vercel**: The project includes a `vercel.json` file. It is pre-configured to use the `@vercel/python` builder, meaning you can deploy it natively to Vercel without any extra configuration.

## Testing

A comprehensive test suite is provided in `test_main.py`. This tests the FastAPI endpoints, the MCP JSON-RPC protocol handling, and all tool execution paths.

**1. Install test dependencies**
```bash
pip install pytest pytest-asyncio httpx
```

**2. Run the tests**
```bash
pytest test_main.py -v
```

## Example Request

To get the temperature of a city using the MCP JSON-RPC endpoint:

```bash
curl -X POST http://127.0.0.1:8000/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "get_temperature", "arguments": {"city": "Hyderabad"}}}'
```
