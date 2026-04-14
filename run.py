"""
Development entry point.
Run with:  python run.py
or:        uvicorn app.main:app --reload --port 8000
"""
import uvicorn
from app.config import get_settings

if __name__ == "__main__":
    s = get_settings()
    uvicorn.run(
        "app.main:app",
        host=s.host,
        port=s.port,
        reload=s.debug,
        log_level="debug" if s.debug else "info",
    )
