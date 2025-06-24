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
            <tr><td>1.1.1.1</td><td>US</td><td>Cloudflare</td><td>2024-01-01</td></tr>
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
                self.assertEqual(len(files), 2)
                hist_file = [f for f in files if not f.endswith("_nmap.txt")][0]
                nmap_file = [f for f in files if f.endswith("_nmap.txt")][0]
                path = os.path.join("dns_history", hist_file)
                with open(path, "r", encoding="utf-8") as f:
                    data = f.read()
                self.assertIn("2024-01-01: 1.1.1.1 - Cloudflare", data)
                nmap_path = os.path.join("dns_history", nmap_file)
                with open(nmap_path, "r", encoding="utf-8") as f:
                    nmap_data = f.read()
                self.assertIn("nmap output", nmap_data)
                mock_run.assert_called_with(
                    ["nmap", "-sT", "-p", "443", "--script", "ssl-cert", "1.1.1.1"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
            finally:
                os.chdir(cwd)


if __name__ == "__main__":
    unittest.main()

