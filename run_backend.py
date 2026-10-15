#!/usr/bin/env python
"""
PRICEGUARD Backend Runner.
Launches the FastAPI Uvicorn REST API server.

Usage:
  python run_backend.py
  python run_backend.py --port 8000 --reload
"""
import argparse
import sys
import os

# Ensure current directory is in Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def main():
    parser = argparse.ArgumentParser(description="PRICEGUARD FastAPI REST Server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host address to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on (default: 8000)")
    parser.add_argument("--reload", action="store_true", default=True, help="Enable auto-reload on code changes (default: True)")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes")
    args = parser.parse_args()

    import uvicorn
    print(f"""
    ===================================================================
    🛡️  PRICEGUARD Decision Support System - RESTful API Backend
    ===================================================================
    📡 Server running at : http://{args.host}:{args.port}
    📚 Interactive Docs  : http://localhost:{args.port}/docs
    📖 ReDoc Specs       : http://localhost:{args.port}/redoc
    ===================================================================
    """)
    uvicorn.run(
        "backend.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers if not args.reload else None
    )

if __name__ == "__main__":
    main()
