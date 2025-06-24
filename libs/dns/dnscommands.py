import urllib.parse
from dns import resolver, message, query, flags, exception
from libs.utils import wait_for_enter
import requests
from bs4 import BeautifulSoup
import os
import time
import subprocess


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
        domain = self._get_domain()
        if not domain:
            self.logger.log("No domain specified")
            wait_for_enter()
            return
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(
                f"https://viewdns.info/iphistory/?domain={domain}",
                headers=headers,
                timeout=10,
            )
            if resp.status_code != 200:
                self.logger.error(
                    f"History lookup failed with status {resp.status_code}"
                )
                wait_for_enter()
                return
            soup = BeautifulSoup(resp.text, "html.parser")
            header = soup.find("th", string=lambda x: x and "IP Address" in x)
            if not header:
                self.logger.log("No historic DNS data found")
                wait_for_enter()
                return
            table = header.find_parent("table")
            rows = table.find_all("tr")[1:]
            if not rows:
                self.logger.log("No historic DNS data found")
                wait_for_enter()
                return
            results = []
            ips = []
            for row in rows:
                cells = [c.get_text(strip=True) for c in row.find_all("td")]
                if len(cells) >= 4:
                    ip, _loc, owner, last_seen = cells[:4]
                    line = f"{last_seen}: {ip} - {owner}"
                    self.logger.log(line)
                    results.append(line)
                    ips.append((ip, owner))
            if results:
                history_dir = os.path.join(os.getcwd(), "dns_history")
                os.makedirs(history_dir, exist_ok=True)
                ts = time.strftime("%Y%m%d_%H%M%S")
                fname = f"{domain}_{ts}.txt"
                path = os.path.join(history_dir, fname)
                try:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write("\n".join(results))
                    self.logger.log(f"Saved DNS history to {path}")

                    # run nmap for each IP and save output
                    for ip, owner in ips:
                        if "cloudflare" in owner.lower():
                            self.logger.log(
                                f"Skipping nmap scan for Cloudflare IP {ip}"
                            )
                            continue
                        try:
                            proc = subprocess.run(
                                [
                                    "nmap",
                                    "-sT",
                                    "-p",
                                    "443",
                                    "--script",
                                    "ssl-cert",
                                    ip,
                                ],
                                capture_output=True,
                                text=True,
                                timeout=30,
                            )
                            output = proc.stdout.strip()
                            self.logger.log(output)
                            nmap_fname = f"{domain}_{ip}_{ts}_nmap.txt"
                            nmap_path = os.path.join(history_dir, nmap_fname)
                            with open(nmap_path, "w", encoding="utf-8") as nf:
                                nf.write(output)
                            self.logger.log(
                                f"Saved nmap output for {ip} to {nmap_path}"
                            )
                        except Exception as exc:
                            self.logger.error(
                                f"Error running nmap for {ip}: {exc}"
                            )
                except Exception as exc:
                    self.logger.error(f"Error writing history file: {exc}")
        except Exception as exc:
            self.logger.error(f"Error retrieving DNS history: {exc}")
        wait_for_enter()
