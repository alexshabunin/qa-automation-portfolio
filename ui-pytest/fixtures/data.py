import random
import string
import time
from typing import Any


_TAGS = ["frontend", "backend", "infra", "bug", "research"]
_STATUSES = ["todo", "in_progress", "done"]


def _ulid_like() -> str:
    # the SPA card lookup expects a 26-char Crockford ULID. We don't need
    # real ULIDs in mocks; we just need something matching the pattern.
    alphabet = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
    return "".join(random.choices(alphabet, k=26))


def _now_iso() -> str:
    t = time.gmtime()
    return time.strftime("%Y-%m-%dT%H:%M:%S.000000Z", t)


def fake_task(**overrides: Any) -> dict:
    title = overrides.pop("title", None) or "Task " + "".join(
        random.choices(string.ascii_letters, k=8)
    )
    task = {
        "id": _ulid_like(),
        "title": title,
        "description": "",
        "status": random.choice(_STATUSES),
        "tags": random.sample(_TAGS, k=random.randint(0, 2)),
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
    }
    task.update(overrides)
    return task


def fake_tasks_list(n: int = 3) -> dict:
    items = [fake_task() for _ in range(n)]
    return {"data": items, "total": n}
