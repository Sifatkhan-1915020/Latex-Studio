import sys
import os
import webbrowser
import threading
import time
from pathlib import Path

# Add current directory to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from app.database import init_db
from app.config import ensure_tectonic_installed

def open_browser():
    time.sleep(1.2)
    print("\n" + "="*60)
    print("🚀 Overleaf LaTeX Studio is running at: http://127.0.0.1:8000")
    print("="*60 + "\n")
    try:
        webbrowser.open("http://127.0.0.1:8000")
    except Exception:
        pass

def main():
    print("\n--- Initializing Overleaf LaTeX Studio ---")
    
    # 1. Initialize SQLite Database
    print("✓ Initializing local database...")
    init_db()

    # 2. Check and ensure LaTeX Compiler
    compiler_path = ensure_tectonic_installed()
    print(f"✓ Standalone LaTeX compiler ready at: {compiler_path}")


    # 3. Launch browser in a background thread
    threading.Thread(target=open_browser, daemon=True).start()

    # 4. Start Uvicorn Server
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()
