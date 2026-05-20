from playwright.sync_api import Page


class BasePage:
    URL_PATH = ""

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")

    def open(self) -> None:
        url = f"{self.base_url}/{self.URL_PATH.lstrip('/')}" if self.URL_PATH else self.base_url
        self.page.goto(url, wait_until="domcontentloaded")

    # generic helpers that all pages share
    def get_toast_text(self) -> str:
        toast = self.page.locator('[data-test="toast"]')
        toast.wait_for(state="visible")
        return toast.inner_text().strip()
