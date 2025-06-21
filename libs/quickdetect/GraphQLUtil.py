from selenium.webdriver.common.by import By
from urllib.parse import urljoin
import requests
from libs.utils.logger import FileLogger

class GraphQLUtil:
    """Utility class to detect GraphQL usage on a webpage."""

    def __init__(self, webdriver, logger=None):
        self.webdriver = webdriver
        self.logger = logger or FileLogger()

    def has_graphql(self) -> bool:
        """Return True if a GraphQL endpoint is referenced in the DOM or network."""
        try:
            scripts = self.webdriver.find_elements(By.XPATH, "//script")
            for tag in scripts:
                src = tag.get_attribute("src") or ""
                if "/graphql" in src.lower():
                    return True
                content = tag.get_attribute("innerHTML") or ""
                if "/graphql" in content.lower():
                    return True
        except Exception as e:
            self.logger.error(f"Error scanning script tags for GraphQL: {e}")
        try:
            urls = self.webdriver.execute_script(
                "return (window.performance && window.performance.getEntries) ? "
                "window.performance.getEntries().map(e => e.name) : []"
            )
            for url in urls or []:
                if "/graphql" in str(url).lower():
                    return True
        except Exception as e:
            self.logger.error(f"Error retrieving performance entries: {e}")
        return False

    def allows_introspection(self) -> bool:
        """Return True if an introspection query succeeds on a detected endpoint."""
        endpoints = set()
        try:
            urls = self.webdriver.execute_script(
                "return (window.performance && window.performance.getEntries) ?"
                "window.performance.getEntries().map(e => e.name) : []"
            )
            for url in urls or []:
                if "/graphql" in str(url).lower():
                    endpoints.add(str(url))
        except Exception as e:
            self.logger.error(f"Error retrieving performance entries: {e}")

        if not endpoints:
            return False

        query = {
            "query": "query IntrospectionQuery { __schema { queryType { name } } }"
        }
        base = getattr(self.webdriver, "current_url", "")
        for endpoint in endpoints:
            try:
                full_url = urljoin(base, endpoint)
                resp = requests.post(full_url, json=query, timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    if isinstance(data, dict) and data.get("data") and not data.get("errors"):
                        return True
            except Exception as e:
                self.logger.error(f"Error querying GraphQL endpoint {endpoint}: {e}")
        return False
