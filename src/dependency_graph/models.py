"""Dependency graph data models and analysis."""
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class DependencyType(str, Enum):
    """Type of dependency."""
    DIRECT = "direct"
    TRANSITIVE = "transitive"


@dataclass
class Dependency:
    """A single dependency in the graph."""
    name: str
    ecosystem: str  # npm, pip, maven, etc.
    version: str
    dep_type: DependencyType = DependencyType.DIRECT
    required_by: List[str] = field(default_factory=list)  # List of package names that require this
    
    def __hash__(self):
        """Make hashable for sets."""
        return hash((self.name, self.ecosystem, self.version))
    
    def __eq__(self, other):
        """Equality comparison."""
        if not isinstance(other, Dependency):
            return False
        return (self.name == other.name and 
                self.ecosystem == other.ecosystem and 
                self.version == other.version)
    
    def __str__(self):
        return f"{self.name}@{self.version}"


@dataclass
class DependencyEdge:
    """Edge in the dependency graph."""
    source: str  # Package name that has the dependency
    source_version: str
    target: str  # Package being depended on
    target_version_spec: str  # Version specifier (e.g., "^1.2.0", ">=1.0,<2.0")
    extras: Dict[str, str] = field(default_factory=dict)  # Extra metadata


class DependencyGraph:
    """Graph representation of project dependencies."""
    
    def __init__(self, ecosystem: str, root_package: str = "root"):
        """Initialize dependency graph.
        
        Args:
            ecosystem: Package ecosystem (npm, pip, maven, etc.)
            root_package: Name of root/application package
        """
        self.ecosystem = ecosystem
        self.root_package = root_package
        self.nodes: Dict[str, Dependency] = {}  # {package_name: Dependency}
        self.edges: List[DependencyEdge] = []  # All dependency edges
    
    def add_dependency(
        self,
        name: str,
        version: str,
        dep_type: DependencyType = DependencyType.TRANSITIVE,
    ) -> Dependency:
        """Add a dependency to the graph.
        
        Args:
            name: Package name
            version: Package version
            dep_type: Type of dependency (direct or transitive)
            
        Returns:
            The added Dependency object
        """
        key = name
        if key not in self.nodes:
            self.nodes[key] = Dependency(
                name=name,
                ecosystem=self.ecosystem,
                version=version,
                dep_type=dep_type,
            )
        return self.nodes[key]
    
    def add_edge(
        self,
        source: str,
        source_version: str,
        target: str,
        target_version_spec: str,
    ) -> None:
        """Add a dependency edge (A depends on B).
        
        Args:
            source: Package name that has the dependency
            source_version: Version of source package
            target: Package being depended on
            target_version_spec: Version specifier for target
        """
        edge = DependencyEdge(
            source=source,
            source_version=source_version,
            target=target,
            target_version_spec=target_version_spec,
        )
        self.edges.append(edge)
    
    def get_dependents(self, package_name: str) -> List[Dependency]:
        """Get all packages that depend on the given package.
        
        Args:
            package_name: Package to find dependents of
            
        Returns:
            List of Dependency objects that depend on package_name
        """
        dependents = []
        for edge in self.edges:
            if edge.target == package_name:
                if edge.source in self.nodes:
                    dependents.append(self.nodes[edge.source])
        return dependents
    
    def get_dependencies(self, package_name: str) -> List[Tuple[str, str]]:
        """Get all packages that the given package depends on.
        
        Args:
            package_name: Package to find dependencies of
            
        Returns:
            List of (target_package, version_spec) tuples
        """
        dependencies = []
        for edge in self.edges:
            if edge.source == package_name:
                dependencies.append((edge.target, edge.target_version_spec))
        return dependencies
    
    def get_transitive_deps(self, package_name: str, max_depth: int = 10) -> Set[str]:
        """Get all transitive dependencies of a package.
        
        Args:
            package_name: Root package to find transitive dependencies of
            max_depth: Maximum recursion depth to prevent infinite loops
            
        Returns:
            Set of all transitive dependency package names
        """
        visited = set()
        stack = [(package_name, 0)]
        
        while stack:
            pkg, depth = stack.pop()
            if pkg in visited or depth > max_depth:
                continue
            visited.add(pkg)
            
            for dep_name, _ in self.get_dependencies(pkg):
                if dep_name not in visited:
                    stack.append((dep_name, depth + 1))
        
        visited.discard(package_name)  # Don't include the original package
        return visited
    
    def find_conflicting_requirements(self) -> List[Dict]:
        """Find conflicting dependency version requirements.
        
        This is a simplified conflict detector that identifies when
        multiple packages require incompatible versions of a dependency.
        
        Returns:
            List of conflict dictionaries with 'package' and 'conflicts' keys
        """
        conflicts = []
        package_requirements: Dict[str, Set[str]] = {}
        
        for edge in self.edges:
            pkg = edge.target
            if pkg not in package_requirements:
                package_requirements[pkg] = set()
            package_requirements[pkg].add(edge.target_version_spec)
        
        for pkg, specs in package_requirements.items():
            if len(specs) > 1:
                conflicts.append({
                    "package": pkg,
                    "conflicts": list(specs),
                    "required_by": [e.source for e in self.edges if e.target == pkg],
                })
        
        return conflicts
    
    def affected_by_vulnerability(self, vuln_package: str, vuln_versions: List[str]) -> Set[str]:
        """Find all packages affected by a vulnerability in a dependency.
        
        Args:
            vuln_package: Package with vulnerability
            vuln_versions: Affected version specs
            
        Returns:
            Set of all packages that transitively depend on the vulnerable package
        """
        affected = {vuln_package}
        
        # Find all packages that depend on the vulnerable package
        to_check = [vuln_package]
        checked = set()
        
        while to_check:
            pkg = to_check.pop()
            if pkg in checked:
                continue
            checked.add(pkg)
            
            dependents = self.get_dependents(pkg)
            for dep in dependents:
                affected.add(dep.name)
                to_check.append(dep.name)
        
        return affected
    
    def __str__(self) -> str:
        """String representation."""
        return (
            f"DependencyGraph({self.ecosystem}, "
            f"nodes={len(self.nodes)}, edges={len(self.edges)})"
        )
