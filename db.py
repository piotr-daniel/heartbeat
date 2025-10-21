import os
from datetime import datetime
from dotenv import load_dotenv
from fastapi import HTTPException
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# --- Connection Pool Setup ---
db_pool: pool.SimpleConnectionPool | None = None


def init_db_pool(minconn: int = 1, maxconn: int = 5):
    """Initialize the PostgreSQL connection pool."""
    global db_pool
    if db_pool is None:
        db_pool = pool.SimpleConnectionPool(
            minconn=minconn,
            maxconn=maxconn,
            dsn=DATABASE_URL,
            cursor_factory=RealDictCursor,
        )
        print("✅ Database connection pool initialized.")
    return db_pool


def get_connection():
    """Get a connection from the pool."""
    global db_pool
    if db_pool is None:
        raise HTTPException(status_code=500, detail="Database pool not initialized.")
    return db_pool.getconn()


def release_connection(conn):
    """Release the connection back to the pool."""
    global db_pool
    if db_pool:
        db_pool.putconn(conn)


# --- CRUD Functions ---

def create_log(log_type: str, clients: int):
    """Insert a log entry into the logs table."""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO logs (type, timestamp, no_of_clients)
                VALUES (%s, %s, %s)
                RETURNING id;
                """,
                (log_type, datetime.now(), clients),
            )
            log_id = cur.fetchone()["id"]
        conn.commit()
        return {"id": log_id, "message": "Log created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if conn:
            release_connection(conn)


def get_logs():
    """Retrieve all log entries."""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM logs ORDER BY timestamp DESC;")
            logs = cur.fetchall()
            return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            release_connection(conn)


def update_stats(name: str, value):
    """Update or insert the stats record."""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE stats
                SET value = %s, timestamp = %s
                WHERE name = %s
                RETURNING *;
                """,
                (value, datetime.now(), name),
            )
            updated_stats = cur.fetchall()
        conn.commit()
        return updated_stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            release_connection(conn)


def get_stats():
    """Retrieve all stats entries."""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM stats ORDER BY timestamp DESC;")
            stats = cur.fetchall()
            stats_list = {row['name']: row['value'] for row in stats}
            return stats_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            release_connection(conn)


def close_pool():
    """Close all connections in the pool (useful on shutdown)."""
    global db_pool
    if db_pool:
        db_pool.closeall()
        print("Database pool closed.")
