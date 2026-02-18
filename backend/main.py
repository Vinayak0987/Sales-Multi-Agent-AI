"""
Strategic Grid — Backend API Server
FastAPI application powering the Strategic Grid Dashboard.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import leads, agents, dashboard

app = FastAPI(
    title="Strategic Grid API",
    description="Backend API for the Strategic Grid Sales Intelligence Dashboard",
    version="2.4.0"
)

# CORS — allow the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(leads.router, prefix="/api/leads", tags=["Leads"])
app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])


@app.get("/")
def health():
    return {"status": "online", "system": "Strategic Grid", "version": "2.4.0"}
