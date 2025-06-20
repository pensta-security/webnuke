import json
from typing import Any, Dict, List
from selenium.webdriver.remote.webdriver import WebDriver
from libs.utils.logger import FileLogger


class NetworkLogger:
    """Capture network events using Chrome DevTools Protocol."""

    def __init__(self, driver: WebDriver, logger: FileLogger | None = None):
        self.driver = driver
        self.logger = logger or FileLogger()
        try:
            self.driver.execute_cdp_cmd("Network.enable", {})
        except Exception as e:
            self.logger.error(f"Error enabling network logging: {e}")

    def get_log(self) -> List[Dict[str, Any]]:
        """Return raw network events from performance logs."""
        events: List[Dict[str, Any]] = []
        try:
            entries = self.driver.get_log("performance")
            for entry in entries:
                try:
                    message = json.loads(entry.get("message", "{}")).get("message", {})
                    if message.get("method", "").startswith("Network."):
                        events.append(message)
                except Exception as e:
                    self.logger.error(f"Error parsing log entry: {e}")
        except Exception as e:
            self.logger.error(f"Error retrieving performance logs: {e}")
        return events

    def get_har(self) -> List[Dict[str, Any]]:
        """Simplified HAR-like list with URL and status for each response."""
        har: List[Dict[str, Any]] = []
        for event in self.get_log():
            if event.get("method") == "Network.responseReceived":
                params = event.get("params", {})
                response = params.get("response", {})
                har.append({
                    "url": response.get("url"),
                    "status": response.get("status"),
                })
        return har
