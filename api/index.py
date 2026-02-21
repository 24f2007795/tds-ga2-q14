from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import numpy as np
import os

app = FastAPI()

# Enable CORS for all origins and methods
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load telemetry file safely for Vercel

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "q-vercel-latency.json")

with open(FILE_PATH) as f:
    data = json.load(f)


@app.post("/")
async def analyze(payload: dict):
    regions = payload.get("regions", [])
    threshold = payload.get("threshold_ms", 0)

    result = {}

    for region in regions:
        records = [r for r in data if r.get("region") == region]

        if not records:
            continue

        # Adjust keys if needed (based on your telemetry file)
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
        headers={"Access-Control-Allow-Origin": "*"}
    )
