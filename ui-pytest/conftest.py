import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest
import requests

from pages import BoardPage


REPO_ROOT = Path(__file__).resolve().parent.parent
APP_DIR = REPO_ROOT / "app"


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_http(url: str, timeout: float = 10.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            if requests.get(url, timeout=1).ok:
                return
        except requests.RequestException:
            pass
        time.sleep(0.2)
    raise RuntimeError(f"static server at {url} did not respond in {timeout}s")


@pytest.fixture(scope="session")
def app_server():
    # boot the SPA on a random free port for the whole session
    port = int(os.getenv("APP_PORT") or _free_port())
    proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"],
        cwd=str(APP_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    url = f"http://127.0.0.1:{port}"
    try:
        _wait_http(url + "/", timeout=10)
        yield url
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()


@pytest.fixture(scope="session")
def base_url(app_server):
    return app_server


@pytest.fixture
def board(page, base_url) -> BoardPage:
    return BoardPage(page, base_url)


# pytest-playwright knobs
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 800},
    }
