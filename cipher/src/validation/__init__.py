"""Validation and confidence scoring module."""
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Result of running tests."""
    passed: int
    failed: int
    skipped: int
    
    def pass_rate(self) -> float:
        """Calculate pass rate."""
        total = self.passed + self.failed
        if total == 0:
            return 0.0
        return self.passed / total


class ConfidenceScorer:
    """Score confidence level of remediation."""
    
    @staticmethod
    def score_upgrade(
        test_results: Optional[TestResult],
        changelog_analysis: Dict[str, bool],
        version_bump_type: str,
    ) -> float:
        """Score confidence of an upgrade (0.0 - 1.0).
        
        Args:
            test_results: Test execution results
            changelog_analysis: Analysis results from changelog
            version_bump_type: Type of version bump (patch, minor, major)
            
        Returns:
            Confidence score (0.0 = low confidence, 1.0 = high confidence)
        """
        score = 0.5  # Base score
        
        # Test results weight: 40%
        if test_results:
            score += (test_results.pass_rate() * 0.4)
        else:
            score -= 0.1  # Penalize missing tests
        
        # Changelog analysis weight: 30%
        breaking_changes = changelog_analysis.get("has_breaking_changes", True)
        deprecations = changelog_analysis.get("has_deprecations", True)
        
        if not breaking_changes and not deprecations:
            score += 0.3
        elif not breaking_changes:
            score += 0.15
        
        # Version bump type weight: 30%
        if version_bump_type == "patch":
            score += 0.3
        elif version_bump_type == "minor":
            score += 0.15
        
        # Normalize to [0, 1]
        return max(0.0, min(1.0, score))
