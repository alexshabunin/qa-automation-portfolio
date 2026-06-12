import allure
import vedro
from vedro_playwright import opened_browser_page

from contexts import opened_board_page, opened_create_task_drawer
from dicts import Feature, Priority, Story, Translations, allure_labels
from interfaces.web.pages.board import BoardPage
from mocks import mocked_create_task


@allure_labels(Feature.TaskEditor, Story.Validation, Priority.Normal)
class Scenario(vedro.Scenario):
    # Three invalid-title cases, each pinned to its own AllureID so the
    # parametrized rows stay traceable on the report side.
    subject = "Drawer rejects invalid title input ({input_label})"

    @vedro.params("empty",         "",       Translations.TitleRequired,      "B-401")
    @vedro.params("whitespace",    "   ",    Translations.TitleRequired,      "B-402")
    @vedro.params("too short",     "ab",     Translations.TitleTooShort,      "B-403")
    @vedro.params("invalid chars", "ab@cd",  Translations.TitleInvalidChars,  "B-404")
    def __init__(
        self,
        input_label: str,
        typed_title: str,
        expected_error: str,
        allure_id: str,
    ):
        self.input_label = input_label
        self.typed_title = typed_title
        self.expected_error = expected_error
        self.allure_id = allure_id

    async def given_browser_page(self):
        self.page = await opened_browser_page()
        allure.dynamic.id(self.allure_id)

    async def given_opened_board_page(self):
        self.board: BoardPage = await opened_board_page(
            self.page,
            initial_tasks={"data": [], "total": 0},
        )

    async def given_opened_create_task_drawer(self):
        await opened_create_task_drawer(self.board)

    async def when_submit_invalid_title(self):
        drawer = self.board.task_drawer
        await drawer.title_input.fill(self.typed_title)
        # A strict mock with `wait_for_requests=0` doubles as an assertion:
        # the network is silent. If the form posted anyway, exiting the
        # context raises and the scenario fails loudly.
        async with mocked_create_task(
            self.page, response_body={}, wait_for_requests=0
        ):
            await drawer.save_button.click()
            await drawer.title_error.wait_for()

    async def then_inline_error_matches_translation(self):
        assert await self.board.task_drawer.title_error.text() == self.expected_error

    async def and_drawer_is_still_open(self):
        assert await self.board.task_drawer.save_button.is_visible(), (
            "Drawer dismissed itself on a validation error — should stay open."
        )
