import json
import re
from dataclasses import dataclass, field
from typing import Any, Optional
from urllib.parse import parse_qsl, urlsplit

from playwright.sync_api import Page, Route


@dataclass
class RecordedRequest:
    method: str
    url: str
    query: dict[str, str]
    body: Any


@dataclass
class MockHandle:
    requests: list[RecordedRequest] = field(default_factory=list)


def _record(route: Route, store: list[RecordedRequest]):
    req = route.request
    parts = urlsplit(req.url)
    try:
        body = req.post_data_json
    except Exception:
        body = req.post_data
    store.append(
        RecordedRequest(
            method=req.method,
            url=req.url,
            query=dict(parse_qsl(parts.query, keep_blank_values=True)),
            body=body,
        )
    )


def mock_tasks_list(page: Page, response_body: dict) -> MockHandle:
    # GET /api/tasks — keep alive for the whole test (search refetches reuse it)
    handle = MockHandle()

    def handler(route: Route):
        if route.request.method != "GET" or "/api/tasks" not in route.request.url:
            route.fallback()
            return
        # /api/tasks/{id} is a different endpoint — let it pass through
        path = urlsplit(route.request.url).path
        if re.match(r".*/api/tasks/[^/]+$", path):
            route.fallback()
            return
        _record(route, handle.requests)
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(response_body, default=str),
        )

    page.route("**/*", handler)
    return handle


def mock_create_task(page: Page, response_body: dict, status: int = 201) -> MockHandle:
    handle = MockHandle()

    def handler(route: Route):
        if route.request.method != "POST" or "/api/tasks" not in route.request.url:
            route.fallback()
            return
        _record(route, handle.requests)
        route.fulfill(
            status=status,
            content_type="application/json",
            body=json.dumps(response_body, default=str),
        )

    page.route("**/*", handler)
    return handle


def mock_update_task(
    page: Page, task_id: str, response_body: dict, status: int = 200
) -> MockHandle:
    handle = MockHandle()

    def handler(route: Route):
        if route.request.method not in {"PATCH", "PUT"}:
            route.fallback()
            return
        if f"/api/tasks/{task_id}" not in route.request.url:
            route.fallback()
            return
        _record(route, handle.requests)
        route.fulfill(
            status=status,
            content_type="application/json",
            body=json.dumps(response_body, default=str),
        )

    page.route("**/*", handler)
    return handle


def mock_create_task_failure(page: Page, status: int = 500, message: str = "Server error"):
    handle = MockHandle()

    def handler(route: Route):
        if route.request.method != "POST" or "/api/tasks" not in route.request.url:
            route.fallback()
            return
        _record(route, handle.requests)
        route.fulfill(
            status=status,
            content_type="application/json",
            body=json.dumps({"error": message}),
        )

    page.route("**/*", handler)
    return handle
