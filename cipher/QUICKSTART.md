# Quick Start Guide - CVE Remediation Agent

## Prerequisites

- Python 3.9 or later
- pip package manager
- Git
- GitHub account with personal access token

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/cve-remediation-agent.git
   cd cve-remediation-agent
   ```

2. **Create Python virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -e .
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Configure the agent** (optional)
   ```bash
   cp config/agent_config.yaml config/agent_config.local.yaml
   # Edit to customize settings
   ```

## Running the Agent

### Scan a project for vulnerabilities

```bash
cve-agent scan /path/to/project --min-severity CRITICAL
```

### Scan and generate remediation PRs (requires GitHub setup)

```bash
cve-agent remediate /path/to/project --auto-pr
```

### Batch scan multiple repositories

```bash
cve-agent batch --repos /path/repo1,/path/repo2,/path/repo3
```

### Show version

```bash
cve-agent version
```

## Development

### Run tests

```bash
pytest tests/ -v --cov=src
```

### Format code

```bash
black src/ tests/
isort src/ tests/
```

### Type checking

```bash
mypy src/ --ignore-missing-imports
```

### Lint

```bash
flake8 src/ tests/
```

## Project Structure

- **src/detection/**: CVE vulnerability detection (NVD, OSV APIs)
- **src/dependency_graph/**: Dependency file parsing (npm, pip, Maven, Gradle)
- **src/upgrade/**: Version resolution and conflict handling
- **src/pr_generation/**: PR generation and formatting
- **src/git/**: GitHub API integration
- **src/validation/**: Testing and confidence scoring
- **config/**: Configuration files
- **tests/**: Unit and integration tests

## Next Steps

1. Set up your API keys in `.env`
2. Try scanning a sample project: `cve-agent scan .`
3. Review the Phase 2 roadmap for upcoming features (LLM integration, advanced version resolution)
4. Read [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines

## Troubleshooting

### "Module not found" errors
- Ensure virtual environment is activated
- Run `pip install -e .` again

### API rate limits
- OSV: 10 requests/minute (free)
- NVD: 5 requests/minute (free), higher with API key
- Set `NVD_API_KEY` in `.env` for higher limits

### GitHub authentication failures
- Verify `GITHUB_TOKEN` is set and has correct scopes
- Required scopes: `repo`, `read:org`, `workflow`

## Support

- Issues: [GitHub Issues](https://github.com/your-org/cve-remediation-agent/issues)
- Documentation: See [README.md](README.md)
- Contributing: See [CONTRIBUTING.md](CONTRIBUTING.md)
