"""npm/yarn/pnpm package lock file parser."""
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from .models import DependencyGraph, DependencyType

logger = logging.getLogger(__name__)


class NPMParser:
    """Parser for npm package-lock.json and yarn.lock formats."""
    
    @staticmethod
    def parse_package_lock(lock_file_path: str) -> DependencyGraph:
        """Parse npm package-lock.json file.
        
        Args:
            lock_file_path: Path to package-lock.json
            
        Returns:
            DependencyGraph representation
            
        Raises:
            FileNotFoundError: If lock file doesn't exist
            json.JSONDecodeError: If lock file is invalid JSON
        """
        with open(lock_file_path, 'r') as f:
            lock_data = json.load(f)
        
        graph = DependencyGraph(ecosystem="npm")
        
        # Root package info
        root_name = lock_data.get("name", "root")
        graph.root_package = root_name
        
        # Parse lockfileVersion to handle different formats
        lock_version = lock_data.get("lockfileVersion", 1)
        
        if lock_version >= 3:
            NPMParser._parse_lock_v3(lock_data, graph)
        elif lock_version >= 2:
            NPMParser._parse_lock_v2(lock_data, graph)
        else:
            NPMParser._parse_lock_v1(lock_data, graph)
        
        logger.info(f"Parsed npm lock file: {len(graph.nodes)} dependencies")
        return graph
    
    @staticmethod
    def _parse_lock_v1(lock_data: Dict[str, Any], graph: DependencyGraph) -> None:
        """Parse npm package-lock.json format v1."""
        # v1: dependencies at root level and nested within packages
        dependencies = lock_data.get("dependencies", {})
        NPMParser._process_dependencies(dependencies, graph, parent="root")
    
    @staticmethod
    def _parse_lock_v2(lock_data: Dict[str, Any], graph: DependencyGraph) -> None:
        """Parse npm package-lock.json format v2."""
        # v2: flat "packages" structure with package paths as keys
        packages = lock_data.get("packages", {})
        
        for pkg_path, pkg_data in packages.items():
            if pkg_path == "":  # Root package
                continue
            
            # Extract package name and version
            name = pkg_data.get("name", "")
            version = pkg_data.get("version", "")
            
            if name:
                graph.add_dependency(name, version, DependencyType.TRANSITIVE)
        
        # Parse dependencies
        for pkg_path, pkg_data in packages.items():
            source_name = pkg_data.get("name", "root")
            source_version = pkg_data.get("version", "")
            
            for dep_name, dep_version in pkg_data.get("dependencies", {}).items():
                graph.add_edge(source_name, source_version, dep_name, dep_version)
    
    @staticmethod
    def _parse_lock_v3(lock_data: Dict[str, Any], graph: DependencyGraph) -> None:
        """Parse npm package-lock.json format v3."""
        # v3: similar to v2
        NPMParser._parse_lock_v2(lock_data, graph)
    
    @staticmethod
    def _process_dependencies(
        deps: Dict[str, Any],
        graph: DependencyGraph,
        parent: str = "root",
    ) -> None:
        """Recursively process dependencies (for v1 format).
        
        Args:
            deps: Dependencies dict
            graph: DependencyGraph to add to
            parent: Parent package name
        """
        for name, dep_data in deps.items():
            version = dep_data.get("version", "")
            graph.add_dependency(name, version, DependencyType.TRANSITIVE)
            graph.add_edge(parent, "", name, version)
            
            # Recursively process nested dependencies
            nested_deps = dep_data.get("dependencies", {})
            if nested_deps:
                NPMParser._process_dependencies(nested_deps, graph, parent=name)
    
    @staticmethod
    def parse_yarn_lock(lock_file_path: str) -> DependencyGraph:
        """Parse yarn.lock file (simplified parser for v1 format).
        
        Args:
            lock_file_path: Path to yarn.lock
            
        Returns:
            DependencyGraph representation
            
        Note:
            This is a simplified parser. Full yarn.lock parsing is complex.
        """
        graph = DependencyGraph(ecosystem="npm")  # npm ecosystem for yarn
        
        try:
            with open(lock_file_path, 'r') as f:
                content = f.read()
            
            # Simple regex-based parsing for yarn v1 format
            # This is a simplified version; production would need more robust parsing
            import re
            
            # Pattern: "package-name@version-spec":
            pattern = r'"([^"]+)@([^"]*)":\s*\n\s*version\s*"([^"]+)"'
            matches = re.findall(pattern, content)
            
            for name, spec, version in matches:
                graph.add_dependency(name, version, DependencyType.TRANSITIVE)
            
            logger.info(f"Parsed yarn.lock: {len(graph.nodes)} dependencies")
        except Exception as e:
            logger.error(f"Failed to parse yarn.lock: {e}")
        
        return graph
