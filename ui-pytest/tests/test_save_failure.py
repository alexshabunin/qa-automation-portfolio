import allure
import pytest

from fixtures.mocks import mock_create_task_failure, mock_tasks_list


@allure.feature("Task editor")
@allure.story("Save errors")
class TestSaveFailure:

    @allure.title("Backend 500 on save — drawer stays open, user input preserved")
    @pytest.mark.negative
    def test_500_keeps_drawer_open(self, board):
        mock_tasks_list(board.page, {"data": [], "total": 0})
        mock_create_task_failure(board.page, status=500, message="Database is down")

        board.open()
        board.wait_until_ready()
        board.click_create()
        board.drawer.fill_title("Important item I do not want to retype")
        board.drawer.fill_description("This text must survive a save failure.")
        board.drawer.save()

        # drawer must stay visible
        assert board.drawer.root().is_visible(), "drawer closed on failed save"
        # server message surfaced
        msg = board.drawer.drawer_error_text()
        assert "down" in msg.lower() or "error" in msg.lower()
        # title preserved
        title_value = board.page.locator(board.drawer.TITLE_INPUT).input_value()
        assert title_value == "Important item I do not want to retype"
