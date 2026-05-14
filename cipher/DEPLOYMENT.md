# Deployment Guide

## Prerequisites

- Docker and Docker Compose (for containerized deployment)
- Python 3.9+ (for local installation)
- GitHub account with personal access token
- Anthropic or OpenAI API key (for LLM features)

## Local Installation

### 1. Setup

```bash
# Clone repository
git clone https://github.com/your-org/cve-remediation-agent.git
cd cve-remediation-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Create environment file
cp .env.example .env
# Edit .env with your API keys
```

### 2. Test Installation

```bash
# Verify installation
cve-agent version

# Run tests
pytest tests/ -v

# Scan a project
cve-agent scan /path/to/project
```

## Docker Deployment

### 1. Build Image

```bash
docker build -t cve-remediation-agent:latest .
```

### 2. Run Container

```bash
docker run \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  -e GITHUB_TOKEN=$GITHUB_TOKEN \
  -v /path/to/project:/app/projects \
  cve-remediation-agent:latest \
  scan /app/projects
```

### 3. Docker Compose

```bash
# Create .env file
cp .env.example .env
# Edit .env with credentials

# Run with compose
docker-compose up

# Run specific command
docker-compose run --rm cve-agent remediate /app/projects --auto-pr
```

## GitHub Actions

### 1. Add Secrets

1. Go to repository Settings → Secrets
2. Add secrets:
   - `ANTHROPIC_API_KEY`
   - `GITHUB_TOKEN` (auto-created)
   - `NVD_API_KEY` (optional)

### 2. Enable Workflows

Copy workflow files from `.github/workflows/` to your repository.

### 3. Trigger Scans

- **Scheduled**: Daily at 2 AM UTC (see `automated-scan.yml`)
- **Manual**: Via GitHub UI
- **On Push**: Can be added via `on: push` configuration

### 4. Monitor Runs

View workflow runs in Actions tab. Failed scans create GitHub issues.

## Kubernetes Deployment

### 1. Build and Push Image

```bash
docker build -t your-registry/cve-remediation-agent:1.0.0 .
docker push your-registry/cve-remediation-agent:1.0.0
```

### 2. Create ConfigMap and Secrets

```bash
kubectl create configmap cve-agent-config \
  --from-file=config/agent_config.yaml

kubectl create secret generic cve-agent-credentials \
  --from-literal=anthropic-key=$ANTHROPIC_API_KEY \
  --from-literal=github-token=$GITHUB_TOKEN \
  --from-literal=nvd-key=$NVD_API_KEY
```

### 3. Deploy Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: cve-remediation-agent
spec:
  containers:
  - name: agent
    image: your-registry/cve-remediation-agent:1.0.0
    env:
    - name: ANTHROPIC_API_KEY
      valueFrom:
        secretKeyRef:
          name: cve-agent-credentials
          key: anthropic-key
    - name: GITHUB_TOKEN
      valueFrom:
        secretKeyRef:
          name: cve-agent-credentials
          key: github-token
    volumeMounts:
    - name: config
      mountPath: /app/config
    - name: projects
      mountPath: /app/projects
  volumes:
  - name: config
    configMap:
      name: cve-agent-config
  - name: projects
    hostPath:
      path: /path/to/projects
```

## CI/CD Integration

### Jenkins

```groovy
pipeline {
    agent any

    environment {
        ANTHROPIC_API_KEY = credentials('anthropic-key')
        GITHUB_TOKEN = credentials('github-token')
    }

    stages {
        stage('Scan') {
            steps {
                sh 'pip install -e .'
                sh 'cve-agent scan ${WORKSPACE} --min-severity CRITICAL'
            }
        }

        stage('Remediate') {
            steps {
                sh 'cve-agent remediate ${WORKSPACE} --auto-pr'
            }
        }
    }

    post {
        always {
            junit 'test-results/*.xml'
        }
    }
}
```

### GitLab CI

```yaml
stages:
  - scan
  - remediate

scan:
  stage: scan
  image: python:3.10
  script:
    - pip install -e .
    - cve-agent scan .
  only:
    - schedules

remediate:
  stage: remediate
  image: python:3.10
  script:
    - cve-agent remediate . --auto-pr
  only:
    - manual
```

## Production Best Practices

### 1. API Key Management

- Use secret management systems (AWS Secrets Manager, HashiCorp Vault)
- Rotate keys regularly
- Use minimal permission scopes

### 2. Monitoring

```yaml
# Prometheus metrics (future)
- agent_scans_total
- agent_vulnerabilities_found_total
- agent_prs_created_total
- agent_api_errors_total
```

### 3. Logging

- Log all operations to centralized system (ELK, CloudWatch, DataDog)
- Include: timestamp, module, level, message, context
- Avoid logging sensitive data

### 4. Rate Limiting

- Respect API rate limits (OSV: 10/min, NVD: 5/min)
- Implement exponential backoff
- Cache results when possible

### 5. Error Handling

- Monitor for API failures
- Alert on configuration errors
- Implement graceful degradation

### 6. Backup & Recovery

- Version control for all generated PRs
- Archive scan results
- Document rollback procedures

## Scaling

### Horizontal Scaling

For scanning large numbers of repositories:

1. **Queue System**: Use job queue (Celery, RQ) for async scanning
2. **Database**: Store results in PostgreSQL
3. **Load Balancer**: Distribute API requests

### Caching

Implement Redis caching for:
- CVE data (24-48 hour TTL)
- Changelog data (7 day TTL)
- Package metadata (weekly refresh)

## Troubleshooting

### High API Usage

```bash
# Check rate limit status
cve-agent --debug 2>&1 | grep -i "rate"

# Solutions:
# 1. Reduce scanning frequency
# 2. Add API keys for higher limits
# 3. Implement caching
```

### Failed Scans

```bash
# Increase logging detail
export LOG_LEVEL=DEBUG
cve-agent scan /path/to/project

# Check logs for:
# - API failures
# - File parsing errors
# - Network issues
```

### PR Creation Issues

```bash
# Verify GitHub credentials
echo $GITHUB_TOKEN

# Test GitHub API access
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user

# Check PR permissions
# - repo scope required
# - read:org for team access
```

## Maintenance

### Weekly

- Monitor API usage and costs
- Review scan results
- Check for new ecosystem versions

### Monthly

- Update dependencies: `pip install --upgrade -e .`
- Review and merge PRs
- Update configuration based on feedback

### Quarterly

- Upgrade Python version if new LTS released
- Review and update documentation
- Performance tuning

## Support & Issues

- GitHub Issues: Bug reports and features
- GitHub Discussions: Questions and ideas
- Email: cve-agent@your-org.com
