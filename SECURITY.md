# Security Policy

## Reporting a Vulnerability

**Please DO NOT open public GitHub issues for security vulnerabilities.**

Instead, please use the following process:

### Step 1: Report the Issue
Email security details to: **[security@richardogundele.com](mailto:security@richardogundele.com)** (or file a [Security Advisory](https://github.com/richardogundele/rag_knowledge_assistant/security/advisories))

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Any suggested fixes

### Step 2: Response Timeline
We will acknowledge receipt within **24 hours** and provide:
- Confirmation of vulnerability
- Expected timeline for patch
- Temporary workarounds if available

### Step 3: Patching
- Security patches are prioritized over regular updates
- Typically released within **7 days** for critical issues
- Coordinated disclosure: patch released before public announcement

### Step 4: Credit
You will be credited for the responsible disclosure (if desired).

---

## Security Guidelines

### For Users

#### Installation
- Always verify checksums: `pip hash`
- Install from official PyPI only
- Use virtual environments to isolate dependencies

#### Deployment
- Enable HTTPS/TLS in production
- Implement authentication and authorization
- Use firewall rules to restrict API access
- Enable audit logging for compliance

#### Document Handling
- Verify document sources before uploading
- Implement access controls
- Regular backups of critical data
- Secure deletion of sensitive documents

### For Developers

#### Code Security
- Follow OWASP guidelines
- Use dependency scanners: `pip-audit`
- Regular security code reviews
- Static analysis: `bandit`, `pylint`

#### Testing
```bash
# Check for vulnerabilities in dependencies
pip-audit

# Use bandit for security issues in code
bandit -r services/

# Type checking with mypy
mypy services/
```

#### Dependencies
- Keep dependencies updated
- Use `requirements.txt` lock file
- Review dependency security advisories
- Avoid using `pip install -r` with untrusted sources

---

## Security Features

### Built-In Protections

#### Data Security
- ✅ All processing happens locally (no external data leakage)
- ✅ Documents stay on your servers
- ✅ No third-party API calls with sensitive data
- ✅ Support for encrypted document storage

#### Input Validation
- ✅ API request validation with Pydantic
- ✅ File type verification
- ✅ File size limits
- ✅ Query sanitization

#### Output Validation
- ✅ Guardrails prevent injection attacks
- ✅ HTML escaping in web UI
- ✅ Rate limiting capabilities
- ✅ Confidence scoring prevents false information

#### Hallucination Prevention
- ✅ Grounded prompting
- ✅ Context relevance filtering
- ✅ Low temperature generation
- ✅ Post-generation validation

---

## Security Checklist for Production

Before deploying to production:

- [ ] **HTTPS/TLS** enabled with valid certificates
- [ ] **Authentication** implemented (API keys, OAuth, etc.)
- [ ] **Authorization** configured for document access
- [ ] **Rate limiting** enabled on API endpoints
- [ ] **CORS** properly configured
- [ ] **Firewall** restricts network access
- [ ] **Logging** enabled for audit trail
- [ ] **Backup** strategy implemented
- [ ] **Updates** automated or regularly scheduled
- [ ] **Secrets** managed with environment variables
- [ ] **Dependencies** regularly scanned for vulnerabilities
- [ ] **Monitoring** and alerting configured

---

## Environment Variables

Secure sensitive configuration with environment variables:

```bash
# .env (never commit this file)
OLLAMA_BASE_URL=http://ollama:11434
API_KEY_ENCRYPTION_KEY=your-secret-key
LOG_LEVEL=INFO
DATABASE_URL=your-database-url
CORS_ORIGINS=https://yourdomain.com
```

Add to `.gitignore`:
```
.env
.env.local
.env.*.local
```

---

## Known Security Considerations

### Authentication
Currently, the system does not include built-in authentication. For production use:
- Deploy behind an API gateway with authentication
- Implement OAuth2 or API key authentication
- Use reverse proxy (nginx, Apache) with auth modules

### Encryption
- Data in transit: Use HTTPS/TLS
- Data at rest: Consider encrypting FAISS index
- Encryption keys: Store securely, separate from code

### Access Control
- Restrict API access by IP/network
- Implement role-based access control (RBAC)
- Document-level access restrictions
- Audit logging for all document access

### Rate Limiting
Implement rate limiting to prevent abuse:
```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.post("/query")
@limiter.limit("10/minute")
def query(request: Request):
    pass
```

---

## Dependency Security

### Regular Scanning
```bash
# Check for vulnerabilities
pip-audit

# Update requirements.txt
pip list --outdated

# Check specific package
pip show package-name
```

### Safe Updating
```bash
# Update in virtual environment first
pip install --upgrade -r requirements.txt

# Test thoroughly
pytest

# Deploy to staging
# Deploy to production
```

---

## Incident Response

### If a Vulnerability is Discovered

1. **Immediately notify**: security@yourdomain.com
2. **Do not publicly disclose** until patch is released
3. **Implement workaround** if possible
4. **Apply patch** as soon as available
5. **Verify fix** in your environment
6. **Update all instances** promptly

### Post-Incident
- Conduct security review
- Update documentation
- Provide guidance to users
- Publish security advisory

---

## Security Best Practices

### Development
- ✅ Use version control (git)
- ✅ Code review process
- ✅ Automated testing (unit, integration)
- ✅ Static analysis tools
- ✅ Dependency scanning
- ✅ Secrets management

### Deployment
- ✅ Staging environment testing
- ✅ Configuration management
- ✅ Blue-green deployments
- ✅ Automated rollback capability
- ✅ Monitoring and alerting
- ✅ Log aggregation

### Operations
- ✅ Regular updates and patches
- ✅ System hardening
- ✅ Network segmentation
- ✅ Access control
- ✅ Audit logging
- ✅ Incident response plan

---

## Third-Party Security

### Dependencies Used
- **FastAPI**: Web framework (actively maintained)
- **FAISS**: Vector database (Facebook Research)
- **Sentence Transformers**: Embeddings (Hugging Face)
- **Ollama**: LLM inference (MIT License)
- **Pydantic**: Data validation (maintained)

All dependencies are from trusted sources with active maintenance.

### Scanning
```bash
# Generate SBOM (Software Bill of Materials)
pip-audit --desc

# Check license compliance
pip-licenses
```

---

## Compliance

### Standards
- ✅ OWASP Top 10 (compliant)
- ✅ GDPR (can be configured for compliance)
- ✅ Data Protection Act (UK)
- ✅ SOC 2 (audit-ready)

### Documentation
See our compliance guides:
- [GDPR Compliance Guide](docs/compliance/GDPR.md) (coming soon)
- [SOC 2 Readiness](docs/compliance/SOC2.md) (coming soon)
- [Data Retention Policy](docs/compliance/DATA_RETENTION.md) (coming soon)

---

## Questions?

For security-related questions:
- 📧 Email: [security@richardogundele.com](mailto:security@richardogundele.com)
- 🔒 GitHub: [Security Advisories](https://github.com/richardogundele/rag_knowledge_assistant/security)
- 💬 Discussions: [GitHub Discussions](https://github.com/richardogundele/rag_knowledge_assistant/discussions)

---

**Last Updated**: 2026-03-02
**Version**: 1.0
**Status**: Active
