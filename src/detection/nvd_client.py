"""NVD (National Vulnerability Database) API client."""
import logging
import requests
from typing import List, Optional, Dict, Any
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential

from .vulnerability import Vulnerability, CVESeverity, CVSS, CVESource

logger = logging.getLogger(__name__)


class NVDClient:
    """Client for fetching CVE data from NVD API."""
    
    BASE_URL = "https://services.nvd.nist.gov/rest/json"
    API_VERSION = "2.0"
    
    def __init__(self, api_key: Optional[str] = None, timeout: int = 10):
        """Initialize NVD client.
        
        Args:
            api_key: Optional NVD API key for higher rate limits
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def search_cpe(self, cpe: str) -> List[Vulnerability]:
        """Search for CVEs by CPE identifier.
        
        Args:
            cpe: CPE 2.3 format identifier (e.g., cpe:2.3:a:vendor:product:version:*:*:*:*:*:*:*)
            
        Returns:
            List of vulnerabilities
        """
        url = f"{self.BASE_URL}/cves/{self.API_VERSION}"
        params = {
            "cpeName": cpe,
            "resultsPerPage": 100,
        }
        if self.api_key:
            params["apiKey"] = self.api_key
        
        try:
            resp = self.session.get(url, params=params, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            vulnerabilities = []
            
            for vuln_item in data.get("vulnerabilities", []):
                vuln = self._parse_nvd_vulnerability(vuln_item)
                if vuln:
                    vulnerabilities.append(vuln)
            
            return vulnerabilities
        except requests.RequestException as e:
            logger.error(f"NVD API error for CPE {cpe}: {e}")
            return []
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def search_by_package(self, package_name: str, ecosystem: str) -> List[Vulnerability]:
        """Search for CVEs by package name.
        
        Args:
            package_name: Package name
            ecosystem: Package ecosystem (npm, pip, etc.)
            
        Returns:
            List of vulnerabilities
        """
        # NVD doesn't search by package directly; this is a simplified interface
        # In production, would map package names to CPEs via NVD data
        logger.warning(f"NVD search_by_package not directly supported. Use search_cpe instead.")
        return []
    
    def _parse_nvd_vulnerability(self, item: Dict[str, Any]) -> Optional[Vulnerability]:
        """Parse NVD vulnerability JSON structure.
        
        Args:
            item: Vulnerability item from NVD API
            
        Returns:
            Parsed Vulnerability object or None
        """
        try:
            cve_meta = item.get("cve", {})
            cve_id = cve_meta.get("id", "UNKNOWN")
            description = ""
            
            # Extract description
            for desc in cve_meta.get("descriptions", []):
                if desc.get("lang") == "en":
                    description = desc.get("value", "")
                    break
            
            # Extract CVSS score
            cvss = None
            metrics = item.get("metrics", {})
            cvss_v31 = metrics.get("cvssMetricV31", [])
            if cvss_v31:
                cvss_data = cvss_v31[0].get("cvssData", {})
                score = cvss_data.get("baseScore", 0.0)
                vector = cvss_data.get("vectorString", "")
                severity = CVESeverity.from_cvss_score(score)
                cvss = CVSS(version="3.1", score=score, vector=vector, severity=severity)
            
            # Published date
            published = cve_meta.get("published", "")
            published_date = None
            if published:
                try:
                    published_date = datetime.fromisoformat(published.replace("Z", "+00:00"))
                except ValueError:
                    pass
            
            # For now, return minimal vulnerability (full affectedVersions parsing requires product mappings)
            vuln = Vulnerability(
                cve_id=cve_id,
                package_name="",  # Not directly available in NVD
                ecosystem="unknown",
                affected_versions=[],
                fixed_versions=[],
                severity=cvss.severity if cvss else CVESeverity.UNKNOWN,
                cvss=cvss,
                description=description,
                published_date=published_date,
                sources=[CVESource.NVD],
            )
            return vuln
        except Exception as e:
            logger.error(f"Failed to parse NVD vulnerability: {e}")
            return None
    
    def close(self):
        """Close HTTP session."""
        self.session.close()
