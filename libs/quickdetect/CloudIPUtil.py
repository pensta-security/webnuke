import socket
from urllib.parse import urlparse
from ipwhois import IPWhois

class CloudIPUtil:
    def __init__(self, url):
        self.url = url

    def get_provider(self):
        parsed = urlparse(self.url)
        domain = parsed.hostname
        if not domain:
            return None
        try:
            ip = socket.gethostbyname(domain)
        except Exception:
            return None
        try:
            obj = IPWhois(ip)
            data = obj.lookup_rdap(depth=1)
            text = "{} {}".format(
                data.get('network', {}).get('name', ''),
                data.get('asn_description', '')
            ).lower()
            providers = {
                'amazon': 'AWS',
                'google': 'Google Cloud',
                'microsoft': 'Azure',
                'cloudflare': 'Cloudflare',
                'digitalocean': 'DigitalOcean',
                'ovh': 'OVH'
            }
            for key, val in providers.items():
                if key in text:
                    return val
        except Exception:
            return None
        return None

