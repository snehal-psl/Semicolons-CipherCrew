# Architecture

## System Overview

The CVE Remediation Agent follows a modular architecture designed for extensibility and maintainability.

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI Interface                           │
│              (cli.py - scan, remediate, batch)              │
└──────────┬────────────────────────────────────────────┬─────┘
           │                                            │
    ┌──────▼──────┐                            ┌──────▼──────┐
    │   Detection │                            │  Dependency │
    │   Module    │                            │    Graph    │
    │             │                            │   Module    │
    │ - Scanner   │                            │             │
    │ - NVD API   │                            │ - npm       │
    │ - OSV API   │                            │ - pip       │
    │ - CVE Data  │                            │ - Maven     │
    └──────┬──────┘                            │ - Gradle    │
           │                                  └──────┬──────┘
           │         ┌───────────────────────────────┼────────┐
           └────────▶│      Upgrade Module           │        │
                     │                               │        │
                     │ - Version Resolver            │        │
                     │ - Changelog Analysis          │        │
                     │ - Conflict Resolution         │        │
                     │ - AI Integration (Phase 2)    │        │
                     │                               │        │
                     └──────────────────┬────────────┘        │
                                        │                     │
                    ┌───────────────────▼─────────────────┐   │
                    │       PR Generation                 │   │
                    │                                     │   │
                    │ - PR Builder                       │   │
                    │ - Risk Assessment                  │   │
                    │ - Formatting                       │   │
                    └──────────────┬──────────────────────┘   │
                                   │                          │
                    ┌──────────────▼────────────────────┐     │
                    │      Git Integration              │     │
                    │                                  │     │
                    │ - GitHub API Client              │     │
                    │ - Branch Management              │     │
                    │ - PR Operations                  │     │
                    │ - Approval Workflows             │     │
                    └──────────────┬───────────────────┘     │
                                   │                         │
                    ┌──────────────▼────────────────────┐    │
                    │      Validation Module            │    │
                    │                                  │    │
                    │ - Test Execution                │    │
                    │ - Result Analysis               │    │
                    │ - Confidence Scoring            │    │
                    └──────────────────────────────────┘    │
                                                            │
                    ┌───────────────────────────────────────┘
                    │
           ┌────────▼────────┐
           │  Utils & Config │
           │                 │
           │ - CLI utils     │
           │ - Config mgmt   │
           │ - Logging       │
           └─────────────────┘
```

## Core Modules

### 1. Detection Module (`src/detection/`)

**Purpose**: Multi-source CVE detection and data aggregation

**Components**:
- **Vulnerability**: Data model with CVSS/EPSS scoring
- **NVDClient**: Integration with National Vulnerability Database
- **OSVClient**: Integration with Open Source Vulnerabilities database
- **Scanner**: Orchestrates detection across sources

**Flow**:
1. Scanner queries both NVD and OSV APIs
2. Results are deduplicated by CVE ID
3. Vulnerabilities filtered by severity threshold
4. Returns aggregated list with merged metadata

**Key Classes**:
```python
class Vulnerability:
    - cve_id: str
    - package_name: str
    - ecosystem: str
    - affected_versions: List[str]
    - fixed_versions: List[str]
    - severity: CVESeverity
    - cvss: Optional[CVSS]
    - epss_score: Optional[float]

class Scanner:
    - scan_package(package, ecosystem, version) -> ScanResult
    - scan_packages(packages) -> List[ScanResult]
```

### 2. Dependency Graph Module (`src/dependency_graph/`)

**Purpose**: Multi-language dependency parsing and graph analysis

**Components**:
- **DependencyGraph**: Graph data structure (nodes, edges)
- **NPMParser**: Parses npm package-lock.json (v1/v2/v3), yarn.lock
- **PythonParser**: Parses requirements.txt, setup.py, poetry.lock
- **MavenParser**: Parses pom.xml files
- **GradleParser**: Parses build.gradle files

**Features**:
- Transitive dependency resolution
- Conflict detection (multiple versions of same package)
- Impact analysis (which packages are affected by vulnerability)
- Circular dependency detection (future)

**Key Classes**:
```python
class DependencyGraph:
    - add_dependency(name, version, type)
    - add_edge(source, target, spec)
    - get_transitive_deps(package)
    - find_conflicting_requirements()
    - affected_by_vulnerability(package, versions)
