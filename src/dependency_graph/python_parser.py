"""Python package dependency parser (pip, poetry, requirements)."""
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import re

from .models import DependencyGraph, DependencyType

logger = logging.getLogger(__name__)


class PythonParser:
    """Parser for Python dependency files (pip, poetry, etc.)."""
    
    @staticmethod
    def parse_poetry_lock(lock_file_path: str) -> DependencyGraph:
        """Parse poetry.lock file (TOML format).
        
        Args:
            lock_file_path: Path to poetry.lock
            
        Returns:
            DependencyGraph representation
            
        Raises:
            ImportError: If toml library not available
        """
        try:
            import toml
        except ImportError:
            logger.error("toml library required for poetry.lock parsing")
            return DependencyGraph(ecosystem="pip")
        
        with open(lock_file_path, 'r') as f:
            lock_data = toml.load(f)
        
        graph = DependencyGraph(ecosystem="pip")
        
        # Parse packages
        packages = lock_data.get("package", [])
        if isinstance(packages, dict):
            packages = [packages]
        
        for pkg in packages:
            name = pkg.get("name", "")
            version = pkg.get("version", "")
            
            if name:
                graph.add_dependency(name, version, DependencyType.TRANSITIVE)
        
        # Parse dependencies between packages
        for i, pkg in enumerate(packages):
            source_name = pkg.get("name", "")
            source_version = pkg.get("version", "")
            
            for dep_name, dep_spec in pkg.get("dependencies", {}).items():
                if isinstance(dep_spec, dict):
                    dep_version = dep_spec.get("version", "*")
                else:
                    dep_version = str(dep_spec)
                
                graph.add_edge(source_name, source_version, dep_name, dep_version)
        
        logger.info(f"Parsed poetry.lock: {len(graph.nodes)} dependencies")
        return graph
    
    @staticmethod
    def parse_requirements_txt(file_path: str) -> DependencyGraph:
        """Parse requirements.txt file.
        
        Args:
            file_path: Path to requirements.txt
            
        Returns:
            DependencyGraph representation
        """
        graph = DependencyGraph(ecosystem="pip", root_package="app")
        
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Skip extras syntax like "package[extra]"
                pkg_spec = line.split('[')[0].strip()
                
                # Parse package name and version
                name, version = PythonParser._parse_requirement_line(pkg_spec)
                if name:
                    graph.add_dependency(name, version or "*", DependencyType.DIRECT)
                    graph.add_edge("root", "", name, version or "*")
            
            logger.info(f"Parsed requirements.txt: {len(graph.nodes)} dependencies")
        except Exception as e:
            logger.error(f"Failed to parse requirements.txt: {e}")
        
        return graph
    
    @staticmethod
    def parse_setup_py(file_path: str) -> DependencyGraph:
        """Parse setup.py file (simplified, extracts install_requires).
        
        Args:
            file_path: Path to setup.py
            
        Returns:
            DependencyGraph representation
            
        Note:
            This is a simplified parser using regex. Full evaluation would require
            executing Python, which is a security risk.
        """
        graph = DependencyGraph(ecosystem="pip", root_package="app")
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Extract install_requires list
            pattern = r'install_requires\s*=\s*\[(.*?)\]'
            match = re.search(pattern, content, re.DOTALL)
            
            if match:
                requires_str = match.group(1)
                # Split by comma and process each requirement
                for req in requires_str.split(','):
                    req = req.strip().strip('\'"')
                    if req:
                        name, version = PythonParser._parse_requirement_line(req)
                        if name:
                            graph.add_dependency(name, version or "*", DependencyType.DIRECT)
                            graph.add_edge("root", "", name, version or "*")
            
            logger.info(f"Parsed setup.py: {len(graph.nodes)} dependencies")
        except Exception as e:
            logger.error(f"Failed to parse setup.py: {e}")
        
        return graph
    
    @staticmethod
    def _parse_requirement_line(line: str) -> Tuple[Optional[str], Optional[str]]:
        """Parse a single requirement line (e.g., "django>=3.0,<4.0").
        
        Args:
            line: Requirement specification
            
        Returns:
            Tuple of (package_name, version_spec) or (None, None)
        """
        # Remove whitespace
        line = line.strip()
        if not line:
            return None, None
        
        # Match package name and version specifier
        # Package names can contain alphanumeric, hyphens, underscores, dots
        match = re.match(r'^([a-zA-Z0-9._-]+)\s*([<>=!~\d\.,\s]*)$', line)
        
        if match:
            name = match.group(1).lower().replace('_', '-')
            version = match.group(2).strip() or None
            return name, version
        
        return None, None
