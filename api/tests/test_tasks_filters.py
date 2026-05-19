import allure
import pytest


@allure.feature("Tasks")
@allure.story("Filters & pagination")
@pytest.mark.usefixtures("clean_tasks")
class TestTasksFilters:

    def _seed(self, api):
        api.tasks.create(title="Alpha launch retrospective", tags=["frontend"])
        api.tasks.create(title="Beta plan", status="in_progress", tags=["backend"])
        api.tasks.create(title="Gamma release", status="done", tags=["infra", "bug"])
        api.tasks.create(title="Alpha follow up", tags=["bug"])

    @allure.title("Empty store returns total=0")
    def test_empty(self, api_manager):
        body = api_manager.tasks.get_list().json()
        assert body == {"data": [], "total": 0}

    @allure.title("q= filters title substring (case insensitive)")
    def test_q_filter(self, api_manager):
        self._seed(api_manager)
        body = api_manager.tasks.get_list(q="alpha").json()
        titles = {t["title"] for t in body["data"]}
        assert titles == {"Alpha launch retrospective", "Alpha follow up"}
        assert body["total"] == 2

    @allure.title("status= filters by status")
    def test_status_filter(self, api_manager):
        self._seed(api_manager)
        body = api_manager.tasks.get_list(status="in_progress").json()
        assert [t["title"] for t in body["data"]] == ["Beta plan"]

    @allure.title("tag= filters by tag membership")
    def test_tag_filter(self, api_manager):
        self._seed(api_manager)
        body = api_manager.tasks.get_list(tag="bug").json()
        titles = {t["title"] for t in body["data"]}
        assert titles == {"Gamma release", "Alpha follow up"}

    @allure.title("limit/offset paginates while total stays constant")
    def test_pagination(self, api_manager):
        self._seed(api_manager)
        page1 = api_manager.tasks.get_list(limit=2, offset=0).json()
        page2 = api_manager.tasks.get_list(limit=2, offset=2).json()
        assert page1["total"] == 4
        assert page2["total"] == 4
        assert len(page1["data"]) == 2
        assert len(page2["data"]) == 2
        ids1 = {t["id"] for t in page1["data"]}
        ids2 = {t["id"] for t in page2["data"]}
        assert ids1.isdisjoint(ids2)
