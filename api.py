from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import sqlite3
import os
from typing import List, Optional

app = FastAPI(title="DNS Filter API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.join("database", "dns_filter.db")

def get_db_connection():
    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=500, detail="Database file not found")
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def read_root():
    # Serve the dashboard HTML file
    return FileResponse("dashboard.html")

@app.get("/api/stats")
async def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Total blocked domains
        cursor.execute("SELECT COUNT(*) FROM blocked")
        total_blocked = cursor.fetchone()[0]
        
        # Blocked queries count
        cursor.execute("SELECT COUNT(*) FROM queries WHERE action='blocked'")
        blocked_queries = cursor.fetchone()[0]
        
        # Allowed queries count
        cursor.execute("SELECT COUNT(*) FROM queries WHERE action='allowed'")
        allowed_queries = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_blocked_domains": total_blocked,
            "blocked_queries": blocked_queries,
            "allowed_queries": allowed_queries,
            "total_queries": blocked_queries + allowed_queries
        }
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/top-blocked")
async def get_top_blocked_domains(limit: int = 10):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT domain, COUNT(*) as count 
            FROM queries 
            WHERE action='blocked'
            GROUP BY domain 
            ORDER BY count DESC 
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [{"domain": row["domain"], "count": row["count"]} for row in rows]
    except Exception as e:
        conn.close()
        return []

@app.get("/api/logs/blocked")
async def get_blocked_logs(limit: int = 100):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT timestamp, client_ip, domain, query_type 
            FROM queries 
            WHERE action='blocked'
            ORDER BY id DESC 
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    except Exception as e:
        conn.close()
        return []

@app.get("/api/logs/allowed")
async def get_allowed_logs(limit: int = 100):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT timestamp, client_ip, domain, query_type, response_time 
            FROM queries 
            WHERE action='allowed'
            ORDER BY id DESC 
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    except Exception as e:
        conn.close()
        return []

@app.get("/api/domains")
async def get_all_domains(limit: int = 1000):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT domain 
            FROM blocked 
            ORDER BY domain 
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [row["domain"] for row in rows]
    except Exception as e:
        conn.close()
        return []
