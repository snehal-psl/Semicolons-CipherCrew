"""PR generation and formatting module."""
from dataclasses import dataclass
from typing import List, Optional, Dict
from enum import Enum

from src.detection import Vulnerability, CVESeverity


class RiskLevel(str, Enum):
    """Risk level for a remediation PR."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass
class RemediationPR:
    """Pull request for CVE remediation."""
    title: str
    description: str
    branch_name: str
    vulnerabilities: List[Vulnerability]
    changes: Dict[str, str]  # File path -> new content
    risk_level: RiskLevel
    requires_approval: bool = True
    assignees: List[str] = None
    labels: List[str] = None
    
    def __post_init__(self):
        """Initialize optional fields."""
        if self.assignees is None:
            self.assignees = []
        if self.labels is None:
            self.labels = []
    
    def get_risk_factors(self) -> List[str]:
        """Get human-readable risk factors."""
        factors = []
        
        critical_count = sum(1 for v in self.vulnerabilities if v.severity == CVESeverity.CRITICAL)
        if critical_count > 0:
            factors.append(f"Fixes {critical_count} critical CVE(s)")
        
        # Add more risk factors as needed
        return factors


class PRBuilder:
    """Builder for remediation pull requests."""
    
    @staticmethod
    def build_pr(
        vulnerabilities: List[Vulnerability],
        package_name: str,
        old_version: str,
        new_version: str,
        ecosystem: str,
        changes: Dict[str, str],
    ) -> RemediationPR:
        """Build a remediation PR from vulnerability data.
        
        Args:
            vulnerabilities: List of vulnerabilities being fixed
            package_name: Package name
            old_version: Current version
            new_version: Upgraded version
            ecosystem: Package ecosystem
            changes: File changes (path -> content)
            
        Returns:
            RemediationPR object
        """
        # Determine risk level
        risk_level = PRBuilder._assess_risk(vulnerabilities, old_version, new_version)
        
        # Build title and description
        cve_ids = [v.cve_id for v in vulnerabilities]
        title = PRBuilder._build_title(cve_ids, package_name, old_version, new_version)
        description = PRBuilder._build_description(vulnerabilities, package_name, old_version, new_version)
        
        # Build branch name
        branch_name = PRBuilder._build_branch_name(
            cve_ids[0] if cve_ids else "security",
            package_name,
            ecosystem,
        )
        
        # Determine approval requirement
        requires_approval = risk_level != RiskLevel.LOW
        
        # Assign labels
        labels = ["security", "cve", ecosystem]
        if risk_level == RiskLevel.CRITICAL:
            labels.append("critical")
        
        pr = RemediationPR(
            title=title,
            description=description,
            branch_name=branch_name,
            vulnerabilities=vulnerabilities,
            changes=changes,
            risk_level=risk_level,
            requires_approval=requires_approval,
            labels=labels,
        )
        
        return pr
    
    @staticmethod
    def _assess_risk(
        vulnerabilities: List[Vulnerability],
        old_version: str,
        new_version: str,
    ) -> RiskLevel:
        """Assess risk level of the upgrade.
        
        Args:
            vulnerabilities: Vulnerabilities being fixed
            old_version: Current version
            new_version: New version
            
        Returns:
            RiskLevel assessment
        """
        from packaging import version as pkg_version
        
        # Check if it's a major version bump
        try:
            old_v = pkg_version.parse(old_version)
            new_v = pkg_version.parse(new_version)
            
            if old_v.major != new_v.major:
                return RiskLevel.HIGH
        except Exception:
            pass
        
        # Check severity of vulnerabilities
        critical_count = sum(1 for v in vulnerabilities if v.severity == CVESeverity.CRITICAL)
        if critical_count > 1:
            return RiskLevel.HIGH
        
        return RiskLevel.MEDIUM
    
    @staticmethod
    def _build_title(cve_ids: List[str], package_name: str, old_ver: str, new_ver: str) -> str:
        """Build PR title."""
        cve_str = ", ".join(cve_ids[:3])  # Limit to 3 CVEs in title
        return f"chore(security): remediate {cve_str} in {package_name} ({old_ver} → {new_ver})"
    
    @staticmethod
    def _build_description(
        vulnerabilities: List[Vulnerability],
        package_name: str,
        old_version: str,
        new_version: str,
    ) -> str:
        """Build PR description."""
        lines = [
            f"## Security Update for {package_name}",
            "",
            f"**Upgrade**: `{old_version}` → `{new_version}`",
            "",
            "### Vulnerabilities Fixed",
            "",
        ]
        
        for vuln in vulnerabilities[:10]:  # Limit to 10 in description
            severity_emoji = {
                CVESeverity.CRITICAL: "🔴",
                CVESeverity.HIGH: "🟠",
                CVESeverity.MEDIUM: "🟡",
                CVESeverity.LOW: "🟢",
                CVESeverity.UNKNOWN: "⚪",
            }.get(vuln.severity, "⚪")
            
            cvss_info = ""
            if vuln.cvss:
                cvss_info = f" (CVSS {vuln.cvss.score})"
            
            lines.append(f"- {severity_emoji} {vuln.cve_id}{cvss_info}")
            if vuln.description:
                lines.append(f"  {vuln.description[:100]}")
        
        lines.extend([
            "",
            "### Testing",
            "- [ ] Local tests pass",
            "- [ ] No breaking changes detected",
            "",
            "### Checklist",
            "- [ ] Review security advisory",
            "- [ ] Verify changelog for breaking changes",
            "- [ ] Test in staging environment",
        ])
        
        return "\n".join(lines)
    
    @staticmethod
    def _build_branch_name(cve_id: str, package_name: str, ecosystem: str) -> str:
        """Build git branch name."""
        # Sanitize package name
        safe_pkg = package_name.lower().replace("/", "-").replace("_", "-")
        return f"security/{cve_id}-{ecosystem}-{safe_pkg}".lower()
