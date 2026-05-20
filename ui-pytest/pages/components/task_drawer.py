from playwright.sync_api import Page


class TaskDrawer:
    ROOT = '[data-test="task-drawer"]'
    TITLE_INPUT = '[data-test="task-title-input"]'
    DESC_INPUT = '[data-test="task-description-input"]'
    STATUS_SELECT = '[data-test="task-status-select"]'
    SAVE_BTN = '[data-test="drawer-save"]'
    CANCEL_BTN = '[data-test="drawer-cancel"]'
    CLOSE_BTN = '[data-test="drawer-close"]'
    TITLE_ERROR = '[data-test="task-title-error"]'
    DRAWER_ERROR = '[data-test="drawer-error"]'

    def __init__(self, page: Page):
        self.page = page

    def root(self):
        return self.page.locator(self.ROOT)

    def wait_until_open(self):
        # the input mounting is the real signal "form is usable"
        self.page.locator(self.TITLE_INPUT).wait_for(state="visible")

    def wait_until_closed(self):
        self.root().wait_for(state="hidden")

    def fill_title(self, value: str):
        box = self.page.locator(self.TITLE_INPUT)
        box.fill(value)

    def fill_description(self, value: str):
        self.page.locator(self.DESC_INPUT).fill(value)

    def pick_status(self, value: str):
        self.page.locator(self.STATUS_SELECT).select_option(value=value)

    def pick_tags(self, *slugs: str):
        for slug in slugs:
            self.page.locator(f'[data-test="tag-chip-{slug}"]').click()

    def save(self):
        self.page.locator(self.SAVE_BTN).click()

    def cancel(self):
        self.page.locator(self.CANCEL_BTN).click()

    def title_error_text(self) -> str:
        loc = self.page.locator(self.TITLE_ERROR)
        loc.wait_for(state="visible")
        return loc.inner_text().strip()

    def drawer_error_text(self) -> str:
        loc = self.page.locator(self.DRAWER_ERROR)
        loc.wait_for(state="visible")
        return loc.inner_text().strip()

    def is_save_disabled(self) -> bool:
        return self.page.locator(self.SAVE_BTN).is_disabled()
