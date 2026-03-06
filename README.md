# MCP Temperature Tool Server

A Model Context Protocol (MCP) tool server built with Python and FastAPI, designed to be deployed on cloud platforms like Render, Vercel, and Railway.

## Tool Details

**1. `get_temperature`**
* **Description**: Get the current simulated temperature of a city.
* **Input**: JSON with a `city` string property.

**2. `get_temperature_forecast`**
* **Description**: Get the simulated temperature forecast for a city for the next 3 days.
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

**4. Run the server**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Cloud Deployment (Vercel, Render, Railway)

This server relies on standard `FastAPI` and `uvicorn`, making it natively compatible with platforms such as Render, Railway, or Vercel (via `vercel.json`).

* **Render / Railway**: These platforms will automatically detect Python due to `requirements.txt` and you can use the start command `uvicorn main:app --host 0.0.0.0 --port $PORT` (Render/Railway use the `$PORT` environment variable).
* **Vercel**: You may need a simple `vercel.json` file configuring `rewrites` to point all traffic to `main:app` as a Serverless Function.

## Example Request

To get the temperature of a city using the MCP JSON-RPC endpoint:

```bash
curl -X POST http://127.0.0.1:8000/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "get_temperature", "arguments": {"city": "Hyderabad"}}}'
```
