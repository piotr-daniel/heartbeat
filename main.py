import asyncio
import json
import time
from db import init_db_pool, close_pool, get_stats, get_logs, create_log, update_stats, get_connection
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Heartbeat Server", version="1.0")

templates = Jinja2Templates(directory="templates")

# Static + templates
app.mount("/static", StaticFiles(directory="static"), name="static")

# Allow local + deployed connections
app.add_middleware(
    CORSMiddleware,  # type: ignore
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["Content-Type", "Authorization"],
)

active_clients = set()
beat_interval = 1.0
alive = True


@app.api_route("/health", methods=["GET", "HEAD"])
async def health_check(request: Request):
    """
    Health check endpoint compatible with browsers and uptime services.
    HEAD → headers only
    GET → full JSON response
    """
    db_status = "ok"
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
    except Exception:
        db_status = "error"
    finally:
        if conn:
            conn.close()

    status_code = status.HTTP_200_OK if db_status == "ok" else status.HTTP_503_SERVICE_UNAVAILABLE

    headers = {
        "X-App-Status": "ok" if db_status == "ok" else "degraded",
        "X-DB-Status": db_status,
        "X-Timestamp": datetime.utcnow().isoformat() + "Z",
    }

    # Return headers only for HEAD
    if request.method == "HEAD":
        return Response(status_code=status_code, headers=headers)

    # Return JSON for GET
    return JSONResponse(
        {
            "status": headers["X-App-Status"],
            "database": headers["X-DB-Status"],
            "timestamp": headers["X-Timestamp"],
        },
        status_code=status_code,
        headers=headers,
    )


@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    """
    Serve the heartbeat page with live stats from the DB
    """
    stats = get_stats()
    stats['heart_life'] = (datetime.now() + timedelta(seconds=int(stats['heart_life']))).strftime(
                "%d %B %Y - %H:%M:%S")
    update_stats('total_visits', stats['total_visits'] + 1)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "stats": stats
        }
    )


@app.post("/update-stat")
async def update_stat(request: Request):
    stats = get_stats()
    data = await request.json()
    name = data["name"]
    value = data["value"]
    update_stats(name, stats[name]+value)
    print(f"Updating {name} → {value}")
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """Handle WebSocket connections"""
    await ws.accept()
    active_clients.add(ws)

    print(f"💓 Client connected ({len(active_clients)} total)")
    await run_in_threadpool(create_log, "connect", len(active_clients))

    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        active_clients.remove(ws)
        print(f"💔 Client disconnected ({len(active_clients)} left)")
        await run_in_threadpool(create_log, "disconnect", len(active_clients))


async def heartbeat_loop():
    """Send pulse messages to all connected clients at interval"""
    global beat_interval
    global alive

    while True:
        if len(active_clients) > 1:
            stats = get_stats()
            if stats['max_clients'] < len(active_clients):
                update_stats('max_clients', len(active_clients))

            if stats["heart_life"] <= 0 and alive:
                update_stats('number_of_deaths', stats['number_of_deaths'] + 1)
                update_stats('is_alive', 0)
                alive = False
            if stats["heart_life"] > 0 and not alive:
                update_stats('number_of_births', stats['number_of_births'] + 1)
                update_stats('is_alive', 1)
                alive = True

            beat_interval = max(0.4, 1.6 - 0.1 * min(len(active_clients), 12))
            update_stats("heart_life", stats["heart_life"] - 2)
            stats["heart_life"] = (datetime.now() + timedelta(seconds=int(stats["heart_life"]))).strftime(
                "%d %B %Y - %H:%M:%S")
            msg = {
                "type": "heartbeat",
                "interval": beat_interval,
                "timestamp": time.time(),
                "active_clients": len(active_clients),
                "max_clients": int(stats["max_clients"]),
                "total_visits": int(stats["total_visits"]),
                "number_of_births": int(stats["number_of_births"]),
                "heart_life": stats["heart_life"],
            }
            await broadcast(msg)
        else:
            msg = {"type": "flatline"}
            await broadcast(msg)
        await asyncio.sleep(beat_interval)


async def broadcast(message: dict):
    """Broadcast a message to all active clients"""
    disconnected = []
    for ws in list(active_clients):
        try:
            await ws.send_json(message)
        except Exception:
            disconnected.append(ws)
    for ws in disconnected:
        active_clients.discard(ws)


@app.on_event("startup")
async def on_startup():
    """Start background heartbeat"""
    init_db_pool()
    asyncio.create_task(heartbeat_loop())
    print("🚀 Heartbeat server started.")
    await run_in_threadpool(create_log, "server started", len(active_clients))


@app.on_event("shutdown")
async def shutdown_event():
    close_pool()


def timestamp_to_date(value, fmt="%Y-%m-%d"):
    return datetime.fromtimestamp(value).strftime(fmt)


templates.env.filters["timestamp_to_date"] = timestamp_to_date


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
