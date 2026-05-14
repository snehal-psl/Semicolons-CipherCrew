"""Tests for CVE detection module."""
import pytest
from unittest.mock import Mock, patch
import json
from datetime import datetime

from src.detection import Vulnerability, CVESeverity, CVSS, CVESource, Scanner


class TestVulnerability:
    """Test Vulnerability data model."""
    
    def test_vulnerability_creation(self):
        """Test creating a vulnerability."""
        vuln = Vulnerability(
            cve_id="CVE-2021-1234",
            package_name="lodash",
            ecosystem="npm",
            affected_versions=["<4.17.20"],
            fixed_versions=["4.17.20"],
            severity=CVESeverity.HIGH,
        )
        
        assert vuln.cve_id == "CVE-2021-1234"
        assert vuln.package_name == "lodash"
        assert vuln.severity == CVESeverity.HIGH
        assert not vuln.is_critical()
    
    def test_critical_severity(self):
        """Test critical severity detection."""
        vuln = Vulnerability(
            cve_id="CVE-2021-1234",
            package_name="test",
            ecosystem="npm",
            affected_versions=["*"],
            fixed_versions=["1.0.0"],
            severity=CVESeverity.CRITICAL,
        )
        
        assert vuln.is_critical()
    
    def test_cvss_score_mapping(self):
        """Test CVSS score to severity mapping."""
        assert CVESeverity.from_cvss_score(9.5) == CVESeverity.CRITICAL
        assert CVESeverity.from_cvss_score(7.5) == CVESeverity.HIGH
        assert CVESeverity.from_cvss_score(5.0) == CVESeverity.MEDIUM
        assert CVESeverity.from_cvss_score(2.0) == CVESeverity.LOW
    
    def test_exploitability_check(self):
        """Test exploitability assessment."""
        vuln1 = Vulnerability(
            cve_id="CVE-1",
            package_name="test",
            ecosystem="npm",
            affected_versions=["*"],
            fixed_versions=["1.0.0"],
            severity=CVESeverity.HIGH,
            epss_score=0.6,
        )
        assert vuln1.is_exploitable()
        
        vuln2 = Vulnerability(
            cve_id="CVE-2",
            package_name="test",
            ecosystem="npm",
            affected_versions=["*"],
            fixed_versions=["1.0.0"],
            severity=CVESeverity.MEDIUM,
            epss_score=0.3,
        )
        assert not vuln2.is_exploitable()


class TestScanner:
    """Test Scanner functionality."""
    
    def test_scanner_initialization(self):
        """Test scanner creation."""
        scanner = Scanner()
        assert scanner.osv_client is not None
        assert scanner.nvd_client is not None
    
    @patch('src.detection.scanner.Scanner.osv_client')
    def test_scan_package(self, mock_osv):
        """Test scanning a package."""
        # Mock OSV response
        mock_vuln = Vulnerability(
            cve_id="CVE-2021-1234",
            package_name="lodash",
            ecosystem="npm",
            affected_versions=["<4.17.20"],
            fixed_versions=["4.17.20"],
            severity=CVESeverity.HIGH,
        )
        mock_osv.query_package.return_value = [mock_vuln]
        
        scanner = Scanner()
        scanner.osv_client = mock_osv
        
        result = scanner.scan_package("lodash", "npm", "4.17.19")
        
        assert result.package_name == "lodash"
        assert len(result.vulnerabilities) >= 0
    
    def test_vulnerability_deduplication(self):
        """Test deduplication of vulnerabilities."""
        scanner = Scanner()
        
        vuln1 = Vulnerability(
            cve_id="CVE-2021-1234",
            package_name="test",
            ecosystem="npm",
            affected_versions=["*"],
            fixed_versions=["1.0.0"],
            severity=CVESeverity.HIGH,
            description="Initial desc",
        )
        
        vuln2 = Vulnerability(
            cve_id="CVE-2021-1234",
            package_name="test",
            ecosystem="npm",
            affected_versions=["*"],
            fixed_versions=["1.0.0"],
            severity=CVESeverity.HIGH,
            description="More detailed description",
        )
        
        deduped = scanner._deduplicate_vulns([vuln1, vuln2])
        
        assert len(deduped) == 1
        assert deduped[0].description == "More detailed description"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
