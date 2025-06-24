import os
import tempfile
import unittest
import subprocess
from unittest.mock import patch

from libs.dns.dnscommands import DNSCommands


class DummyDriver:
    current_url = ""


class DummyCurses:
    def get_param(self, _):
        return b"example.com"


class RecordLogger:
    def __init__(self):
        self.records = []

    def log(self, text):
        self.records.append(text)

    error = log
    debug = log


class DNSHistoryTests(unittest.TestCase):
    @patch("libs.dns.dnscommands.wait_for_enter")
    @patch("libs.dns.dnscommands.subprocess.run")
    @patch("libs.dns.dnscommands.requests.get")
    @patch("libs.dns.dnscommands.time.strftime", return_value="20240101_120000")
    def test_history_written_to_file(self, mock_ts, mock_get, mock_run, _mock_wait):
        html = """
            <table>
            <tr><th>IP Address</th><th>Location</th><th>Owner</th><th>Last Seen</th></tr>
            <tr><td>1.1.1.1</td><td>US</td><td>Cloudflare, Inc</td><td>2024-01-01</td></tr>
            <tr><td>2.2.2.2</td><td>US</td><td>OtherCorp</td><td>2024-01-02</td></tr>
            </table>
        """

        class Resp:
            status_code = 200
            text = html

        mock_get.return_value = Resp()
        mock_run.return_value = subprocess.CompletedProcess(
            ["nmap"], 0, stdout="nmap output"
        )

        logger = RecordLogger()
        cmds = DNSCommands(DummyDriver(), DummyCurses(), logger, [])

        with tempfile.TemporaryDirectory() as tmpdir:
            cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                cmds.show_history()
                files = os.listdir("dns_history")
                self.assertEqual(len(files), 3)
                hist_file = [f for f in files if f.endswith(".txt") and not f.endswith("_nmap.txt") and not f.endswith("_ips.txt")][0]
                nmap_file = [f for f in files if f.endswith("_nmap.txt")][0]
                ip_list_file = [f for f in files if f.endswith("_ips.txt")][0]
                path = os.path.join("dns_history", hist_file)
                with open(path, "r", encoding="utf-8") as f:
                    data = f.read()
                self.assertIn("2024-01-01: 1.1.1.1 - Cloudflare, Inc", data)
                self.assertIn("2024-01-02: 2.2.2.2 - OtherCorp", data)
                nmap_path = os.path.join("dns_history", nmap_file)
                with open(nmap_path, "r", encoding="utf-8") as f:
                    nmap_data = f.read()
                self.assertIn("nmap output", nmap_data)
                mock_run.assert_called_once()
                called_args, called_kwargs = mock_run.call_args
                cmd = called_args[0]
                self.assertEqual(cmd[:3], ["nmap", "-Pn", "-iL"])
                self.assertTrue(cmd[3].endswith("_ips.txt"))
                self.assertEqual(cmd[4:9], ["-sT", "-p", "443", "--script", "ssl-cert"])
                self.assertEqual(cmd[9:], ["--min-parallelism", "10"])
                self.assertEqual(called_kwargs["capture_output"], True)
                self.assertEqual(called_kwargs["text"], True)
                self.assertEqual(called_kwargs["timeout"], 300)
                # domain summary should not be logged since nmap output lacks the domain
                self.assertFalse(any("Nmap domain summary:" in r for r in logger.records))
            finally:
                os.chdir(cwd)


class HighlightTests(unittest.TestCase):
    @patch("libs.dns.dnscommands.wait_for_enter")
    @patch("libs.dns.dnscommands.subprocess.run")
    @patch("libs.dns.dnscommands.requests.get")
    @patch("libs.dns.dnscommands.time.strftime", return_value="20240101_120000")
    def test_nmap_highlight_logged(self, mock_ts, mock_get, mock_run, _mock_wait):
        html = """
            <table>
            <tr><th>IP Address</th><th>Location</th><th>Owner</th><th>Last Seen</th></tr>
            <tr><td>3.3.3.3</td><td>US</td><td>Corp</td><td>2024-01-03</td></tr>
            </table>
        """

        class Resp:
            status_code = 200
            text = html

        mock_get.return_value = Resp()
        mock_run.return_value = subprocess.CompletedProcess(
            ["nmap"], 0, stdout="open port on foo.test.co.uk (3.3.3.3)"
        )

        driver = DummyDriver()
        driver.current_url = "http://foo.test.co.uk"
        logger = RecordLogger()
        cmds = DNSCommands(driver, DummyCurses(), logger, [])

        with tempfile.TemporaryDirectory() as tmpdir:
            cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                cmds.show_history()
                self.assertIn("Highlighted nmap results:", logger.records)
                self.assertTrue(any("foo.test.co.uk" in r for r in logger.records))
                self.assertTrue(any("3.3.3.3" in r for r in logger.records))
                self.assertIn("Nmap domain summary:", logger.records)
                self.assertTrue(any("3.3.3.3" in r and "foo.test.co.uk" in r for r in logger.records))
            finally:
                os.chdir(cwd)

    @patch("libs.dns.dnscommands.wait_for_enter")
    @patch("libs.dns.dnscommands.subprocess.run")
    @patch("libs.dns.dnscommands.requests.get")
    @patch("libs.dns.dnscommands.time.strftime", return_value="20240101_120000")
    def test_nmap_highlight_with_separate_domain_line(self, mock_ts, mock_get, mock_run, _mock_wait):
        html = """
            <table>
            <tr><th>IP Address</th><th>Location</th><th>Owner</th><th>Last Seen</th></tr>
            <tr><td>4.4.4.4</td><td>US</td><td>Corp</td><td>2024-01-04</td></tr>
            </table>
        """

        class Resp:
            status_code = 200
            text = html

        mock_get.return_value = Resp()
        mock_run.return_value = subprocess.CompletedProcess(
            ["nmap"],
            0,
            stdout="Nmap scan report for 4.4.4.4\n| ssl-cert: Subject: commonName=bar.test.co.uk",
        )

        driver = DummyDriver()
        driver.current_url = "http://bar.test.co.uk"
        logger = RecordLogger()
        cmds = DNSCommands(driver, DummyCurses(), logger, [])

        with tempfile.TemporaryDirectory() as tmpdir:
            cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                cmds.show_history()
                self.assertIn("Highlighted nmap results:", logger.records)
                self.assertTrue(any("bar.test.co.uk" in r for r in logger.records))
                self.assertTrue(any("4.4.4.4" in r for r in logger.records))
                self.assertIn("Nmap domain summary:", logger.records)
                self.assertTrue(any("4.4.4.4" in r and "bar.test.co.uk" in r for r in logger.records))
            finally:
                os.chdir(cwd)


if __name__ == "__main__":
    unittest.main()

