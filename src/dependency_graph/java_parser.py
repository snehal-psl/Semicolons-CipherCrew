"""Maven/Gradle dependency parser for Java projects."""
import logging
import xml.etree.ElementTree as ET
from typing import Optional, Dict
from pathlib import Path

from .models import DependencyGraph, DependencyType

logger = logging.getLogger(__name__)


class MavenParser:
    """Parser for Maven pom.xml files."""
    
    @staticmethod
    def parse_pom_xml(pom_file_path: str) -> DependencyGraph:
        """Parse Maven pom.xml file.
        
        Args:
            pom_file_path: Path to pom.xml
            
        Returns:
            DependencyGraph representation
            
        Raises:
            FileNotFoundError: If pom.xml doesn't exist
            ET.ParseError: If XML is invalid
        """
        tree = ET.parse(pom_file_path)
        root = tree.getroot()
        
        # Handle Maven namespace
        namespace = {"m": "http://maven.apache.org/POM/4.0.0"}
        
        graph = DependencyGraph(ecosystem="maven")
        
        # Extract root package info
        project_name_elem = root.find("m:artifactId", namespace)
        if project_name_elem is None:
            project_name_elem = root.find("artifactId")
        graph.root_package = project_name_elem.text if project_name_elem is not None else "root"
        
        # Parse dependencies
        deps_elem = root.find("m:dependencies", namespace)
        if deps_elem is None:
            deps_elem = root.find("dependencies")
        
        if deps_elem is not None:
            for dep in deps_elem.findall("m:dependency", namespace):
                if dep is None:
                    dep = deps_elem.find("dependency")
                
                artifact_id = dep.find("m:artifactId", namespace) or dep.find("artifactId")
                group_id = dep.find("m:groupId", namespace) or dep.find("groupId")
                version = dep.find("m:version", namespace) or dep.find("version")
                scope = dep.find("m:scope", namespace) or dep.find("scope")
                
                if artifact_id is not None and group_id is not None:
                    # Create qualified name
                    pkg_name = f"{group_id.text}:{artifact_id.text}"
                    pkg_version = version.text if version is not None else "*"
                    scope_val = scope.text if scope is not None else "compile"
                    
                    dep_type = DependencyType.DIRECT if scope_val == "compile" else DependencyType.TRANSITIVE
                    graph.add_dependency(pkg_name, pkg_version, dep_type)
                    graph.add_edge(graph.root_package, "", pkg_name, pkg_version)
        
        logger.info(f"Parsed pom.xml: {len(graph.nodes)} dependencies")
        return graph


class GradleParser:
    """Parser for Gradle build.gradle files (simplified)."""
    
    @staticmethod
    def parse_build_gradle(build_file_path: str) -> DependencyGraph:
        """Parse Gradle build.gradle file (simplified parser).
        
        Args:
            build_file_path: Path to build.gradle
            
        Returns:
            DependencyGraph representation
            
        Note:
            This is a simplified regex-based parser. Full Gradle parsing
            would require evaluating Groovy/Kotlin DSL.
        """
        import re
        
        graph = DependencyGraph(ecosystem="gradle")
        
        try:
            with open(build_file_path, 'r') as f:
                content = f.read()
            
            # Remove comments
            content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
            content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
            
            # Extract dependencies block
            dep_pattern = r'dependencies\s*\{(.*?)\}'
            dep_match = re.search(dep_pattern, content, re.DOTALL)
            
            if dep_match:
                deps_block = dep_match.group(1)
                
                # Parse individual dependency lines
                # Patterns: 'implementation "group:artifact:version"' or variations
                dep_line_pattern = r'(?:implementation|compile|api|testImplementation)\s+["\']([^":]+):([^":]+):([^"\']+)["\']'
                matches = re.findall(dep_line_pattern, deps_block)
                
                for group_id, artifact_id, version in matches:
                    pkg_name = f"{group_id}:{artifact_id}"
                    graph.add_dependency(pkg_name, version, DependencyType.DIRECT)
                    graph.add_edge(graph.root_package, "", pkg_name, version)
            
            logger.info(f"Parsed build.gradle: {len(graph.nodes)} dependencies")
        except Exception as e:
            logger.error(f"Failed to parse build.gradle: {e}")
        
        return graph
