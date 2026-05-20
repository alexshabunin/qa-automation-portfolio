from playwright.sync_api import Page


class TaskList:
    ROOT = '[data-test="task-list"]'

    def __init__(self, page: Page):
        self.page = page

    def card_by_id(self, task_id: str):
        return self.page.locator(f'[data-test="task-{task_id}"]')

    def wait_for_card(self, task_id: str):
        self.card_by_id(task_id).wait_for(state="visible")

    def card_title(self, task_id: str) -> str:
        return (
            self.card_by_id(task_id)
            .locator('[data-test="task-title"]')
            .inner_text()
            .strip()
        )

    def card_status(self, task_id: str) -> str:
        return (
            self.card_by_id(task_id)
            .locator('[data-test="task-status"]')
            .inner_text()
            .strip()
        )

    def card_tag_texts(self, task_id: str) -> list[str]:
        nodes = self.card_by_id(task_id).locator('[data-test^="task-tag-"]')
        return sorted([t.strip() for t in nodes.all_inner_texts()])

    def visible_task_ids(self) -> list[str]:
        attrs = self.page.locator(f'{self.ROOT} [data-test^="task-"]').evaluate_all(
            "nodes => nodes.map(n => n.getAttribute('data-test'))"
        )
        out = []
        for v in attrs or []:
            if v and v.startswith("task-") and len(v) > len("task-"):
                tid = v[len("task-") :]
                if "-" not in tid:  # filter out task-title etc inside cards
                    out.append(tid)
        return out

    def click_card(self, task_id: str):
        self.card_by_id(task_id).click()
