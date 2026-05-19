import json
from typing import Any, Iterable, Optional

import allure
import requests


class CustomRequester:
    # Base class for every API client. Wraps requests.Session, adds:
    #   - base_url so call sites pass paths, not URLs
    #   - allure step + attachments for every request
    #   - expected_status check (raises AssertionError on mismatch)

    DEFAULT_TIMEOUT = 10

    def __init__(self, session: requests.Session, base_url: str):
        self.session = session
        self.base_url = base_url.rstrip("/")

    def send_request(
        self,
        method: str,
        endpoint: str,
        *,
        params: Optional[dict] = None,
        data: Optional[Any] = None,
        json_body: Optional[Any] = None,
        headers: Optional[dict] = None,
        expected_status: Optional[int | Iterable[int]] = None,
        timeout: Optional[float] = None,
    ) -> requests.Response:
        url = f"{self.base_url}{endpoint if endpoint.startswith('/') else '/' + endpoint}"
        step_name = f"{method.upper()} {endpoint}"

        with allure.step(step_name):
            if json_body is not None:
                allure.attach(
                    json.dumps(json_body, ensure_ascii=False, indent=2, default=str),
                    name="request body",
                    attachment_type=allure.attachment_type.JSON,
                )
            if params:
                allure.attach(
                    json.dumps(params, ensure_ascii=False, indent=2),
                    name="query params",
                    attachment_type=allure.attachment_type.JSON,
                )

            response = self.session.request(
                method=method.upper(),
                url=url,
                params=params,
                data=data,
                json=json_body,
                headers=headers,
                timeout=timeout or self.DEFAULT_TIMEOUT,
            )

            # always attach the response body so allure has it on failures
            body_text = response.text
            try:
                pretty = json.dumps(response.json(), ensure_ascii=False, indent=2)
                allure.attach(
                    pretty,
                    name=f"response {response.status_code}",
                    attachment_type=allure.attachment_type.JSON,
                )
            except ValueError:
                allure.attach(
                    body_text,
                    name=f"response {response.status_code}",
                    attachment_type=allure.attachment_type.TEXT,
                )

            if expected_status is not None:
                expected = (
                    {expected_status}
                    if isinstance(expected_status, int)
                    else set(expected_status)
                )
                assert response.status_code in expected, (
                    f"{step_name}: expected status in {sorted(expected)}, "
                    f"got {response.status_code}. body={body_text[:500]}"
                )

            return response
