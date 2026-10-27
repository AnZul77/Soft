#!/usr/bin/env python
"""
Launcher for AI-Powered Investment Intelligence Platform Backend.
Can be run from anywhere: python run_backend.py
"""
import sys
from pathlib import Path

# Ensure 'backend' directory is on sys.path
root_dir = Path(__file__).resolve().parent
backend_dir = root_dir / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.config import settings

def main():
    import uvicorn
    print("\n" + "=" * 65)
    print("   AI-POWERED INVESTMENT INTELLIGENCE PLATFORM BACKEND")
    print(f"   Version: {settings.VERSION}")
    print("=" * 65)
    print(f"   [API Server]  http://127.0.0.1:8000")
    print(f"   [Swagger UI]  http://127.0.0.1:8000/docs")
    print(f"   [ReDoc]       http://127.0.0.1:8000/redoc")
    print(f"   [Health]      http://127.0.0.1:8000/health")
    print(f"   [Database]    {settings.DATABASE_URL}")
    print("=" * 65 + "\n")
    
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True, app_dir=str(backend_dir))

if __name__ == "__main__":
    main()
