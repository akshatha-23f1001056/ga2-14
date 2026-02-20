from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import json
import numpy as np

app = FastAPI()

# Load telemetry data
with open("q-vercel-latency.json") as f:
    telemetry = json.load(f)

# Enable CORS manually
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

@app.post("/api/latency")
async def analyze(data: dict):

    regions = data["regions"]
    threshold = data["threshold_ms"]

    result = {}

    for region in regions:
        region_data = [r for r in telemetry if r["region"] == region]

        latencies = [r["latency_ms"] for r in region_data]
        uptimes = [r["uptime"] for r in region_data]

        avg_latency = float(np.mean(latencies))
        p95_latency = float(np.percentile(latencies, 95))
        avg_uptime = float(np.mean(uptimes))
        breaches = sum(1 for l in latencies if l > threshold)

        result[region] = {
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "avg_uptime": avg_uptime,
            "breaches": breaches
        }

    return JSONResponse(content=result)
