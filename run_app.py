#!/usr/bin/env python
"""
PRICEGUARD Full-Stack Unified Launcher.
Runs both the FastAPI REST Backend (port 8000) and the Streamlit Dashboard (port 8501) concurrently.

Usage:
  python run_app.py              # Runs both Backend + Streamlit Dashboard
  python run_app.py --backend    # Runs Backend API only
  python run_app.py --dashboard  # Runs Streamlit Dashboard only
"""
import sys
import os
import subprocess
import argparse
import time

def run_backend_process():
    print("🚀 Starting PRICEGUARD FastAPI Backend on http://localhost:8000 ...")
    return subprocess.Popen([sys.executable, "run_backend.py", "--port", "8000"])

def run_streamlit_process():
    print("🎨 Starting PRICEGUARD Streamlit Dashboard on http://localhost:8501 ...")
    return subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "8501", "--server.headless", "true"])

def main():
    parser = argparse.ArgumentParser(description="PRICEGUARD Unified Service Launcher")
    parser.add_argument("--backend", action="store_true", help="Launch only FastAPI backend")
    parser.add_argument("--dashboard", action="store_true", help="Launch only Streamlit dashboard")
    args = parser.parse_args()

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    processes = []
    try:
        if args.backend:
            p_back = run_backend_process()
            processes.append(p_back)
            p_back.wait()
        elif args.dashboard:
            p_dash = run_streamlit_process()
            processes.append(p_dash)
            p_dash.wait()
        else:
            print("""
    ===================================================================
    🛡️  PRICEGUARD DSS - FULL STACK SERVICE LAUNCHER
    ===================================================================
    📡 FastAPI REST API   : http://localhost:8000 (Swagger: /docs)
    🖥️  Streamlit Console : http://localhost:8501
    ===================================================================
            """)
            p_back = run_backend_process()
            processes.append(p_back)
            time.sleep(2)  # Give backend a moment to initialize
            p_dash = run_streamlit_process()
            processes.append(p_dash)

            # Keep parent process alive
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down PRICEGUARD services...")
        for p in processes:
            p.terminate()
            p.wait()
        print("✅ All services stopped safely.")

if __name__ == "__main__":
    main()
