import allure
import pytest

from fixtures.mocks import mock_create_task, mock_tasks_list
from fixtures.data import fake_task


@allure.feature("Board")
@allure.story("Validation")
class TestDrawerValidation:

    @pytest.mark.negative
    @pytest.mark.parametrize(
        "title,expected_error",
        [
            ("", "Title is required."),
            ("   ", "Title is required."),
            ("ab", "Title must be at least 3 characters."),
            ("ab@cd", "Title has invalid characters."),
        ],
    )
    @allure.title("Drawer rejects invalid title: '{title}'")
    def test_invalid_titles_are_rejected_client_side(
        self, board, title, expected_error
    ):
        mock_tasks_list(board.page, {"data": [], "total": 0})
        # mock POST anyway — if validation leaks, the test catches the extra call
        create_mock = mock_create_task(board.page, fake_task())

        board.open()
        board.wait_until_ready()
        board.click_create()
        board.drawer.fill_title(title)
        board.drawer.save()

        assert board.drawer.title_error_text() == expected_error
        assert create_mock.requests == [], "form must not POST on a client-side reject"
