from setuptools import setup, find_packages

setup(
    name="cve-remediation-agent",
    version="0.1.0",
    description="Autonomous AI CVE Remediation Agent for automated vulnerability detection and patching",
    author="Security Team",
    python_requires=">=3.9",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "pyyaml>=6.0",
        "pydantic>=2.0",
        "pygithub>=2.1.1",
        "packaging>=23.0",
        "tenacity>=8.2.0",
        "openai>=1.0.0",
        "anthropic>=0.7.0",
        "pytest>=7.0",
        "pytest-cov>=4.0",
        "python-dotenv>=1.0",
    ],
    extras_require={
        "dev": [
            "black>=23.0",
            "flake8>=6.0",
            "mypy>=1.0",
            "isort>=5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "cve-agent=src.cli:main",
        ],
    },
)
