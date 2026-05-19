from typing import Iterable, Optional

import requests

from custom_requester import CustomRequester


class TasksAPI(CustomRequester):
    BASE = "/v1/tasks"

    def get_list(
        self,
        *,
        q: Optional[str] = None,
        status: Optional[str] = None,
        tag: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        expected_status: Optional[int | Iterable[int]] = 200,
    ) -> requests.Response:
        params: dict = {}
        if q is not None:
            params["q"] = q
        if status is not None:
            params["status"] = status
        if tag is not None:
            params["tag"] = tag
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        return self.send_request(
            "GET",
            self.BASE,
            params=params or None,
            expected_status=expected_status,
        )

    def create(
        self,
        *,
        title: str,
        description: str = "",
        status: str = "todo",
        tags: Optional[list[str]] = None,
        expected_status: Optional[int | Iterable[int]] = 201,
    ) -> requests.Response:
        return self.send_request(
            "POST",
            self.BASE,
            json_body={
                "title": title,
                "description": description,
                "status": status,
                "tags": tags or [],
            },
            expected_status=expected_status,
        )

    def get(
        self,
        task_id: str,
        *,
        expected_status: Optional[int | Iterable[int]] = 200,
    ) -> requests.Response:
        return self.send_request(
            "GET",
            f"{self.BASE}/{task_id}",
            expected_status=expected_status,
        )

    def patch(
        self,
        task_id: str,
        *,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        tags: Optional[list[str]] = None,
        expected_status: Optional[int | Iterable[int]] = 200,
    ) -> requests.Response:
        body: dict = {}
        if title is not None:
            body["title"] = title
        if description is not None:
            body["description"] = description
        if status is not None:
            body["status"] = status
        if tags is not None:
            body["tags"] = tags
        return self.send_request(
            "PATCH",
            f"{self.BASE}/{task_id}",
            json_body=body,
            expected_status=expected_status,
        )

    def delete(
        self,
        task_id: str,
        *,
        expected_status: Optional[int | Iterable[int]] = 204,
    ) -> requests.Response:
        return self.send_request(
            "DELETE",
            f"{self.BASE}/{task_id}",
            expected_status=expected_status,
        )

    def clear(
        self,
        *,
        expected_status: Optional[int | Iterable[int]] = 204,
    ) -> requests.Response:
        # test-only nuke. backend exposes DELETE /v1/tasks for fixture cleanup.
        return self.send_request(
            "DELETE",
            self.BASE,
            expected_status=expected_status,
        )
