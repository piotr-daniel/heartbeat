import asyncio
import json
import os
import time
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Heartbeat Server", version="1.0")

# Static + templates
app.mount("/static", StaticFiles(directory="static"), name="static")

# Allow local + deployed connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

active_clients = set()
beat_interval = 1.0
alive = False
log_file = "heartbeat_log.json"


@app.get("/")
async def get_index():
    """Serve the main heartbeat page"""
    with open("templates/index.html", "r") as f:
        return HTMLResponse(f.read())


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """Handle WebSocket connections"""
    await ws.accept()
    active_clients.add(ws)
    global alive
    alive = True

    print(f"💓 Client connected ({len(active_clients)} total)")
    await log_event("connect", len(active_clients))

    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        active_clients.remove(ws)
        print(f"💔 Client disconnected ({len(active_clients)} left)")
        await log_event("disconnect", len(active_clients))
        if not active_clients:
            alive = False


async def heartbeat_loop():
    """Send pulse messages to all connected clients at interval"""
    global beat_interval
    while True:
        if len(active_clients) > 1:
            # smooth scaling: logarithmic feel
            beat_interval = max(0.4, 1.6 - 0.1 * min(len(active_clients), 12))
            msg = {
                "type": "heartbeat",
                "interval": beat_interval,
                "timestamp": time.time(),
                "active_clients": len(active_clients),
            }
            await broadcast(msg)
            await log_event("beat", len(active_clients))
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


async def log_event(event_type: str, clients: int):
    """Append simple heartbeat log to file"""
    event = {
        "time": datetime.now().isoformat(),
        "event": event_type,
        "clients": clients,
    }
    with open(log_file, "a") as f:
        f.write(json.dumps(event) + "\n")


@app.on_event("startup")
async def on_startup():
    """Start background heartbeat"""
    asyncio.create_task(heartbeat_loop())
    print("🚀 Heartbeat server started.")


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
