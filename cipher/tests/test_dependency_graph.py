"""Tests for dependency graph module."""
import pytest
import json
import tempfile
from pathlib import Path

from src.dependency_graph import (
    DependencyGraph,
    Dependency,
    DependencyType,
    NPMParser,
    PythonParser,
)


class TestDependencyGraph:
    """Test DependencyGraph functionality."""
    
    def test_graph_creation(self):
        """Test creating a dependency graph."""
        graph = DependencyGraph(ecosystem="npm", root_package="my-app")
        
        assert graph.ecosystem == "npm"
        assert graph.root_package == "my-app"
        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0
    
    def test_add_dependency(self):
        """Test adding dependencies to graph."""
        graph = DependencyGraph(ecosystem="npm")
        
        dep = graph.add_dependency("lodash", "4.17.21")
        
        assert "lodash" in graph.nodes
        assert graph.nodes["lodash"].version == "4.17.21"
    
    def test_add_edge(self):
        """Test adding dependency edges."""
        graph = DependencyGraph(ecosystem="npm")
        
        graph.add_dependency("app", "1.0.0", DependencyType.DIRECT)
        graph.add_dependency("lodash", "4.17.21")
        graph.add_edge("app", "1.0.0", "lodash", "^4.17.0")
        
        assert len(graph.edges) == 1
        assert graph.edges[0].source == "app"
        assert graph.edges[0].target == "lodash"
    
    def test_get_dependencies(self):
        """Test retrieving dependencies."""
        graph = DependencyGraph(ecosystem="npm")
        
        graph.add_dependency("app", "1.0.0")
        graph.add_dependency("lodash", "4.17.21")
        graph.add_dependency("moment", "2.29.0")
        
        graph.add_edge("app", "1.0.0", "lodash", "^4.17.0")
        graph.add_edge("app", "1.0.0", "moment", "^2.29.0")
        
        deps = graph.get_dependencies("app")
        
        assert len(deps) == 2
        assert ("lodash", "^4.17.0") in deps
        assert ("moment", "^2.29.0") in deps
    
    def test_get_transitive_deps(self):
        """Test transitive dependency resolution."""
        graph = DependencyGraph(ecosystem="npm")
        
        graph.add_dependency("app", "1.0.0")
        graph.add_dependency("express", "4.17.1")
        graph.add_dependency("body-parser", "1.19.0")
        graph.add_dependency("bytes", "3.1.0")
        
        graph.add_edge("app", "1.0.0", "express", "^4.17.0")
        graph.add_edge("express", "4.17.1", "body-parser", "1.19.0")
        graph.add_edge("body-parser", "1.19.0", "bytes", "3.1.0")
        
        transitive = graph.get_transitive_deps("app")
        
        assert "express" in transitive
        assert "body-parser" in transitive
        assert "bytes" in transitive
    
    def test_conflict_detection(self):
        """Test finding conflicting dependencies."""
        graph = DependencyGraph(ecosystem="npm")
        
        graph.add_dependency("app", "1.0.0")
        graph.add_dependency("lodash", "4.17.21")
        graph.add_dependency("pkg1", "1.0.0")
        graph.add_dependency("pkg2", "1.0.0")
        
        # Both pkg1 and pkg2 depend on lodash but with different versions
        graph.add_edge("pkg1", "1.0.0", "lodash", "^4.15.0")
        graph.add_edge("pkg2", "1.0.0", "lodash", "^4.17.0")
        
        conflicts = graph.find_conflicting_requirements()
        
        # At least lodash should be in conflicts
        conflict_pkgs = [c["package"] for c in conflicts]
        assert "lodash" in conflict_pkgs


class TestNPMParser:
    """Test npm lock file parser."""
    
    def test_parse_package_lock_v2(self):
        """Test parsing npm package-lock.json v2."""
        lock_data = {
            "lockfileVersion": 2,
            "name": "my-app",
            "packages": {
                "": {
                    "name": "my-app",
                    "version": "1.0.0",
                    "dependencies": {
                        "lodash": "^4.17.21"
                    }
                },
                "node_modules/lodash": {
                    "name": "lodash",
                    "version": "4.17.21"
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(lock_data, f)
            lock_file = f.name
        
        try:
            graph = NPMParser.parse_package_lock(lock_file)
            
            assert graph.ecosystem == "npm"
            assert "lodash" in graph.nodes
        finally:
            Path(lock_file).unlink()


class TestPythonParser:
    """Test Python dependency parser."""
    
    def test_parse_requirements_txt(self):
        """Test parsing requirements.txt."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("django>=3.0,<4.0\n")
            f.write("# Comment\n")
            f.write("requests>=2.25.0\n")
            f.write("\n")  # Empty line
            f.write("pytest\n")
            req_file = f.name
        
        try:
            graph = PythonParser.parse_requirements_txt(req_file)
            
            assert graph.ecosystem == "pip"
            assert "django" in graph.nodes
            assert "requests" in graph.nodes
            assert "pytest" in graph.nodes
        finally:
            Path(req_file).unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
