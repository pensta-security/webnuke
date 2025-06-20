from selenium.webdriver.common.by import By
from libs.utils.logger import FileLogger

class WebSocketUtil:
    def __init__(self, webdriver, logger=None):
        self.webdriver = webdriver
        self.logger = logger or FileLogger()

    def has_websocket(self) -> bool:
        try:
            scripts = self.webdriver.find_elements(By.XPATH, "//script")
            for tag in scripts:
                src = tag.get_attribute("src") or ""
                content = tag.get_attribute("innerHTML") or ""
                combined = src + " " + content
                if "ws://" in combined.lower() or "wss://" in combined.lower():
                    return True
        except Exception as e:
            self.logger.error(f"Error scanning script tags for WebSocket: {e}")
        try:
            urls = self.webdriver.execute_script(
                "return (window.performance && window.performance.getEntries) ? "
                "window.performance.getEntries().map(e => e.name) : []"
            )
            for url in urls or []:
                if isinstance(url, str) and ("ws://" in url.lower() or "wss://" in url.lower()):
                    return True
        except Exception as e:
            self.logger.error(f"Error retrieving performance entries: {e}")
        return False
