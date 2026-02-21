from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import json
import numpy as np
import os

app = FastAPI()

# Load telemetry file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "q-vercel-latency.json")

with open(FILE_PATH) as f:
    data = json.load(f)


# ✅ Handle OPTIONS explicitly (preflight)
@app.options("/")
async def options_handler():
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*"
        }
    )


@app.post("/")
async def analyze(request: Request):
    payload = await request.json()
    regions = payload.get("regions", [])
    threshold = payload.get("threshold_ms", 0)

    result = {}

    for region in regions:
        records = [r for r in data if r.get("region") == region]

        if not records:
            continue

        latencies = [r.get("latency_ms", r.get("latency")) for r in records]
        uptimes = [r.get("uptime_pct", r.get("uptime")) for r in records]

        result[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": sum(1 for l in latencies if l > threshold),
        }

    return JSONResponse(
        content=result,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*"
        }
    )
