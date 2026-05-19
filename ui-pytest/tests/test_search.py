import allure
import pytest

from fixtures.data import fake_task
from fixtures.mocks import mock_tasks_list


@allure.feature("Search")
@allure.story("Debounced search")
class TestSearch:

    @allure.title("Search debounce — five keystrokes coalesce into one backend call")
    @pytest.mark.smoke
    def test_debounce_collapses_keystrokes(self, board):
        matching = fake_task(title="Alpha launch retrospective")
        mock = mock_tasks_list(board.page, {"data": [matching], "total": 1})

        board.open()
        board.wait_until_ready()
        # boot fires one GET. clear so we only count search refetches.
        mock.requests.clear()

        board.search("alpha", delay_ms=30)
        board.task_list.wait_for_card(matching["id"])

        assert len(mock.requests) == 1, (
            f"debounce should coalesce 5 keystrokes into 1 GET, "
            f"got {len(mock.requests)}: {[r.url for r in mock.requests]}"
        )
        assert mock.requests[0].query == {"q": "alpha"}

    @allure.title("Empty result set shows the empty state copy")
    def test_empty_state(self, board):
        mock_tasks_list(board.page, {"data": [], "total": 0})
        board.open()
        board.wait_until_ready()
        # search something that won't match the (empty) list
        board.search("nothing", delay_ms=20)
        # the empty state should be the visible card-area content
        assert board.is_empty_state_shown()
