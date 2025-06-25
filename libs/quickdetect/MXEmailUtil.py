class MXEmailUtil:
    def __init__(self, current_url, logger):
        self.current_url = current_url
        self.logger = logger

    def _get_root_domain(self):
        """Return the registrable domain of the current URL."""
        from libs.utils import get_root_domain

        return get_root_domain(self.current_url)

    def _query_mx_records(self, domain):
        records = []
        try:
            import dns.resolver  # type: ignore
            answers = dns.resolver.resolve(domain, 'MX')
            for rdata in answers:
                records.append(str(rdata.exchange).lower())
        except Exception:
            pass
        if not records:
            try:
                import subprocess
                output = subprocess.check_output(
                    ['dig', '+short', domain, 'mx'],
                    text=True,
                    timeout=5
                )
                for line in output.splitlines():
                    parts = line.strip().split()
                    if parts:
                        records.append(parts[-1].strip('.').lower())
            except Exception:
                pass
        return records

    def get_provider(self):
        domain = self._get_root_domain()
        if not domain:
            return None
        records = self._query_mx_records(domain)
        providers = {
            'outlook': 'Office 365',
            'office365': 'Office 365',
            'microsoft': 'Office 365',
            'google': 'Google Workspace',
            'googlemail': 'Google Workspace',
            'aspmx': 'Google Workspace',
            'zoho': 'Zoho Mail',
            'yahoodns': 'Yahoo Mail',
            'yahoo': 'Yahoo Mail',
            'amazonaws': 'Amazon WorkMail',
            'secureserver': 'GoDaddy Email',
            'protonmail': 'ProtonMail',
            'messagingengine.com': 'FastMail',
        }
        for rec in records:
            for key, provider in providers.items():
                if key in rec:
                    return provider
        return None
