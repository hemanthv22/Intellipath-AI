import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Import database and models
from database.db import engine, Base
from models import user_model, history_model  # Ensures SQLAlchemy knows about the User table

# Import routers (Added analytics_routes here)
from routes import (
    auth_routes, 
    assessment_routes, 
    resume_routes, 
    interview_routes, 
    assistant_routes, 
    roadmap_routes,
    analytics_routes  
)

# Initialize Database Tables in PostgreSQL
# This will create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="IntelliPath AI API",
    description="Backend for AI-powered career path analysis",
    version="1.0"
)

# --- CORS CONFIGURATION ---
# We use explicit origins here so that allow_credentials=True works safely 
# without crashing FastAPI, while covering all common local development ports.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000", 
        "http://localhost:8000",
        "http://127.0.0.1:5500",  # Default VS Code Live Server
        "http://localhost:5500",
        "http://127.0.0.1:3000",  # React default (just in case)
        "http://localhost:3000"
    ], 
    allow_credentials=True,
    allow_methods=["*"],      # Allows POST (for uploads), GET, PUT, DELETE
    allow_headers=["*"],      # Allows Authorization headers and multipart forms
)

# --- API ROUTE REGISTRATION ---
# Prefixing with /api keeps your API endpoints distinct from your frontend pages
app.include_router(auth_routes.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(assessment_routes.router, prefix="/api/assessment", tags=["Assessment"])
app.include_router(resume_routes.router, prefix="/api/resume", tags=["Resume"])
app.include_router(interview_routes.router, prefix="/api/interview", tags=["Interview"])
app.include_router(assistant_routes.router, prefix="/api/assistant", tags=["Assistant"])
app.include_router(roadmap_routes.router, prefix="/api/roadmap", tags=["Roadmap"])

# Added Job Analytics Router
app.include_router(analytics_routes.router, prefix="/api/analytics", tags=["Job Analytics"])

@app.get("/api")
def health_check():
    """Simple endpoint to verify the backend is alive."""
    return {"status": "IntelliPath Backend Running", "database": "Connected"}

# --- STATIC FILES (Serving the Frontend) ---
# IMPORTANT: This must come AFTER the API routes to avoid catching API calls
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
frontend_path = os.path.join(BASE_DIR, 'frontend')

if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
else:
    print(f"Warning: Frontend folder not found at {frontend_path}")

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    # reload=True is great for development; it restarts the server on save
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)