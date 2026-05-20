from playwright.sync_api import Page

from .base_page import BasePage
from .components.task_drawer import TaskDrawer
from .components.task_list import TaskList


class BoardPage(BasePage):
    URL_PATH = ""

    # locators
    SEARCH_INPUT = '[data-test="search-input"]'
    CREATE_BUTTON = '[data-test="create-task-button"]'
    COUNTER = '[data-test="task-counter"]'
    EMPTY_STATE = '[data-test="empty-state"]'

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.drawer = TaskDrawer(page)
        self.task_list = TaskList(page)

    def wait_until_ready(self):
        # board is "ready" when the toolbar counter mounts
        self.page.locator(self.COUNTER).wait_for(state="visible")

    def click_create(self):
        self.page.locator(self.CREATE_BUTTON).click()
        self.drawer.wait_until_open()

    def search(self, query: str, delay_ms: int = 30):
        box = self.page.locator(self.SEARCH_INPUT)
        box.click()
        box.fill("")
        # type char-by-char so the SPA's debounce gets exercised
        box.press_sequentially(query, delay=delay_ms)

    def is_empty_state_shown(self) -> bool:
        return self.page.locator(self.EMPTY_STATE).is_visible()

    def counter_value(self) -> int:
        text = self.page.locator(self.COUNTER).inner_text()
        # counter renders as e.g. "Tasks: 3" — pull out the number
        digits = "".join(c for c in text if c.isdigit())
        return int(digits) if digits else 0
