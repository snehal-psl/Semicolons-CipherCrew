# Development Checklist - CVE Remediation Agent

Use this checklist to ensure all setup steps are complete before starting development.

## ✅ Environment Setup

- [ ] Python 3.9+ installed
- [ ] Git installed and configured
- [ ] Project cloned from repository
- [ ] Virtual environment created: `python -m venv venv`
- [ ] Virtual environment activated: `source venv/bin/activate`
- [ ] Dependencies installed: `pip install -e ".[dev]"`

## ✅ Configuration

- [ ] `.env` file created from `.env.example`
- [ ] `ANTHROPIC_API_KEY` added to `.env` (if using Phase 2 features)
- [ ] `GITHUB_TOKEN` added to `.env` (if using GitHub integration)
- [ ] `config/agent_config.yaml` reviewed and customized
- [ ] Logging level set in config or environment

## ✅ IDE Setup

- [ ] VS Code installed
- [ ] Workspace opened in VS Code
- [ ] Recommended extensions installed (via `.vscode/extensions.json`)
- [ ] Python interpreter selected (pointing to venv)
- [ ] PyLance/Pylance activated
- [ ] Code formatting configured (Black)

## ✅ Code Quality

- [ ] Ran Black formatter: `black src/ tests/`
- [ ] Ran isort: `isort src/ tests/`
- [ ] Ran flake8 linter: `flake8 src/ tests/`
- [ ] Ran mypy type checker: `mypy src/ --ignore-missing-imports`
- [ ] No linting errors or warnings

## ✅ Testing

- [ ] Tests discovered and working: `pytest tests/ --collect-only`
- [ ] All tests passing: `pytest tests/ -v`
- [ ] Coverage report generated: `pytest tests/ --cov=src`
- [ ] Coverage above 80%
- [ ] Individual test files run: `pytest tests/test_detection.py -v`

## ✅ CLI

- [ ] CLI commands discovered: `cve-agent --help`
- [ ] Version command works: `cve-agent version`
- [ ] Scan command available: `cve-agent scan --help`
- [ ] Batch command available: `cve-agent batch --help`
- [ ] Remediate command available: `cve-agent remediate --help`

## ✅ Documentation

- [ ] README.md reviewed
- [ ] QUICKSTART.md completed
- [ ] CONTRIBUTING.md read
- [ ] ARCHITECTURE.md understood
- [ ] ROADMAP.md reviewed for phases
- [ ] PROJECT_STRUCTURE.md reviewed

## ✅ Version Control

- [ ] `.gitignore` prevents committing secrets
- [ ] `.env` file not committed
- [ ] No API keys in code
- [ ] Pre-commit hooks installed (optional): `pre-commit install`

## ✅ Docker

- [ ] Docker installed
- [ ] Dockerfile reviewed
- [ ] Docker image builds: `docker build -t cve-agent:latest .`
- [ ] Docker Compose installed
- [ ] docker-compose.yml reviewed
- [ ] Container runs: `docker-compose up`

## ✅ GitHub

- [ ] Repository forked (if contributing)
- [ ] Branch naming convention understood
- [ ] Issue templates reviewed
- [ ] PR template reviewed
- [ ] GitHub Actions workflows examined

## ✅ First Development Task

### For Phase 1 (Foundation)
- [ ] Run scan on this project: `cve-agent scan .`
- [ ] Review output and understand data structure
- [ ] Examine a parser (e.g., `npm_parser.py`)
- [ ] Look at test examples
- [ ] Read through a module (e.g., `detection/scanner.py`)

### For Phase 2 (AI Integration)
- [ ] Review upgrade module structure
- [ ] Read LLM integration design in ARCHITECTURE.md
- [ ] Set up Anthropic API key
- [ ] Review version resolution requirements in ROADMAP.md
- [ ] Plan first task from Phase 2 work items

### For Phase 3 (GitHub Integration)
- [ ] Review git module structure
- [ ] Set up GitHub personal access token
- [ ] Review GitHub API design in ARCHITECTURE.md
- [ ] Check GitHub Actions workflow setup
- [ ] Plan PR creation workflow

## ✅ Development Workflow

