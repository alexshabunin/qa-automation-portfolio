import allure
import pytest

from fixtures.data import fake_task
from fixtures.mocks import mock_tasks_list, mock_update_task


@allure.feature("Task editor")
@allure.story("Edit task")
class TestEditTask:

    @allure.title("Open existing card -> drawer hydrated with current values")
    def test_drawer_hydrates_from_card(self, board):
        existing = fake_task(
            title="Triage flaky e2e",
            status="todo",
            tags=["bug"],
        )
        mock_tasks_list(board.page, {"data": [existing], "total": 1})

        board.open()
        board.wait_until_ready()
        board.task_list.click_card(existing["id"])

        board.drawer.wait_until_open()
        # the title input must carry the existing value
        title_value = board.page.locator(board.drawer.TITLE_INPUT).input_value()
        assert title_value == "Triage flaky e2e"

    @allure.title("Edit tags + status -> PATCH carries diff and card re-renders")
    @pytest.mark.smoke
    def test_edit_tags_and_status(self, board):
        existing = fake_task(
            title="Refactor cart reducer",
            status="todo",
            tags=["frontend"],
        )
        mock_tasks_list(board.page, {"data": [existing], "total": 1})
        updated = {**existing, "status": "in_progress", "tags": ["frontend", "infra"]}
        update_mock = mock_update_task(board.page, existing["id"], updated)

        board.open()
        board.wait_until_ready()
        board.task_list.click_card(existing["id"])
        board.drawer.wait_until_open()

        board.drawer.pick_status("in_progress")
        board.drawer.pick_tags("infra")
        board.drawer.save()
        board.drawer.wait_until_closed()

        assert len(update_mock.requests) == 1
        sent = update_mock.requests[0].body
        assert sent["status"] == "in_progress"
        assert "infra" in sent["tags"]
        # card re-renders with the new status text
        assert "in progress" in board.task_list.card_status(existing["id"]).lower()
