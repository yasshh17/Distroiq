# Account Deletion Runbook

This runbook provides operational guidance for managing account deletion issues in DistroIQ.

## Quick Reference

| Issue Type | Likely Cause | First Action |
|---|---|---|
| "Failed to delete account" | Configuration | Run `scripts/debug-account-deletion.py` |
| 401 Unauthorized | JWT secret issue | Check `.env` for whitespace in `SUPABASE_JWT_SECRET` |
| 500 Service error | Service role key | Verify `SUPABASE_SERVICE_ROLE_KEY` configuration |
| Timeout errors | Network/Supabase | Check Supabase status page |

## Common Issues

### 1. JWT Secret Whitespace Issue

**Symptoms:**
- Users get "Failed to delete account" error
- Logs show JWT verification failures
- Auth diagnostics fail

**Root Cause:**
Leading or trailing whitespace in `SUPABASE_JWT_SECRET` environment variable.

**Fix:**
```bash
# 1. Check the current value (in backend/.env)
grep SUPABASE_JWT_SECRET backend/.env

# 2. Look for leading/trailing spaces
# BAD:  SUPABASE_JWT_SECRET= your-secret
# GOOD: SUPABASE_JWT_SECRET=your-secret

# 3. Fix by removing spaces
sed -i 's/SUPABASE_JWT_SECRET= /SUPABASE_JWT_SECRET=/' backend/.env

# 4. Restart the backend
cd backend && .venv/bin/python -m uvicorn app.main:app --reload
```

**Prevention:**
- Use the pre-commit hooks: `pre-commit install`
- Run validation: `scripts/validate-env-files.sh backend/.env`

### 2. Service Role Key Not Configured

**Symptoms:**
- Error: "Account deletion not configured"
- 500 status code
- Missing `SUPABASE_SERVICE_ROLE_KEY`

**Fix:**
```bash
# 1. Get the service role key from Supabase dashboard
# Go to: Project Settings > API > Project API keys > service_role

# 2. Add to backend/.env
echo "SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6..." >> backend/.env

# 3. Restart backend
```

### 3. Supabase Connectivity Issues

**Symptoms:**
- Timeouts
- "Unable to reach authentication service"
- Network errors

**Diagnosis:**
```bash
# 1. Check Supabase status
curl -I https://status.supabase.com

# 2. Test connectivity from backend
cd backend
python3 -c "
import asyncio
from app.core.diagnostics import AuthDiagnostics
async def test():
    result = await AuthDiagnostics.test_supabase_connection()
    print(f'Status: {result.passed}')
    print(f'Details: {result.details}')
asyncio.run(test())
"

# 3. Check DNS resolution
nslookup [your-project].supabase.co
```

**Fix:**
- Wait if Supabase is experiencing outages
- Check firewall rules if self-hosted
- Verify `SUPABASE_URL` is correct

### 4. User Not Found

**Symptoms:**
- "User account not found"
- 404 status code
- User reports successful deletion attempt

**This is usually correct behavior:**
- User may have already been deleted
- User ID may be incorrect
- Check audit logs for previous deletion

**Verification:**
```bash
# Check audit logs for this user
grep "user_id.*abc-123-def" backend/logs/app.log

# Verify user exists in Supabase (if accessible)
# Use Supabase dashboard or admin API
```

## Diagnostic Tools

### 1. Interactive Debug Tool
```bash
cd /path/to/distroiq
scripts/debug-account-deletion.py

# Options:
# 1. Test configuration
# 2. Debug specific user ID
# 3. Test with generated user ID
# 4. Test JWT creation and validation
# 5. Full system diagnostic
```

### 2. Command Line Debug
```bash
# Debug specific user
scripts/debug-account-deletion.py --user-id "550e8400-e29b-41d4-a716-446655440000"

# Test JWT system only
scripts/debug-account-deletion.py --test-jwt

# Check configuration only
scripts/debug-account-deletion.py --config-only

# Get JSON output
scripts/debug-account-deletion.py --user-id "..." --json
```

### 3. Health Check
```bash
# Full health check
scripts/health-check.py

# Summary only
scripts/health-check.py --format summary

# Exit with error code if unhealthy
scripts/health-check.py --exit-code
```

