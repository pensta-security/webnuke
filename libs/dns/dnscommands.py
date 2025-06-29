import urllib.parse
from dns import resolver, message, query, flags, exception
from libs.utils import wait_for_enter
import requests
from bs4 import BeautifulSoup
import os
import time
import subprocess
import re


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

                    # gather IPs that aren't Cloudflare owned
                    scan_ips = [ip for ip, owner in ips if "cloudflare" not in owner.lower()]

                    if scan_ips:
                        ip_list_path = os.path.join(history_dir, f"{domain}_{ts}_ips.txt")
                        with open(ip_list_path, "w", encoding="utf-8") as ipf:
                            ipf.write("\n".join(scan_ips))

                        try:
                            proc = subprocess.run(
                                [
                                    "nmap",
                                    "-Pn",
                                    "-iL",
                                    ip_list_path,
                                    "-sT",
                                    "-p",
                                    "443",
                                    "--script",
                                    "ssl-cert",
                                    "--min-parallelism",
                                    "10",
                                ],
                                capture_output=True,
                                text=True,
                                timeout=300,
                            )
                            output = proc.stdout.strip()
                            self.logger.log(output)
                            nmap_fname = f"{domain}_{ts}_nmap.txt"
                            nmap_path = os.path.join(history_dir, nmap_fname)
                            with open(nmap_path, "w", encoding="utf-8") as nf:
                                nf.write(output)
                            self.logger.log(f"Saved nmap output to {nmap_path}")

                            # highlight any nmap lines referencing our domain
                            target_domains = [domain.lower()]
                            if domain.lower().startswith("www."):
                                domain_root = domain[4:].lower()
                                target_domains.append(f"*.{domain_root}")

                            ip_re = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
                            matches = []
                            current_ip = None
                            for line in output.splitlines():
                                ip_match = re.search(ip_re, line)
                                if "nmap scan report for" in line.lower() and ip_match:
                                    current_ip = ip_match.group(0)
                                if any(t in line.lower() for t in target_domains):
                                    ip = ip_match.group(0) if ip_match else current_ip
                                    if ip:
                                        matches.append(f"{ip}: {line.strip()}")
                            if matches:
                                self.logger.log("Highlighted nmap results:")
                                for m in matches:
                                    self.logger.log(f"* {m}")

                                # summarize entries that explicitly contain our domain
                                domain_matches = [m for m in matches if domain.lower() in m.lower()]
                                if domain_matches:
                                    self.logger.log("Nmap domain summary:")
                                    for dm in domain_matches:
                                        self.logger.log(f"* {dm}")
                        except Exception as exc:
                            self.logger.error(f"Error running nmap: {exc}")
                except Exception as exc:
                    self.logger.error(f"Error writing history file: {exc}")
        except Exception as exc:
            self.logger.error(f"Error retrieving DNS history: {exc}")
        wait_for_enter()
