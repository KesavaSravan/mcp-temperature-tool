# MCP Temperature Tool Server

A Model Context Protocol (MCP) tool server built with Python and FastAPI, designed to be deployed on cloud platforms like Render, Vercel, and Railway.

## Tool Details
* **Name**: `get_temperature`
* **Description**: Get the current temperature of a city.
* **Input**: JSON with a `city` string property.

## Endpoints
* `GET /` - Base URL showing service status and available endpoints.
* `GET /health` - Health check.
* `GET /mcp/tools` - List available MCP tools.
* `POST /mcp/run` - Execute an MCP tool.

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

To get the temperature of a city:

```bash
curl -X POST http://127.0.0.1:8000/mcp/run \
  -H "Content-Type: application/json" \
  -d '{"tool": "get_temperature", "input": {"city": "Hyderabad"}}'
```