```

### 3. Upgrade Module (`src/upgrade/`)

**Purpose**: Intelligent version resolution and conflict handling

**Components** (Phase 2):
- **VersionResolver**: Finds compatible upgrade versions
- **ChangelogAnalyzer**: Detects breaking changes (AI-powered)
- **ConflictResolver**: Handles diamond dependencies

**Strategy**:
1. For each vulnerable package:
   - Find all fixed versions
   - Filter by compatibility with constraints
   - Rank by stability/recency
   - Analyze changelog for breaking changes
2. Resolve conflicts between requirements
3. Validate final set of versions

### 4. PR Generation Module (`src/pr_generation/`)

**Purpose**: Build and format remediation pull requests

**Components**:
- **RemediationPR**: Data model for PR content
- **PRBuilder**: Constructs PR with risk assessment

**Features**:
- Groups related CVE fixes
- Assesses risk level (patch/minor/major)
- Formats description with CVE details
- Assigns appropriate labels and approvers
- Creates branch name based on CVE ID

### 5. Git Integration Module (`src/git/`)

**Purpose**: GitHub API integration

**Components** (Phase 3):
- **GitHubClient**: Wraps GitHub API

**Operations**:
- Create/delete branches
- Create/merge pull requests
- Commit file changes
- Manage labels and assignees
- Check approval workflows

### 6. Validation Module (`src/validation/`)

**Purpose**: Test execution and confidence scoring

**Components** (Phase 4):
- **TestRunner**: Executes project tests
- **ConfidenceScorer**: Calculates upgrade confidence

**Confidence Factors**:
- Test pass rate: 40% weight
- Changelog analysis: 30% weight
- Version bump type: 30% weight

## Data Flow

### Scan Workflow

```
User Input (project path)
    ↓
[Detection Module]
    ├─ Parse lock files/manifests
    ├─ Identify packages + versions
    ├─ Query OSV API
    ├─ Query NVD API (optional)
    └─ Return: List[Vulnerability]
    ↓
[Dependency Graph Module]
    ├─ Build dependency graph
    ├─ Map vulnerabilities to graph
    ├─ Find affected packages
    └─ Detect conflicts
    ↓
Report: Vulnerabilities + Impact
```

### Remediate Workflow

```
User Input (project path, --auto-pr)
    ↓
[Scan Phase]
    └─ Return: List[Vulnerability]
    ↓
[Upgrade Phase] (Phase 2)
    ├─ For each vulnerability:
    │  ├─ Find compatible versions
    │  ├─ Analyze changelogs
    │  └─ Resolve conflicts
    └─ Return: List[VersionUpgrade]
    ↓
[PR Generation Phase]
    ├─ Update lock files
    ├─ Create PRs with details
    ├─ Assign reviewers
    └─ Return: List[RemediationPR]
    ↓
[Git Integration Phase] (Phase 3)
    ├─ Create branches
    ├─ Push commits
    ├─ Open pull requests
    └─ Set up CI/CD
    ↓
[Validation Phase] (Phase 4)
    ├─ Run tests
    ├─ Score confidence
    ├─ Optional auto-merge (if low-risk)
    └─ Notify teams
    ↓
GitHub: PRs Ready for Review
```

## Configuration

Configuration is managed via `config/agent_config.yaml` with optional local overrides in `config/agent_config.local.yaml`.

**Key Settings**:
- Minimum CVE severity
- Supported ecosystems
- Version update strategy (patch/minor/major)
- Git branch/PR naming patterns
- Test command patterns
- AI model selection
- Team assignments

## Extensibility

### Adding New Ecosystems

1. Create parser in `src/dependency_graph/{ecosystem}_parser.py`
2. Implement parser interface: `parse_manifest(path) -> DependencyGraph`
3. Register in `src/dependency_graph/__init__.py`
4. Add to `config/agent_config.yaml`

### Adding New Detection Sources

1. Create client in `src/detection/{source}_client.py`
2. Implement client interface: `query_package(name, version) -> List[Vulnerability]`
3. Register in `Scanner` class
4. Add to configuration

### Integrating AI/LLMs

1. Create integration in `src/upgrade/llm_integration.py`
2. Use Anthropic or OpenAI SDK
3. Implement prompt templates for specific tasks
4. Add result caching to reduce API calls

## Testing Strategy

- **Unit tests**: Individual components (parsers, clients, models)
- **Integration tests**: Multi-module workflows
- **End-to-end tests**: Full scan/remediate workflows
- **Mocking**: API responses, file I/O
- **Coverage target**: >80%

## Error Handling

- Graceful fallback for failed API calls
- Retry logic with exponential backoff
- Clear error messages and logging
- Partial results when possible
- No silent failures

## Performance Considerations

- Parallel API requests (bounded by rate limits)
- Caching of CVE/changelog data
- Incremental dependency parsing
- Lazy loading of large dependency graphs
- Connection pooling for HTTP clients

## Security

- API keys stored in environment variables (never in code)
- GitHub tokens with minimal required scopes
- Validation of all external inputs
- Safe markdown escaping in PR descriptions
- No execution of external code
- Audit logging of all changes
