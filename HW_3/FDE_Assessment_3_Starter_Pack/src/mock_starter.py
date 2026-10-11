from __future__ import annotations

import threading
import time

import requests
import uvicorn

from mock_api.app import app

_SERVER_STARTED = False
_LOCK = threading.Lock()


def ensure_mock_api_running() -> None:
    global _SERVER_STARTED
    if _is_healthy():
        return
    with _LOCK:
        if _is_healthy():
            return
        thread = threading.Thread(
            target=uvicorn.run,
            args=(app,),
            kwargs={"host": "127.0.0.1", "port": 8001, "log_level": "warning"},
            daemon=True,
        )
        thread.start()
        for _ in range(20):
            time.sleep(0.15)
            if _is_healthy():
                _SERVER_STARTED = True
                return


def _is_healthy() -> bool:
    try:
        resp = requests.get("http://127.0.0.1:8001/health", timeout=0.2)
        return resp.status_code == 200
    except requests.RequestException:
        return False
