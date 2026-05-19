import allure
import pytest

from fixtures.data import fake_task
from fixtures.mocks import mock_create_task, mock_tasks_list


@allure.feature("Board")
@allure.story("Create task")
class TestCreateTask:

    @allure.title("Create task through the drawer — sends correct payload and shows toast")
    @pytest.mark.smoke
    def test_create_through_drawer(self, board):
        mock_tasks_list(board.page, {"data": [], "total": 0})
        new_task = fake_task(title="Write release notes", status="todo", tags=["bug"])
        create_mock = mock_create_task(board.page, new_task)

        board.open()
        board.wait_until_ready()
        board.click_create()

        board.drawer.fill_title("Write release notes")
        board.drawer.fill_description("draft for 0.4")
        board.drawer.pick_status("todo")
        board.drawer.pick_tags("bug")
        board.drawer.save()
        board.drawer.wait_until_closed()

        assert len(create_mock.requests) == 1, "drawer should POST exactly once"
        sent = create_mock.requests[0].body
        assert sent["title"] == "Write release notes"
        assert sent["status"] == "todo"
        assert sent["tags"] == ["bug"]
        assert board.get_toast_text() == "Task created"

    @allure.title("Cancelling the drawer does not POST anything")
    def test_cancel_does_not_post(self, board):
        mock_tasks_list(board.page, {"data": [], "total": 0})
        create_mock = mock_create_task(board.page, fake_task())

        board.open()
        board.wait_until_ready()
        board.click_create()
        board.drawer.fill_title("Almost there")
        board.drawer.cancel()
        board.drawer.wait_until_closed()

        assert create_mock.requests == []

    @allure.title("Created card appears in the list with the right status")
    def test_created_card_renders(self, board):
        mock_tasks_list(board.page, {"data": [], "total": 0})
        new_task = fake_task(
            title="Polish docs", status="in_progress", tags=["frontend"]
        )
        mock_create_task(board.page, new_task)

        board.open()
        board.wait_until_ready()
        board.click_create()
        board.drawer.fill_title("Polish docs")
        board.drawer.pick_status("in_progress")
        board.drawer.pick_tags("frontend")
        board.drawer.save()
        board.drawer.wait_until_closed()

        board.task_list.wait_for_card(new_task["id"])
        assert board.task_list.card_title(new_task["id"]) == "Polish docs"
        assert "in progress" in board.task_list.card_status(new_task["id"]).lower()
