"""Common utility functions for the agent."""
import logging
from typing import Optional
from packaging import version as pkg_version

logger = logging.getLogger(__name__)


def setup_logging(log_level: str = "INFO") -> None:
    """Configure logging for the agent.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def is_compatible_version(required_spec: str, candidate: str) -> bool:
    """Check if a candidate version satisfies a version requirement.
    
    Args:
        required_spec: Version specifier (e.g., ">=1.0,<2.0", "^1.2.3")
        candidate: Candidate version to check
        
    Returns:
        True if candidate satisfies the requirement
    """
    try:
        from packaging.specifiers import SpecifierSet
        
        # Normalize npm-style specs to PEP 440
        spec_normalized = _normalize_version_spec(required_spec)
        
        specifier_set = SpecifierSet(spec_normalized)
        return candidate in specifier_set
    except Exception as e:
        logger.warning(f"Failed to check version compatibility: {e}")
        return False


def _normalize_version_spec(spec: str) -> str:
    """Normalize version specifiers to PEP 440 format.
    
    Args:
        spec: Version specifier (possibly in npm format like "^1.2.3")
        
    Returns:
        Normalized specifier string
    """
    spec = spec.strip()
    
    # npm caret (^): compatible with version (allows changes that don't modify the left-most non-zero digit)
    if spec.startswith("^"):
        version_str = spec[1:]
        try:
            v = pkg_version.parse(version_str)
            if v.major != 0:
                return f">={version_str},<{v.major + 1}.0.0"
            elif v.minor != 0:
                return f">={version_str},<0.{v.minor + 1}.0"
            else:
                return f">={version_str},<0.0.{v.micro + 1}"
        except:
            pass
    
    # npm tilde (~): compatible with version (allows patch-level changes)
    elif spec.startswith("~"):
        version_str = spec[1:]
        try:
            v = pkg_version.parse(version_str)
            return f">={version_str},<{v.major}.{v.minor + 1}.0"
        except:
            pass
    
    # Handle ranges
    elif "," in spec:
        parts = spec.split(",")
        return ",".join(_normalize_version_spec(p.strip()) for p in parts)
    
    return spec


def get_latest_compatible_version(
    available_versions: list,
    required_spec: str,
) -> Optional[str]:
    """Get the latest version that satisfies a requirement.
    
    Args:
        available_versions: List of available versions
        required_spec: Version requirement specifier
        
    Returns:
        Latest compatible version or None
    """
    compatible = [v for v in available_versions if is_compatible_version(required_spec, v)]
    
    if not compatible:
        return None
    
    try:
        return str(max(compatible, key=pkg_version.parse))
    except Exception as e:
        logger.error(f"Failed to find latest compatible version: {e}")
        return None
