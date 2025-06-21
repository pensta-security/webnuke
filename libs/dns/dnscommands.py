import urllib.parse
from dns import resolver, message, query, flags, exception
from libs.utils import wait_for_enter


class DNSCommands:
    def __init__(self, driver, curses_util, logger, history):
        self.driver = driver
        self.curses_util = curses_util
        self.logger = logger
        self.history = history

    def _get_domain(self):
        url = getattr(self.driver, "current_url", "")
        if not url or url == "":
            response = self.curses_util.get_param("Enter domain").decode("utf-8").strip()
            return response
        return urllib.parse.urlparse(url).hostname

    def _is_dnssec_enabled(self, domain):
        try:
            resolver.resolve(domain, "DNSKEY")
            return True
        except Exception:
            return False

    def _prompt_recursive_check(self):
        ans = self.curses_util.get_param("Verify recursive lookup? (y/n)").decode("utf-8").strip().lower()
        return ans.startswith("y")

    def _check_recursion(self, domain):
        try:
            ns_records = resolver.resolve(domain, "NS")
            for ns in ns_records:
                ns_host = str(ns.target).rstrip(".")
                try:
                    ns_ip = resolver.resolve(ns_host, "A")[0].to_text()
                    q = message.make_query("example.com", "A")
                    q.flags |= flags.RD
                    resp = query.udp(q, ns_ip, timeout=5)
                    ra = bool(resp.flags & flags.RA)
                    self.logger.log(f"{ns_host} recursion enabled: {'yes' if ra else 'no'}")
                except Exception as exc:
                    self.logger.error(f"Error checking recursion for {ns_host}: {exc}")
        except Exception as exc:
            self.logger.error(f"Error retrieving NS records: {exc}")

    def show_dns_info(self):
        domain = self._get_domain()
        if not domain:
            self.logger.log("No domain specified")
            wait_for_enter()
            return
        types = ["A", "AAAA", "MX", "NS", "CNAME", "TXT"]
        for rtype in types:
            try:
                answers = resolver.resolve(domain, rtype)
                for ans in answers:
                    self.logger.log(f"{rtype}: {ans.to_text()}")
            except (resolver.NoAnswer, resolver.NXDOMAIN, resolver.NoNameservers, exception.Timeout):
                pass
            except Exception as exc:
                self.logger.error(f"{rtype} lookup failed: {exc}")
        dnssec = self._is_dnssec_enabled(domain)
        self.logger.log(f"DNSSEC enabled: {'yes' if dnssec else 'no'}")
        if self._prompt_recursive_check():
            self._check_recursion(domain)
        wait_for_enter()

    def show_history(self):
        seen = set()
        for url in self.history:
            host = urllib.parse.urlparse(url).hostname
            if host and host not in seen:
                self.logger.log(host)
                seen.add(host)
        if not seen:
            self.logger.log("No domain history.")
        wait_for_enter()
