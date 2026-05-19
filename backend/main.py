import os
import re
import time
import uuid
from datetime import datetime, timezone
from typing import Optional

import jwt
from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field, field_validator


JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ALGO = "HS256"
JWT_TTL_SEC = int(os.getenv("JWT_TTL_SEC", "3600"))

DEMO_USER = {
    "email": os.getenv("DEMO_USER_EMAIL", "test@taskflow.io"),
    "password": os.getenv("DEMO_USER_PASSWORD", "Test123!"),
}

ALLOWED_TAGS = {"frontend", "backend", "infra", "bug", "research"}
ALLOWED_STATUSES = {"todo", "in_progress", "done"}
TITLE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 _\-]{2,118}[A-Za-z0-9]$")

app = FastAPI(title="TaskFlow API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

bearer = HTTPBearer(auto_error=False)

# in-memory store; resets on restart
_TASKS: dict[str, dict] = {}


# ---------- models ----------

class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int


class TaskIn(BaseModel):
    title: str
    description: str = ""
    status: str = "todo"
    tags: list[str] = Field(default_factory=list)

    @field_validator("title")
    @classmethod
    def _title(cls, v: str) -> str:
        v = v.strip()
        if not TITLE_RE.match(v):
            raise ValueError("invalid title")
        return v

    @field_validator("status")
    @classmethod
    def _status(cls, v: str) -> str:
        if v not in ALLOWED_STATUSES:
            raise ValueError("invalid status")
        return v

    @field_validator("tags")
    @classmethod
    def _tags(cls, v: list[str]) -> list[str]:
        bad = [t for t in v if t not in ALLOWED_TAGS]
        if bad:
            raise ValueError(f"unknown tags: {bad}")
        return sorted(set(v))


class TaskPatch(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[list[str]] = None


class TaskOut(BaseModel):
    id: str
    title: str
    description: str
    status: str
    tags: list[str]
    created_at: str
    updated_at: str


class TasksListResponse(BaseModel):
    data: list[TaskOut]
    total: int


# ---------- auth ----------

def _make_token(email: str) -> str:
    now = int(time.time())
    payload = {"sub": email, "iat": now, "exp": now + JWT_TTL_SEC}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


def require_user(creds: HTTPAuthorizationCredentials = Depends(bearer)) -> str:
    if creds is None or creds.scheme.lower() != "bearer":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "missing bearer token")
    try:
        payload = jwt.decode(creds.credentials, JWT_SECRET, algorithms=[JWT_ALGO])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid token")
    return payload["sub"]


# ---------- routes ----------

@app.get("/v1/health")
def health():
    return {"status": "ok"}


@app.post("/v1/auth/login", response_model=LoginResponse)
def login(body: LoginRequest):
    if body.email != DEMO_USER["email"] or body.password != DEMO_USER["password"]:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "bad credentials")
    return LoginResponse(access_token=_make_token(body.email), expires_in=JWT_TTL_SEC)


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


@app.get("/v1/tasks", response_model=TasksListResponse)
def list_tasks(
    _user: str = Depends(require_user),
    q: Optional[str] = Query(None),
    status_eq: Optional[str] = Query(None, alias="status"),
    tag: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    items = list(_TASKS.values())
    if q:
        ql = q.lower()
        items = [t for t in items if ql in t["title"].lower()]
    if status_eq:
        if status_eq not in ALLOWED_STATUSES:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "invalid status filter")
        items = [t for t in items if t["status"] == status_eq]
    if tag:
        items = [t for t in items if tag in t["tags"]]
    items.sort(key=lambda t: t["created_at"], reverse=True)
    return {"data": items[offset : offset + limit], "total": len(items)}


@app.post("/v1/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(body: TaskIn, _user: str = Depends(require_user)):
    now = _now_iso()
    task = {
        "id": uuid.uuid4().hex,
        "title": body.title,
        "description": body.description,
        "status": body.status,
        "tags": body.tags,
        "created_at": now,
        "updated_at": now,
    }
    _TASKS[task["id"]] = task
    return task


@app.get("/v1/tasks/{task_id}", response_model=TaskOut)
def get_task(task_id: str, _user: str = Depends(require_user)):
    if task_id not in _TASKS:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "task not found")
    return _TASKS[task_id]


@app.patch("/v1/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: str, body: TaskPatch, _user: str = Depends(require_user)):
    if task_id not in _TASKS:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "task not found")
    task = _TASKS[task_id]
    if body.title is not None:
        title = body.title.strip()
        if not TITLE_RE.match(title):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "invalid title")
        task["title"] = title
    if body.description is not None:
        task["description"] = body.description
    if body.status is not None:
        if body.status not in ALLOWED_STATUSES:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "invalid status")
        task["status"] = body.status
    if body.tags is not None:
        bad = [t for t in body.tags if t not in ALLOWED_TAGS]
        if bad:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"unknown tags: {bad}")
        task["tags"] = sorted(set(body.tags))
    task["updated_at"] = _now_iso()
    return task


@app.delete("/v1/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str, _user: str = Depends(require_user)):
    if task_id not in _TASKS:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "task not found")
    del _TASKS[task_id]


@app.delete("/v1/tasks", status_code=status.HTTP_204_NO_CONTENT)
def clear_tasks(_user: str = Depends(require_user)):
    # test-only helper. real backends wouldn't expose this.
    _TASKS.clear()
