# 🫀 Heartbeat Server

![Python](https://img.shields.io/badge/Python-3.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-async-green)
![Status](https://img.shields.io/badge/Alive-💓-pink)

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

Browser (JS + WebSocket) > 
FastAPI Routes (/update-stat, /health, /ws) >
Database Layer (psycopg2 / SQLAlchemy) >
PostgreSQL (persistent stats)

---

## 🛠️ Setup Instructions

### 1️⃣ Clone the repo

```
git clone https://github.com/piotr-daniel/heartbeat.git
cd heartbeat
```

### 2️⃣ Create and activate a virtual environment

```
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### 3️⃣ Install dependencies

```
pip install -r requirements.txt
```

### 4️⃣ Create .env

```
DATABASE_URL=postgresql://user:password@host:port/dbname
```

### 5️⃣ Run locally

```
uvicorn app.main:app --reload
```

---

## 📚 Example Endpoints

| Method | Endpoint    | Description                                      |
| ------ | ----------- |--------------------------------------------------|
| `GET`  | `/`         | Render the main heartbeat page                   |
| `POST` | `/update-stat` | Example - add one minute to the heart’s lifetime |
| `WS`   | `/ws`       | Real-time updates (optional)                     |
| `GET`  | `/health`   | Application health and database status           |


---


## 💬 Final Notes

This project started as a playful experiment but evolved into a living example of a full-stack, production-ready Python app.  
If you’re exploring **FastAPI**, **WebSockets**, or **Render deployment**, this is a great starting point — and an invitation to build on it.

⭐ If you found this project helpful or inspiring, consider giving it a star — it helps keep the heart beating!
