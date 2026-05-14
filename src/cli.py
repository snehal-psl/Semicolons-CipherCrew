"""CLI entry point for the CVE Remediation Agent."""
import argparse
import sys
import logging
from pathlib import Path

from src.utils import setup_logging


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Autonomous AI CVE Remediation Agent",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan project for CVEs")
    scan_parser.add_argument(
        "project_path",
        type=str,
        help="Path to project to scan",
    )
    scan_parser.add_argument(
        "--min-severity",
        choices=["CRITICAL", "HIGH", "MEDIUM", "LOW"],
        default="CRITICAL",
        help="Minimum CVE severity to report",
    )
    scan_parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file",
    )
    
    # Remediate command
    remediate_parser = subparsers.add_parser("remediate", help="Scan and generate remediation PRs")
    remediate_parser.add_argument(
        "project_path",
        type=str,
        help="Path to project to remediate",
    )
    remediate_parser.add_argument(
        "--auto-pr",
        action="store_true",
        help="Automatically create pull requests",
    )
    remediate_parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file",
    )
    
    # Batch command
    batch_parser = subparsers.add_parser("batch", help="Scan multiple repositories")
    batch_parser.add_argument(
        "--repos",
        type=str,
        required=True,
        help="Comma-separated list of repository paths",
    )
    batch_parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file",
    )
    
    # Version command
    subparsers.add_parser("version", help="Show version information")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(log_level="INFO")
    logger = logging.getLogger(__name__)
    
    if not args.command:
        parser.print_help()
        return 1
    
    if args.command == "scan":
        return cmd_scan(args)
    elif args.command == "remediate":
        return cmd_remediate(args)
    elif args.command == "batch":
        return cmd_batch(args)
    elif args.command == "version":
        return cmd_version()
    else:
        parser.print_help()
        return 1


def cmd_scan(args) -> int:
    """Handle scan command."""
    logger = logging.getLogger(__name__)
    
    from src.detection import Scanner
    
    project_path = Path(args.project_path)
    if not project_path.exists():
        logger.error(f"Project path not found: {project_path}")
        return 1
    
    logger.info(f"Scanning project: {project_path}")
    logger.info("Phase 1: Basic scanning infrastructure ready")
    logger.info("Note: Full implementation requires Phase 2-3 (version resolution, PR generation)")
    
    return 0


def cmd_remediate(args) -> int:
    """Handle remediate command."""
    logger = logging.getLogger(__name__)
    
    logger.info(f"Remediating project: {args.project_path}")
    logger.info("Auto-PR mode: {}".format("enabled" if args.auto_pr else "disabled"))
    logger.info("Note: Full implementation requires Phase 2-3 (version resolution, PR generation)")
    
    return 0


def cmd_batch(args) -> int:
    """Handle batch command."""
    logger = logging.getLogger(__name__)
    
    repos = [r.strip() for r in args.repos.split(",")]
    logger.info(f"Batch scanning {len(repos)} repositories")
    
    for repo in repos:
        logger.info(f"  - {repo}")
    
    logger.info("Note: Full implementation requires Phase 2-3 (version resolution, PR generation)")
    
    return 0


def cmd_version() -> int:
    """Show version information."""
    from src import __version__
    print(f"CVE Remediation Agent v{__version__}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
