from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Auto-detect and switch to .venv python if running under global python
venv_python = ROOT / ".venv" / ("Scripts" if os.name == "nt" else "bin") / ("python.exe" if os.name == "nt" else "python")
if venv_python.is_file() and os.path.abspath(sys.executable).lower() != str(venv_python.resolve()).lower():
    subprocess.run([str(venv_python), __file__] + sys.argv[1:])
    sys.exit(0)

PYTHON = str(venv_python) if venv_python.is_file() else sys.executable


def wait_for_service(url: str, name: str, timeout_seconds: float = 12.0) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ProcurementLocalRunner"})
            with urllib.request.urlopen(req, timeout=0.8) as response:
                if response.status == 200:
                    print(f"[ OK ] {name} is ready at {url}")
                    return
        except (urllib.error.URLError, TimeoutError, OSError):
            pass
        time.sleep(0.3)
    print(f"[WARN] {name} did not respond within {timeout_seconds}s at {url}")


def main() -> None:
    signal.signal(signal.SIGTERM, lambda s, f: sys.exit(0))
    procs: list[subprocess.Popen] = []

    print("==================================================")
    print(" AI Procurement Request Copilot")
    print(" One-Command Local Development Stack")
    print("==================================================")

    try:
        print("\n[1/3] Starting Mock Vendor-Risk API (port 8001)...")
        api_proc = subprocess.Popen(
            [PYTHON, "-m", "uvicorn", "mock_api.app:app", "--host", "127.0.0.1", "--port", "8001", "--log-level", "warning"],
            cwd=ROOT,
        )
        procs.append(api_proc)
        wait_for_service("http://127.0.0.1:8001/health", "Mock API")

        print("\n[2/3] Starting Backend Server (port 8000)...")
        server_proc = subprocess.Popen(
            [PYTHON, "-m", "uvicorn", "src.server:server_app", "--host", "127.0.0.1", "--port", "8000", "--log-level", "info"],
            cwd=ROOT,
        )
        procs.append(server_proc)
        wait_for_service("http://127.0.0.1:8000/api/health", "Backend API")

        frontend_dir = ROOT / "frontend"
        if frontend_dir.is_dir():
            print("\n[3/3] Starting React Dashboard (port 5173)...")
            npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
            vite_proc = subprocess.Popen(
                [npm_cmd, "run", "dev"],
                cwd=frontend_dir,
            )
            procs.append(vite_proc)
            print("\n>> React Dashboard: http://127.0.0.1:5173")
            print(">> Backend API:     http://127.0.0.1:8000")
            print(">> Mock Vendor API: http://127.0.0.1:8001")
            print("\nPress Ctrl+C to stop all services.\n")

        while True:
            time.sleep(1)
            for p in procs:
                if p.poll() is not None:
                    print(f"Process {p.pid} exited with code {p.returncode}")
                    return
    except KeyboardInterrupt:
        print("\nShutting down services...")
    finally:
        for p in procs:
            if p.poll() is None:
                p.terminate()
        for p in procs:
            try:
                p.wait(timeout=3)
            except subprocess.TimeoutExpired:
                p.kill()
        print("All services stopped.")


if __name__ == "__main__":
    main()
