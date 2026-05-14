"""OSV (Open Source Vulnerabilities) database API client."""
import logging
import requests
from typing import List, Optional, Dict, Any
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential

from .vulnerability import Vulnerability, CVESeverity, CVSS, CVESource

logger = logging.getLogger(__name__)


class OSVClient:
    """Client for querying OSV database."""
    
    BASE_URL = "https://api.osv.dev/v1"
    
    def __init__(self, timeout: int = 10):
        """Initialize OSV client.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def query_package(self, package_name: str, ecosystem: str, version: Optional[str] = None) -> List[Vulnerability]:
        """Query OSV for vulnerabilities in a package.
        
        Args:
            package_name: Package name
            ecosystem: Package ecosystem (npm, pip, maven, etc.)
            version: Optional specific version to query
            
        Returns:
            List of vulnerabilities
        """
        url = f"{self.BASE_URL}/query"
        payload = {
            "package": {
                "name": package_name,
                "ecosystem": ecosystem,
            }
        }
        if version:
            payload["package"]["version"] = version
        
        try:
            resp = self.session.post(url, json=payload, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            
            vulnerabilities = []
            for vuln_item in data.get("vulns", []):
                vuln = self._parse_osv_vulnerability(vuln_item, package_name, ecosystem)
                if vuln:
                    vulnerabilities.append(vuln)
            
            return vulnerabilities
        except requests.RequestException as e:
            logger.error(f"OSV API error for {ecosystem}:{package_name}: {e}")
            return []
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def query_cve(self, cve_id: str) -> Optional[Vulnerability]:
        """Query OSV by CVE ID.
        
        Args:
            cve_id: CVE identifier (e.g., CVE-2021-12345)
            
        Returns:
            Vulnerability or None
        """
        url = f"{self.BASE_URL}/query"
        payload = {"query": cve_id}
        
        try:
            resp = self.session.post(url, json=payload, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            
            vulns = data.get("vulns", [])
            if vulns:
                return self._parse_osv_vulnerability(vulns[0], "", "")
        except requests.RequestException as e:
            logger.error(f"OSV API error for CVE {cve_id}: {e}")
        
        return None
    
    def _parse_osv_vulnerability(
        self, item: Dict[str, Any], package_name: str, ecosystem: str
    ) -> Optional[Vulnerability]:
        """Parse OSV vulnerability JSON.
        
        Args:
            item: Vulnerability item from OSV API
            package_name: Package name
            ecosystem: Package ecosystem
            
        Returns:
            Parsed Vulnerability object or None
        """
        try:
            vuln_id = item.get("id", "UNKNOWN")
            description = item.get("summary", "") or item.get("details", "")
            
            # Affected versions
            affected_versions = []
            fixed_versions = []
            for affected in item.get("affected", []):
                if affected.get("package", {}).get("name") == package_name:
                    # Parse ranges
                    for version_range in affected.get("versions", []):
                        affected_versions.append(version_range)
                    
                    # Parse fixed versions
                    ranges = affected.get("ranges", [])
                    for range_item in ranges:
                        for fixed in range_item.get("fixed", []):
                            if fixed:
                                fixed_versions.append(fixed)
            
            # CVSS score from references
            severity = CVESeverity.UNKNOWN
            cvss = None
            for ref in item.get("references", []):
                if "cvss" in ref.get("url", "").lower():
                    # Try to extract CVSS score from NVD reference
                    pass
            
            # Published date
            published = item.get("published", "")
            published_date = None
            if published:
                try:
                    published_date = datetime.fromisoformat(published.replace("Z", "+00:00"))
                except ValueError:
                    pass
            
            vuln = Vulnerability(
                cve_id=vuln_id,
                package_name=package_name,
                ecosystem=ecosystem,
                affected_versions=affected_versions,
                fixed_versions=fixed_versions,
                severity=severity,
                cvss=cvss,
                description=description,
                published_date=published_date,
                sources=[CVESource.OSV],
            )
            return vuln
        except Exception as e:
            logger.error(f"Failed to parse OSV vulnerability: {e}")
            return None
    
    def close(self):
        """Close HTTP session."""
        self.session.close()
