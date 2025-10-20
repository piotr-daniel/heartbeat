import os
import psycopg2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from datetime import datetime


# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    """Create a new DB connection."""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def create_log(clients):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO logs (type, timestamp, no_of_clients) VALUES (%s, %s, %s) RETURNING id;",
            ("connect", datetime.now(), clients)
        )
        log_id = cur.fetchone()["id"]
        print('new')
        conn.commit()
        cur.close()
        conn.close()
        return {"message": f"Log created with ID {log_id}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def get_logs():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM logs;")
        logs = cur.fetchall()
        print(logs)
        cur.close()
        conn.close()
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