### 4. Environment Validation
```bash
# Validate environment files
scripts/validate-env-files.sh backend/.env

# Check for secrets
scripts/check-env-secrets.sh backend/.env

# Validate JWT secrets specifically
scripts/validate-jwt-secrets.py backend/.env
```

## Monitoring and Alerts

### Key Metrics to Monitor

1. **Account deletion success rate**
   - Target: >99%
   - Alert: <95% over 1 hour

2. **Account deletion response time**
   - Target: <2 seconds
   - Alert: >5 seconds average

3. **Authentication error rate**
   - Target: <1%
   - Alert: >5% over 15 minutes

4. **Supabase connectivity**
   - Target: 100% uptime
   - Alert: Any failed health checks

### Log Patterns to Watch

```bash
# Authentication failures
grep "AUTH_REQUIRED\|TOKEN_VERIFICATION_FAILED" backend/logs/app.log

# Account deletion failures
grep "DELETION_FAILED\|DELETION_NOT_CONFIGURED" backend/logs/app.log

# External service errors
grep "EXTERNAL_SERVICE_ERROR" backend/logs/app.log

# Rate limiting
grep "RATE_LIMIT_EXCEEDED" backend/logs/app.log
```

## Escalation Procedures

### Level 1: Configuration Issues
- JWT secret formatting
- Environment variable errors
- Basic connectivity

**Actions:**
1. Run diagnostic tools
2. Check environment configuration
3. Restart services if needed

**Escalate if:** Issue persists after configuration fixes

### Level 2: Service Degradation
- Intermittent failures
- Performance issues
- External service problems

**Actions:**
1. Check external service status
2. Review metrics and logs
3. Consider temporary mitigations

**Escalate if:** Affects >10% of users or persists >30 minutes

### Level 3: Security Incidents
- Suspected unauthorized access
- Bulk deletion attempts
- Service abuse

**Actions:**
1. Immediately review audit logs
2. Check for unusual patterns
3. Consider temporary service disable

**Always escalate immediately to security team**

## Recovery Procedures

### Service Recovery
```bash
# 1. Restart backend service
cd backend
.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 2. Clear any cached tokens (if using Redis)
redis-cli FLUSHDB

# 3. Run health check
scripts/health-check.py --exit-code
```

### Data Recovery
Account deletions are permanent by design. However:

1. **Audit trail is preserved** - check logs for deletion details
2. **Database backups** may contain historical data (if available)
3. **Contact Supabase support** for enterprise accounts with backup guarantees

### Communication Template

```
Subject: Account Deletion Service - [Status]

Issue: [Brief description]
Impact: [Number of users affected / severity]
Timeline: [When started / expected resolution]
Actions: [What we're doing]
Workaround: [If available]

Next update: [Time]
```

## Testing Account Deletion

### Pre-deployment Testing
```bash
# 1. Run test suite
cd backend && python -m pytest tests/test_account_deletion.py -v

# 2. Integration test
scripts/debug-account-deletion.py --test-jwt

# 3. Full diagnostic
scripts/debug-account-deletion.py --user-id "test-user-id"

# 4. Deployment readiness
scripts/deployment-check.sh
```

### Post-deployment Validation
```bash
# 1. Health check
scripts/health-check.py

# 2. Create test user and delete
# (Manual process through frontend)

# 3. Check audit logs
grep "account_deletion" backend/logs/app.log | tail -5
```

## Configuration Reference

### Required Environment Variables
```bash
# Backend (.env)
SUPABASE_URL=https://[project].supabase.co
SUPABASE_JWT_SECRET=[64-char-base64-secret]
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6...
ANTHROPIC_API_KEY=sk-ant-api03-...
DATABASE_URL=postgresql+asyncpg://...
```

### Supabase Configuration
- Service role must have `auth.users.delete` permission
- JWT secret must match Supabase project settings
- URL must be the correct project endpoint

## Emergency Contacts

- **Primary On-call:** [Your on-call system]
- **Supabase Support:** [Enterprise support if available]
- **Security Team:** [Security incident escalation]

## Related Documentation

- [Authentication Guide](./AUTHENTICATION.md)
- [Security Procedures](./SECURITY.md)
- [Deployment Guide](./DEPLOYMENT.md)
- [API Documentation](./API.md)