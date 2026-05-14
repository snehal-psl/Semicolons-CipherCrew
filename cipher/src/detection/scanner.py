"""CVE scanner combining multiple data sources."""
import logging
from typing import List, Dict, Set, Optional
from dataclasses import dataclass

from .vulnerability import Vulnerability, CVESeverity, CVESource
from .nvd_client import NVDClient
from .osv_client import OSVClient

logger = logging.getLogger(__name__)


@dataclass
class ScanResult:
    """Result of a CVE scan."""
    package_name: str
    ecosystem: str
    version: str
    vulnerabilities: List[Vulnerability]
    
    def get_by_severity(self, severity: CVESeverity) -> List[Vulnerability]:
        """Filter vulnerabilities by severity level."""
        return [v for v in self.vulnerabilities if v.severity == severity]
    
    def critical_count(self) -> int:
        """Count critical vulnerabilities."""
        return len(self.get_by_severity(CVESeverity.CRITICAL))
    
    def high_count(self) -> int:
        """Count high severity vulnerabilities."""
        return len(self.get_by_severity(CVESeverity.HIGH))


class Scanner:
    """CVE vulnerability scanner."""
    
    def __init__(self, nvd_api_key: Optional[str] = None):
        """Initialize scanner with multiple data sources.
        
        Args:
            nvd_api_key: Optional NVD API key for higher rate limits
        """
        self.nvd_client = NVDClient(api_key=nvd_api_key)
        self.osv_client = OSVClient()
    
    def scan_package(
        self,
        package_name: str,
        ecosystem: str,
        version: str,
        min_severity: CVESeverity = CVESeverity.MEDIUM,
    ) -> ScanResult:
        """Scan a package for vulnerabilities.
        
        Args:
            package_name: Package name
            ecosystem: Package ecosystem (npm, pip, maven, etc.)
            version: Package version to scan
            min_severity: Minimum severity level to report
            
        Returns:
            ScanResult with vulnerabilities
        """
        logger.info(f"Scanning {ecosystem}:{package_name}@{version}")
        
        # Query OSV (primary source for package-specific data)
        vulns = self.osv_client.query_package(package_name, ecosystem, version)
        
        # Deduplicate and filter by severity
        deduped = self._deduplicate_vulns(vulns)
        filtered = [v for v in deduped if self._meets_severity_threshold(v, min_severity)]
        
        result = ScanResult(
            package_name=package_name,
            ecosystem=ecosystem,
            version=version,
            vulnerabilities=filtered,
        )
        
        logger.info(f"Found {len(filtered)} vulnerabilities for {package_name}@{version}")
        return result
    
    def scan_packages(
        self,
        packages: List[Dict[str, str]],
        min_severity: CVESeverity = CVESeverity.MEDIUM,
    ) -> List[ScanResult]:
        """Scan multiple packages.
        
        Args:
            packages: List of {name, ecosystem, version} dicts
            min_severity: Minimum severity level to report
            
        Returns:
            List of ScanResult objects
        """
        results = []
        for pkg in packages:
            result = self.scan_package(
                package_name=pkg["name"],
                ecosystem=pkg["ecosystem"],
                version=pkg["version"],
                min_severity=min_severity,
            )
            results.append(result)
        
        return results
    
    def _deduplicate_vulns(self, vulns: List[Vulnerability]) -> List[Vulnerability]:
        """Remove duplicate vulnerabilities by CVE ID.
        
        Args:
            vulns: List of vulnerabilities (possibly with duplicates)
            
        Returns:
            List with duplicates removed, preferring more complete records
        """
        seen: Dict[str, Vulnerability] = {}
        for v in vulns:
            if v.cve_id not in seen:
                seen[v.cve_id] = v
            else:
                # Merge sources and prefer record with more data
                existing = seen[v.cve_id]
                if len(v.description) > len(existing.description):
                    existing.description = v.description
                if v.cvss and not existing.cvss:
                    existing.cvss = v.cvss
                if v.epss_score and not existing.epss_score:
                    existing.epss_score = v.epss_score
                existing.sources = list(set(existing.sources + v.sources))
        
        return list(seen.values())
    
    def _meets_severity_threshold(self, vuln: Vulnerability, min_severity: CVESeverity) -> bool:
        """Check if vulnerability meets minimum severity threshold.
        
        Args:
            vuln: Vulnerability to check
            min_severity: Minimum severity level
            
        Returns:
            True if vulnerability meets or exceeds min_severity
        """
        severity_order = [CVESeverity.LOW, CVESeverity.MEDIUM, CVESeverity.HIGH, CVESeverity.CRITICAL]
        try:
            vuln_idx = severity_order.index(vuln.severity)
            min_idx = severity_order.index(min_severity)
            return vuln_idx >= min_idx
        except ValueError:
            return False
    
    def close(self):
        """Close all HTTP clients."""
        self.nvd_client.close()
        self.osv_client.close()
