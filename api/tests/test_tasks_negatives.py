import allure
import pytest


@allure.feature("Tasks")
@allure.story("Validation")
@pytest.mark.usefixtures("clean_tasks")
class TestTasksValidation:

    @allure.title("POST with bad title -> 422")
    @pytest.mark.parametrize(
        "title,why",
        [
            ("", "empty"),
            ("  ", "whitespace only"),
            ("xy", "too short"),
            ("a" * 200, "too long"),
            ("!!", "invalid chars"),
        ],
    )
    @pytest.mark.negative
    def test_title_rejected(self, api_manager, title, why):
        api_manager.tasks.create(title=title, expected_status=422)

    @allure.title("POST with unknown status -> 422")
    @pytest.mark.negative
    def test_unknown_status(self, api_manager):
        api_manager.tasks.create(
            title="Valid title",
            status="archived",
            expected_status=422,
        )

    @allure.title("POST with unknown tag -> 422")
    @pytest.mark.negative
    def test_unknown_tag(self, api_manager):
        api_manager.tasks.create(
            title="Valid title",
            tags=["frontend", "android"],
            expected_status=422,
        )

    @allure.title("PATCH with unknown status -> 400")
    @pytest.mark.negative
    def test_patch_bad_status(self, api_manager):
        created = api_manager.tasks.create(title="Patch target").json()
        api_manager.tasks.patch(
            created["id"],
            status="archived",
            expected_status=400,
        )

    @allure.title("GET tasks?status=archived -> 400")
    @pytest.mark.negative
    def test_list_bad_status_filter(self, api_manager):
        api_manager.tasks.get_list(status="archived", expected_status=400)
