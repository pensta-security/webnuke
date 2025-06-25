from urllib.parse import urlparse
import tldextract


def get_root_domain(url: str) -> str | None:
    """Return the registrable domain for a URL."""
    parsed = urlparse(url)
    if not parsed.hostname:
        return None
    ext = tldextract.extract(parsed.hostname)
    return ext.registered_domain or parsed.hostname

