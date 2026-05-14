"""CVE detection module."""
from .vulnerability import Vulnerability, CVESeverity, CVESource
from .nvd_client import NVDClient
from .osv_client import OSVClient
from .scanner import Scanner

__all__ = [
    "Vulnerability",
    "CVESeverity",
    "CVESource",
    "NVDClient",
    "OSVClient",
    "Scanner",
]
