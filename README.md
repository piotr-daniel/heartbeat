# 🫀 Heartbeat Server

### A living, breathing FastAPI app that tracks its own life.

This project is a quirky full-stack experiment that explores **state persistence, live updates, and time-based interactivity**.  
Each visitor sees the “heart”’s remaining lifetime ticking down — and every click **extends its life by one minute**.

It’s a playful way to show off **Python, FastAPI, PostgreSQL, WebSockets, and JavaScript** working together.

---

## 🚀 Features

- **Dynamic Heartbeat UI** — see the app’s life ticking down in real-time.  
- **Click to Extend Life** — each click adds 1 minute to the end-of-life timer.  
- **Persistent Storage** — life data stored in PostgreSQL using psycopg2 (or ORM if preferred).  
- **Live Sync** — optional WebSocket broadcasting keeps all connected users in sync.  
- **Jinja2 Templates** — dynamic HTML rendering from Python data.  
- **Production-ready setup** — compatible with Render, Railway, or local Docker.

---

## 🧠 Tech Stack

| Layer | Tech | Purpose |
|-------|------|----------|
| Backend | **FastAPI** | REST + WebSocket endpoints |
| Frontend | **HTML / JS** | Dynamic updates and click handling |
| Database | **PostgreSQL** | Persistent state for heart stats |
| Template Engine | **Jinja2** | Server-rendered HTML |
| Deployment | **Render / Railway / Docker** | Production hosting |

---

## 🧩 Architecture Overview

Browser (JS + WebSocket)
|
v
FastAPI Routes (/add-life, /stats, /ws)
|
v
Database Layer (psycopg2 / SQLAlchemy)
|
v
PostgreSQL (persistent stats)

---

## 🛠️ Setup Instructions

### 1️⃣ Clone the repo

```bash
git clone https://github.com/yourusername/heartbeat-server.git
cd heartbeat-server
```

### 2️⃣ Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 1️⃣ Clone the repo

```bash
DATABASE_URL=postgresql://user:password@host:port/dbname
```

### 5️⃣ Run locally

```bash
uvicorn app.main:app --reload
```

---

## 📚 Example Endpoints

| Method | Endpoint    | Description                            |
| ------ | ----------- | -------------------------------------- |
| `GET`  | `/`         | Render the main heartbeat page         |
| `POST` | `/add-life` | Add one minute to the heart’s lifetime |
| `GET`  | `/stats`    | Fetch all stored stats                 |
| `WS`   | `/ws`       | Real-time updates (optional)           |
| `GET`  | `/health`   | Application health and database status |
