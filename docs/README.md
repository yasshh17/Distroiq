# DistroIQ Documentation

Welcome to the DistroIQ documentation. This directory contains comprehensive guides for developers, operators, and stakeholders.

## 📚 Documentation Index

### 🏗️ Architecture & Design
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Complete system architecture, design decisions, and technical implementation details
- **[CLAUDE.md](../CLAUDE.md)** - Project overview, tech stack, and development guidelines (main project documentation)

### 🔧 Operations & Maintenance  
- **[OPERATIONS.md](./OPERATIONS.md)** - Complete operational guide including monitoring, deployment, troubleshooting, and maintenance procedures
- **[ACCOUNT_DELETION_RUNBOOK.md](./ACCOUNT_DELETION_RUNBOOK.md)** - Detailed runbook for troubleshooting account deletion issues

### 🚀 Development & Deployment
- **[Code Style Rules](../.claude/rules/code-style.md)** - TypeScript/React and Python coding conventions
- **[Testing Rules](../.claude/rules/testing.md)** - Testing requirements and validation procedures
- **[API Conventions](../.claude/rules/api-conventions.md)** - API design patterns and authentication

### 🛠️ Tools & Scripts
- **[scripts/](../scripts/)** - Operational tooling and diagnostic scripts
  - `health-check.py` - Comprehensive system health checker
  - `debug-account-deletion.py` - Interactive account deletion debugger
  - `deployment-check.sh` - Pre-deployment validation
  - `validate-env-files.sh` - Environment variable validation
  - Pre-commit hooks and validation tools

### ⚡ Quick Start Guides

#### For Developers
1. Read [CLAUDE.md](../CLAUDE.md) for project overview
2. Review [Code Style Rules](../.claude/rules/code-style.md)
3. Set up pre-commit hooks: `pre-commit install`
4. Run health check: `scripts/health-check.py`

#### For Operations
1. Read [OPERATIONS.md](./OPERATIONS.md) for comprehensive guide
2. Familiarize with [Account Deletion Runbook](./ACCOUNT_DELETION_RUNBOOK.md)
3. Set up monitoring and alerts
4. Test diagnostic tools: `scripts/debug-account-deletion.py`

#### For Deployment
1. Run pre-deployment checks: `scripts/deployment-check.sh`
2. Follow deployment procedures in [OPERATIONS.md](./OPERATIONS.md)
3. Validate with health checks post-deployment

## 🎯 Key Features Documented

### Enterprise Security
- **Comprehensive Audit Logging** - All user actions tracked for compliance
- **Production-grade Error Handling** - Structured error responses with correlation IDs
- **JWT Validation with Field Validators** - Prevents whitespace and configuration issues
- **Account Deletion Security** - Multi-step validation with proper authorization

### Operational Excellence  
- **Diagnostic Tooling** - Interactive debugging for complex issues
- **Health Monitoring** - Multi-layer system health checks
- **Pre-commit Validation** - Prevents configuration errors before deployment
- **Metrics & Telemetry** - Comprehensive tracking for performance and business insights

### Development Quality
- **End-to-end Testing** - Complete test coverage for critical paths
- **Configuration Validation** - Runtime validation prevents deployment issues
- **Documentation-driven** - Self-documenting architecture and procedures

## 🆘 Emergency Procedures

### Critical Issues
1. **Service Down**: Check [OPERATIONS.md](./OPERATIONS.md) → Emergency Procedures
2. **Account Deletion Failures**: Use [ACCOUNT_DELETION_RUNBOOK.md](./ACCOUNT_DELETION_RUNBOOK.md)
3. **Security Incident**: Follow escalation matrix in [OPERATIONS.md](./OPERATIONS.md)

### Quick Diagnostics
```bash
# Overall system health
scripts/health-check.py --format summary

# Account deletion specific
scripts/debug-account-deletion.py

# Configuration validation  
scripts/validate-env-files.sh backend/.env
```

## 📞 Support Contacts

- **Development Team**: [Your team contact]
- **Operations**: [Your ops contact] 
- **Security Incidents**: [Your security contact]
- **Emergency Escalation**: [Your escalation process]

## 🔄 Documentation Maintenance

This documentation is maintained alongside the codebase. When making changes:

1. **Update relevant docs** for any architectural changes
2. **Test procedures** described in runbooks  
3. **Verify scripts** mentioned in documentation still work
4. **Update version references** in architecture diagrams

---

**Last Updated**: [Current date would go here]
**Maintained by**: Engineering Team
**Review Schedule**: Monthly