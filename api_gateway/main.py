"""
Generic API Gateway with automatic routing based on config.yaml
- All requests come to port 8000
- /users → distributed to 8001 (v1) or 8002 (v2)
- /orders → fixed to 8003
"""
from fastapi import FastAPI, Request, HTTPException, Body
from fastapi.responses import JSONResponse
import requests
import random
import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.config_loader import load_config

app = FastAPI(title="Generic API Gateway", version="1.0")

config = load_config()
routing_percentage = config.get("api_gateway", {}).get("routing_percentage", 0.5)
microservices = config.get("microservices", {})

SERVICE_PREFIXES = {}
for name, svc in microservices.items():
    url = svc.get("url", "").rstrip("/")  # ensure no trailing slash
    if "user" in name:
        SERVICE_PREFIXES.setdefault("users", []).append(url)
    elif "order" in name:
        SERVICE_PREFIXES.setdefault("orders", []).append(url)


def choose_service(prefix: str) -> str:
    """Select appropriate service URL based on prefix and routing rule"""
    services = SERVICE_PREFIXES.get(prefix)
    if not services:
        raise HTTPException(status_code=404, detail=f"No service found for prefix '{prefix}'")

    if len(services) > 1:
        # Apply strangler pattern
        chosen = services[0] if random.random() < routing_percentage else services[1]
    else:
        chosen = services[0]

    return chosen


def forward_request(method: str, url: str, **kwargs) -> requests.Response:
    """Forward HTTP request to the actual microservice"""
    try:
        response = requests.request(method, url, timeout=15, **kwargs)
        return response
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {e}")

@app.get("/config/routing-percentage")
async def get_routing_percentage():
    return {
        "routing_percentage": routing_percentage,
        "description": "Current percentage of traffic routed to user_service_v1",
    }


@app.put("/config/routing-percentage")
async def update_routing_percentage(data: dict = Body(...)):
    global routing_percentage
    try:
        new_value = float(data.get("routing_percentage"))
        if not 0 <= new_value <= 1:
            raise ValueError("routing_percentage must be between 0 and 1")

        routing_percentage = new_value
        print(f"⚙️ Updated routing_percentage to {routing_percentage}")
        return {
            "message": "Routing percentage updated successfully.",
            "new_routing_percentage": routing_percentage,
        }

    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid routing_percentage value. Must be between 0 and 1.")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "routing_percentage": routing_percentage,
        "service_prefixes": SERVICE_PREFIXES,
    }


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Simple request logging middleware"""
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    print(
        f"[{request.method}] {request.url.path} -> {response.status_code} "
        f"({process_time:.2f} ms)"
    )
    return response


@app.api_route("/{prefix}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def universal_router(prefix: str, path: str, request: Request):
    """
    Universal route entry point:
      POST /users  →  http://user_service:8001 or user_service_v2:8002
      GET  /orders →  http://order_service:8003
    """
    try:
        base_url = choose_service(prefix)
        target_url = f"{base_url}/{prefix}"
        if path:
            target_url += f"/{path}"

        headers = dict(request.headers)
        headers.pop("host", None)
        headers.pop("content-length", None)
        body = await request.body()
        params = dict(request.query_params)

        print(f"Forwarding {request.method} → {target_url}")

        response = forward_request(
            method=request.method,
            url=target_url,
            headers=headers,
            params=params if request.method == "GET" else None,
            data=body if request.method in ["POST", "PUT", "DELETE"] else None,
        )

        try:
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except Exception:
            return JSONResponse(content={"raw": response.text}, status_code=response.status_code)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
