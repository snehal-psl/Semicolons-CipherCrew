# Autonomous AI CVE Remediation Agent

An autonomous agent that detects critical vulnerabilities (CVEs) in project dependencies, intelligently resolves version conflicts, and generates pull requests for remediation.

## Features

- **Multi-Ecosystem Support**: npm, pip, Maven, Gradle, and more
- **Intelligent CVE Detection**: Integration with OSV and NVD for comprehensive vulnerability data
- **Transitive Dependency Analysis**: Identifies vulnerabilities in indirect dependencies
- **AI-Powered Version Resolution**: Uses LLMs to determine compatible upgrade versions
- **Conflict Resolution**: Handles diamond dependencies and pinning constraints
- **Automated Testing**: Validates upgrades against existing test suites
- **GitHub Integration**: Automatic PR generation and workflow integration
- **Detailed Reporting**: CVSS scores, EPSS exploitation probability, and risk assessment

## Quick Start

### Installation

```bash
git clone https://github.com/your-org/cve-remediation-agent.git
cd cve-remediation-agent
pip install -e .
```

### Configuration

Create a `.env` file with your API keys:

```env
ANTHROPIC_API_KEY=sk-ant-...
GITHUB_TOKEN=ghp_...
NVD_API_KEY=...
```

Copy and customize `config/agent_config.yaml`:

```bash
cp config/agent_config.yaml config/agent_config.local.yaml
# Edit config/agent_config.local.yaml with your preferences
```

### Running the Agent

```bash
# Scan a single project
cve-agent scan /path/to/project

# Scan and generate remediation PRs
cve-agent remediate /path/to/project --auto-pr

# Batch scan multiple repositories
cve-agent batch --repos repo1,repo2,repo3
```

## Architecture

### Core Modules

- **`detection/`**: CVE detection from OSV and NVD APIs
- **`dependency_graph/`**: Multi-language dependency parsing (npm, pip, Maven, Gradle)
- **`upgrade/`**: AI-powered version resolution and conflict handling
- **`pr_generation/`**: PR creation and formatting
- **`git/`**: GitHub API integration for branch/PR operations
- **`validation/`**: Test execution and confidence scoring

### Workflow

```
1. Scan Dependencies
   └─ Parse lock files/manifests
   └─ Identify all packages (direct + transitive)

2. Detect Vulnerabilities
   └─ Query OSV/NVD for CVEs
   └─ Filter by severity & exploitability
   └─ Deduplicate results

3. Analyze Impact
   └─ Build dependency graph
   └─ Identify affected packages
   └─ Find version conflicts

4. Resolve Versions
   └─ AI determines compatible upgrades
   └─ Analyze changelogs for breaking changes
   └─ Validate against constraints

5. Update & Test
   └─ Update lock files
   └─ Run test suite
   └─ Capture results

6. Generate PR
   └─ Format PR with details
   └─ Add risk assessment
   └─ Request appropriate approvers

7. Monitor & Report
   └─ Track PR status
   └─ Log results
   └─ Notify stakeholders
```

## Configuration

See `config/agent_config.yaml` for all options:

- **Detection settings**: CVE sources, minimum severity, transitive scanning
- **Version strategy**: patch/minor/major update preferences
- **Git integration**: Branch naming, auto-merge policies, approval requirements
- **Testing**: Test command patterns, pass rate thresholds
- **AI/LLM**: Model selection, temperature, token limits
- **Notifications**: Slack, email, GitHub integration

## Development

### Setup Dev Environment

```bash
pip install -e ".[dev]"
pre-commit install
```

### Running Tests

```bash
pytest tests/ -v --cov=src
```

### Code Quality

```bash
black src/
flake8 src/
mypy src/
isort src/
```

## Roadmap

### Phase 1 (Complete)
- CVE detection (NVD, OSV)
- Dependency parsing (npm, pip, Maven, Gradle)
- Basic dependency graph analysis

### Phase 2 (In Progress)
- AI-powered version resolution
- Changelog analysis
- Conflict resolution

### Phase 3
- GitHub Actions integration
- Automated testing
- Confidence scoring

### Phase 4
- Docker image scanning
- Private package registry support
- Multi-repo orchestration

### Phase 5
- Advanced analytics and ML-based predictions
- Integration with more CI/CD platforms
- Enterprise features

## Limitations & Known Issues

- Dependency parsing is simplified for Maven/Gradle (doesn't handle complex Groovy/Kotlin DSL)
- yarn.lock v1 parser is basic (v2/v3 support coming)
- Test suite discovery is ecosystem-specific and may not work for all project structures
- No support for private package registries initially

## Security Considerations

- Store API keys in environment variables, not in config files
- Use GitHub token with minimal required scopes
- Enable PR approval requirements for production use
- Audit generated PRs before merging
- Implement rollback procedures

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - See LICENSE file

## Support

- Issues: [GitHub Issues](https://github.com/your-org/cve-remediation-agent/issues)
- Discussions: [GitHub Discussions](https://github.com/your-org/cve-remediation-agent/discussions)
- Email: security@your-org.com