Before each coding session:
- [ ] Activate virtual environment
- [ ] Check for new documentation in `docs/` (if exists)
- [ ] Review task description
- [ ] Create feature branch: `git checkout -b feature/description`

After coding:
- [ ] Format code: `black src/ tests/`
- [ ] Run linter: `flake8 src/ tests/`
- [ ] Run type checker: `mypy src/`
- [ ] Run tests: `pytest tests/ -v --cov=src`
- [ ] Commit changes with meaningful message
- [ ] Push to fork: `git push origin feature/description`
- [ ] Create PR with template

## ✅ Common Tasks

### Adding a New Parser
- [ ] Create file: `src/dependency_graph/x_parser.py`
- [ ] Implement parser class
- [ ] Add to `__init__.py` exports
- [ ] Add tests in `tests/test_dependency_graph.py`
- [ ] Update configuration in `config/agent_config.yaml`
- [ ] Update README.md with new ecosystem

### Adding a New Module
- [ ] Create directory: `src/new_module/`
- [ ] Create `__init__.py` with public API
- [ ] Create implementation files
- [ ] Create corresponding tests: `tests/test_new_module.py`
- [ ] Add docstrings to all public functions
- [ ] Update ARCHITECTURE.md
- [ ] Update imports in main modules if needed

### Adding a CLI Command
- [ ] Update `src/cli.py` with new subparser
- [ ] Implement command handler function
- [ ] Add help text and arguments
- [ ] Test command: `cve-agent new-command --help`
- [ ] Add command to documentation
- [ ] Create test for new command

### Debugging
- [ ] Use VS Code debugger: `launch.json` configurations
- [ ] Set breakpoints and inspect variables
- [ ] Use print debugging as fallback
- [ ] Check logs: `logs/cve-agent.log`
- [ ] Increase log level: `export LOG_LEVEL=DEBUG`

## ✅ Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Module not found | Ensure venv activated, `pip install -e .` |
| Tests fail | Check Python version (3.9+), run `pip install -e ".[dev]"` |
| Black reformats differently | Update Black: `pip install --upgrade black` |
| Type checking fails | Ignore missing imports: `mypy src/ --ignore-missing-imports` |
| API rate limits | Add API keys to `.env`, implement caching |
| Docker build fails | Ensure Dockerfile in project root, check Python version |
| GitHub token errors | Verify token, check scopes: repo, read:org, workflow |

## 📚 Helpful Commands Reference

```bash
# Development
python -m venv venv                      # Create virtual env
source venv/bin/activate                # Activate venv (Windows: venv\Scripts\activate)
pip install -e ".[dev]"                 # Install dev dependencies

# Code Quality
black src/ tests/                        # Format code
isort src/ tests/                        # Sort imports
flake8 src/ tests/                       # Lint
mypy src/                                # Type check

# Testing
pytest tests/ -v                         # Run all tests verbose
pytest tests/ -v --cov=src               # Run with coverage
pytest tests/test_detection.py::TestVulnerability::test_vulnerability_creation
                                          # Run specific test

# CLI
cve-agent version                        # Show version
cve-agent scan /path                     # Scan project
cve-agent scan /path --min-severity HIGH # Scan with filter

# Git
git checkout -b feature/description      # Create feature branch
git add src/                             # Stage changes
git commit -m "type: description"        # Commit
git push origin feature/description      # Push

# Docker
docker build -t cve-agent:latest .       # Build image
docker run cve-agent:latest scan .       # Run scan
docker-compose up                        # Start dev env

# Documentation
cat README.md                            # View main docs
cat QUICKSTART.md                        # View quick start
cat CONTRIBUTING.md                      # View contributing guide
```

## 🎯 Ready to Start?

1. **First Time Setup**: Follow Environment Setup section ✅
2. **Before First Code Change**: Complete Code Quality section ✅
3. **Before First PR**: Complete all sections ✅
4. **Regular Development**: Just complete Development Workflow section ✅

## 📖 Reference Docs

- [README.md](README.md) - Project overview
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [ROADMAP.md](ROADMAP.md) - Implementation timeline
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - File structure
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment

---

**Status**: Use this checklist before starting development
**Last Updated**: May 13, 2026
**Questions**: See CONTRIBUTING.md for support
