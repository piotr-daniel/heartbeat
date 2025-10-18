from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import asyncio, time

app = FastAPI()

# Mount static files (JS/CSS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Keep track of connected clients
active_clients = set()
beat_interval = 1.0
alive = False


@app.get("/")
async def get_index():
    with open("templates/index.html", "r") as f:
        return HTMLResponse(f.read())


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    active_clients.add(ws)
    global alive
    alive = True
    print(f"💓 Client connected ({len(active_clients)} total)")
    try:
        while True:
            await asyncio.sleep(1)  # Keep connection alive
    except WebSocketDisconnect:
        active_clients.remove(ws)
        print(f"💔 Client disconnected ({len(active_clients)} left)")
        if not active_clients:
            alive = False


async def heartbeat_loop():
    global beat_interval, alive
    while True:
        if len(active_clients) > 1:
            # Adjust beat speed based on connected clients
            beat_interval = max(0.4, 1.6 - 0.1 * len(active_clients))
            msg = {"type": "heartbeat", "interval": beat_interval, "timestamp": time.time(), "active_clients": len(active_clients)}
            for ws in list(active_clients):
                try:
                    await ws.send_json(msg)
                except:
                    active_clients.discard(ws)
        else:
            # No clients → flatline
            msg = {"type": "flatline"}
            for ws in list(active_clients):
                try:
                    await ws.send_json(msg)
                except:
                    active_clients.discard(ws)
        await asyncio.sleep(beat_interval)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(heartbeat_loop())
