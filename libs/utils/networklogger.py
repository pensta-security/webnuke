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


def load_har_file(path: str, logger: FileLogger | None = None) -> List[Dict[str, Any]]:
    """Load a HAR file returning a simplified list of entries.

    The returned objects match :func:`NetworkLogger.get_har` so other
    modules can consume either network logs or imported HAR data
    transparently.  Supports both simplified lists and full HAR
    structures as exported by common tools.
    """
    logger = logger or FileLogger()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as exc:  # pragma: no cover - file errors rare
        logger.error(f"Error reading HAR file: {exc}")
        return []

    if isinstance(data, dict) and "log" in data:
        entries = data.get("log", {}).get("entries", [])
        har: List[Dict[str, Any]] = []
        for entry in entries:
            request = entry.get("request", {})
            response = entry.get("response", {})
            har.append({
                "url": request.get("url"),
                "status": response.get("status"),
            })
        return har

    if isinstance(data, list):
        return data

    return []
