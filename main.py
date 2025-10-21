import asyncio
import json
import time
from db import init_db_pool, close_pool, get_stats, get_logs, create_log, update_stats
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
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
alive = False
# stats_list = {s['name']: s['value'] for s in get_stats()}


@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    """
    Serve the heartbeat page with live stats from the DB
    """
    stats = get_stats()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "stats": stats
        }
    )


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """Handle WebSocket connections"""
    await ws.accept()
    active_clients.add(ws)
    global alive
    alive = True

    print(f"💓 Client connected ({len(active_clients)} total)")
    await run_in_threadpool(create_log, "connect", len(active_clients))

    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        active_clients.remove(ws)
        print(f"💔 Client disconnected ({len(active_clients)} left)")
        await run_in_threadpool(create_log, "disconnect", len(active_clients))
        if not active_clients:
            alive = False


async def heartbeat_loop():
    """Send pulse messages to all connected clients at interval"""
    global beat_interval
    while True:
        if len(active_clients) > 1:
            stats_list = get_stats()
            if stats_list['max_clients'] < len(active_clients):
                update_stats('max_clients', len(active_clients))
            beat_interval = max(0.4, 1.6 - 0.1 * min(len(active_clients), 12))
            msg = {
                "type": "heartbeat",
                "interval": beat_interval,
                "timestamp": time.time(),
                "active_clients": len(active_clients),
                "max_clients": int(stats_list['max_clients']),
            }
            await broadcast(msg)
        else:
            msg = {"type": "flatline"}
            # update_stats('number_of_deaths', 1)
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


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
