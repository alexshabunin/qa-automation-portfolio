import requests

from apis import AuthAPI, TasksAPI


class ApiManager:
    # Facade. One object hands out per-domain API clients sharing one Session.

    def __init__(self, session: requests.Session, base_url: str):
        self.session = session
        self.base_url = base_url
        self.auth = AuthAPI(session, base_url)
        self.tasks = TasksAPI(session, base_url)
