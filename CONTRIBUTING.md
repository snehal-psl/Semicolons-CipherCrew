# Contributing to CVE Remediation Agent

Thank you for interest in contributing! This document provides guidelines for development.

## Development Setup

### 1. Fork and Clone

```bash
git clone https://github.com/your-org/cve-remediation-agent.git
cd cve-remediation-agent
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Development Dependencies

```bash
pip install -e ".[dev]"
```

### 4. Set Up Pre-commit Hooks (Optional)

```bash
pip install pre-commit
pre-commit install
```

## Code Style

### Python Style Guide

- Follow **PEP 8** with modifications:
  - Line length: 100 characters (not 79)
  - Use type hints for all public functions
- Use **Black** for formatting: `black src/ tests/`
- Use **isort** for import ordering: `isort src/ tests/`
- Check with **flake8**: `flake8 src/ tests/`
- Type check with **mypy**: `mypy src/ --ignore-missing-imports`

### Docstrings

Use Google-style docstrings:

```python
def example_function(param1: str, param2: int) -> bool:
    """Brief description of the function.

    Longer description if needed, explaining the behavior,
    parameters, and return value.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When something is wrong
    """
```

## Testing

### Writing Tests

- Write tests for all new functionality
- Place tests in `tests/` directory
- Use pytest: `pytest tests/ -v`
- Aim for >80% code coverage: `pytest tests/ --cov=src`

### Test Structure

```python
class TestMyFeature:
    """Test cases for MyFeature."""

    def test_basic_functionality(self):
        """Test basic functionality."""
        # Arrange
        obj = MyClass()

        # Act
        result = obj.method()

        # Assert
        assert result == expected_value
```

## Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/short-description
```

Branch naming:
- `feature/description` - New feature
- `fix/description` - Bug fix
- `docs/description` - Documentation
- `refactor/description` - Code refactoring
- `test/description` - Test additions

### 2. Make Changes

- Keep commits small and focused
- Write meaningful commit messages
- Follow the format: `type: description`

### 3. Run Quality Checks

```bash
# Format code
black src/ tests/
isort src/ tests/

# Lint
flake8 src/ tests/

# Type check
mypy src/ --ignore-missing-imports

# Run tests
pytest tests/ -v --cov=src
```

### 4. Create Pull Request

- Reference issues: "Fixes #123"
- Describe changes clearly
- Include test results
- Request review from maintainers

## Project Structure

```
src/
├── detection/       # CVE detection logic
├── dependency_graph/  # Dependency parsing
├── upgrade/         # Version resolution
├── pr_generation/   # PR formatting
├── git/            # GitHub integration
├── validation/     # Testing & scoring
├── cli.py          # CLI interface
└── utils.py        # Utilities

tests/
├── test_detection.py
├── test_dependency_graph.py
└── ...
```

## Phases & Priorities

### Phase 1 (Foundation) - COMPLETE
- CVE detection infrastructure
- Dependency parsing
- Graph analysis

### Phase 2 (AI & Resolution) - IN PROGRESS
- LLM-based version resolution
- Changelog analysis
- Conflict resolution
- **Good for contributions**: Implement `VersionResolver`, changelog parsing

### Phase 3 (GitHub Integration)
- PR creation/merging
- GitHub Actions
- **Good for contributions**: Complete `GitHubClient`, workflow integration

### Phase 4 (Validation)
- Test execution
- Confidence scoring
- **Good for contributions**: Implement `TestRunner`, scoring logic

## Good First Issues

- Add more ecosystem parsers (Go, Rust, PHP)
- Improve error handling in parsers
- Add more test cases
- Improve documentation
- Add CLI flags and options
- Implement simple features in Phase 2

## Code Review

We use the following review criteria:

- ✅ Code follows style guide (black, flake8, mypy)
- ✅ Tests cover new functionality (>80% coverage)
- ✅ Documentation is clear and complete
- ✅ No breaking changes without discussion
- ✅ Commits are well-organized
- ✅ CI/CD passes all checks

## Getting Help

- Issues: Use GitHub Issues for bugs and features
- Discussions: Use GitHub Discussions for questions
- Slack: Contact maintainers on workspace (if available)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Acknowledgments

Thank you for making this project better!
