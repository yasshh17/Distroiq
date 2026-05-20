# DistroIQ Operations Guide

Comprehensive operational guide for running DistroIQ in production.

## Table of Contents

- [System Overview](#system-overview)
- [Monitoring & Alerts](#monitoring--alerts)
- [Deployment Procedures](#deployment-procedures)
- [Troubleshooting](#troubleshooting)
- [Security Operations](#security-operations)
- [Backup & Recovery](#backup--recovery)
- [Performance Tuning](#performance-tuning)
- [Maintenance Procedures](#maintenance-procedures)

## System Overview

### Architecture Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   External      │
│   (Vercel)      │    │   (Render)      │    │   Services      │
│                 │    │                 │    │                 │
│ • Next.js 14    │───▶│ • FastAPI       │───▶│ • Supabase      │
│ • TypeScript    │    │ • Python 3.11   │    │ • Anthropic     │
│ • Tailwind CSS  │    │ • PostgreSQL    │    │ • Cloudflare R2 │
│ • shadcn/ui     │    │ • Redis         │    │ • Doppler       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Critical Paths

1. **Authentication Flow**
   - User login → Supabase Auth → JWT → Backend validation
   - Account deletion → JWT verification → Supabase Admin API

2. **Chat/Query Flow**
   - User query → Backend → Anthropic API → RAG pipeline → Response

3. **Data Flow**
   - ERP/OMS/CRM → Embeddings → pgvector → Retrieval → Context

### Service Dependencies

| Service | Criticality | Fallback |
|---|---|---|
| Supabase Auth | Critical | None - service offline |
| Anthropic API | Critical | Error message to user |
| PostgreSQL | Critical | Connection pooling, retries |
| Redis | High | Graceful degradation |
| Cloudflare R2 | Medium | File uploads disabled |

## Monitoring & Alerts

### Key Metrics

#### Application Metrics
- **Request Rate**: Requests per minute by endpoint
- **Response Time**: P95 latency for critical endpoints
- **Error Rate**: 4xx/5xx errors as percentage of total requests
- **Auth Success Rate**: Successful authentication attempts
- **Account Deletion Success Rate**: Successful account deletions

#### Infrastructure Metrics
- **CPU Usage**: Average and peak CPU across services
- **Memory Usage**: Memory consumption and leaks
- **Database Connections**: Active and idle connections
- **Redis Memory**: Cache hit rate and memory usage
- **Network**: Bandwidth and connection errors

#### Business Metrics
- **Active Users**: Daily and monthly active users
- **Query Volume**: Chat queries per hour/day
- **Data Sources**: Connected sources and health
- **User Engagement**: Session duration and query types

### Alert Thresholds

#### Critical Alerts (Page immediately)
- Error rate > 10% for 5 minutes
- Authentication failure rate > 25% for 3 minutes
- Account deletion failure rate > 50% for 2 minutes
- Any service completely down
- Database connection failures > 50% for 1 minute

#### Warning Alerts (Notify during business hours)
- Response time P95 > 5 seconds for 10 minutes
- Error rate > 5% for 15 minutes
- Memory usage > 85% for 10 minutes
- Redis cache hit rate < 90% for 30 minutes
- External service timeout rate > 5% for 15 minutes

### Monitoring Setup

#### Application Monitoring
```bash
# Health check endpoint
curl -f http://localhost:8000/api/v1/health

# Comprehensive health check
scripts/health-check.py --format json

# Metrics endpoint (if implemented)
curl http://localhost:8000/api/v1/metrics
```

#### Log Aggregation
```bash
# Application logs
tail -f backend/logs/app.log

# Authentication events
grep "auth" backend/logs/app.log | jq

# Error tracking
grep -E "(ERROR|CRITICAL)" backend/logs/app.log
```

#### External Service Monitoring
- **Supabase**: Monitor via dashboard and API
- **Anthropic**: Track API quotas and rate limits
- **Vercel**: Monitor deployments and edge functions
- **Render**: Monitor service health and resource usage

## Deployment Procedures

### Pre-deployment Checklist

```bash
# 1. Run full test suite
cd backend && python -m pytest
cd .. && npm test

# 2. Build validation
npm run build
cd backend && .venv/bin/python -c "from app.main import app; print('✅')"

# 3. Security checks
scripts/validate-env-files.sh backend/.env
scripts/check-env-secrets.sh backend/.env

# 4. Deployment readiness
scripts/deployment-check.sh

# 5. Pre-commit hooks
pre-commit run --all-files
```

### Deployment Process

#### Frontend (Vercel)
```bash
# Automatic deployment on main branch push
git push origin main

# Manual deployment
vercel deploy --prod

# Rollback to previous deployment
vercel rollback [deployment-url]
```

#### Backend (Render)
```bash
# Automatic deployment on main branch push
git push origin main

# Manual deployment via Render dashboard
# 1. Go to Render dashboard
# 2. Select service
# 3. Click "Deploy latest commit"

# Environment variables
# Update via Render dashboard or render.yaml
```

### Post-deployment Validation

```bash
# 1. Health check
scripts/health-check.py --exit-code

# 2. Smoke tests
curl -f https://api.distroiq.com/api/v1/health
curl -f https://distroiq.com/

# 3. Authentication test
# (Manual login/logout test)

# 4. Account deletion test
scripts/debug-account-deletion.py --test-jwt

# 5. Monitor error rates for 15 minutes
# Check monitoring dashboard
```

### Rollback Procedures

#### Frontend Rollback
```bash
# Via Vercel CLI
vercel rollback [previous-deployment-url]

# Via git (if needed)
git revert [bad-commit-hash]
git push origin main
```

#### Backend Rollback
```bash
# Via Render dashboard
# 1. Go to service
# 2. Select previous successful deployment
# 3. Click "Redeploy"

# Via git (emergency)
git revert [bad-commit-hash]
git push origin main
```

## Troubleshooting

### Common Issues

#### High Error Rate
```bash
# 1. Check logs for error patterns
grep -E "(ERROR|CRITICAL)" backend/logs/app.log | tail -20

# 2. Check external service status
curl -I https://api.anthropic.com/v1/health
curl -I https://[project].supabase.co/rest/v1/

# 3. Review recent deployments
git log --oneline -10

# 4. Check resource usage
top
df -h
```

#### Slow Response Times
```bash
# 1. Check database performance
# - Connection pool usage
# - Slow query logs
# - Index performance

# 2. Check external API latency
time curl https://api.anthropic.com/v1/health

# 3. Check Redis performance
redis-cli info stats

# 4. Profile application
# Add performance logging if needed
```

#### Authentication Issues
```bash
# 1. Run authentication diagnostics
scripts/debug-account-deletion.py --test-jwt

# 2. Check Supabase status
curl -I https://[project].supabase.co/auth/v1/settings

# 3. Validate JWT configuration
scripts/validate-jwt-secrets.py backend/.env

# 4. Check for configuration drift
diff backend/.env.example backend/.env
```

### Service Recovery

#### Database Recovery
```bash
# 1. Check database connectivity
psql $DATABASE_URL -c "SELECT 1;"

# 2. Restart connection pool
# (Application restart required)

# 3. Check for locks
psql $DATABASE_URL -c "SELECT * FROM pg_locks WHERE granted = false;"

# 4. Monitor connection count
psql $DATABASE_URL -c "SELECT count(*) FROM pg_stat_activity;"
```

#### Redis Recovery
```bash
# 1. Check Redis status
redis-cli ping

# 2. Check memory usage
redis-cli info memory

# 3. Clear cache if needed (emergency only)
redis-cli flushdb

# 4. Restart Redis (if self-hosted)
sudo systemctl restart redis
```

## Security Operations

### Security Monitoring

#### Authentication Events
```bash
# Monitor login failures
grep "LOGIN_FAILURE" backend/logs/app.log

# Check for brute force attempts
grep "authentication" backend/logs/app.log | \
  grep -E "$(date '+%Y-%m-%d')" | \
  cut -d' ' -f5 | sort | uniq -c | sort -nr

# Monitor account deletions
grep "ACCOUNT_DELETE" backend/logs/app.log
```

#### Anomaly Detection
```bash
# Unusual API usage patterns
grep "api_requests_total" backend/logs/app.log | \
  awk '{print $1, $2}' | uniq -c | sort -nr

# Geographic anomalies (if IP logging enabled)
grep "ip_address" backend/logs/app.log | \
  grep -E "$(date '+%Y-%m-%d')" | \
  # Parse IPs and check against known ranges
```

### Incident Response

#### Security Incident Checklist
1. **Immediate Response**
   - Assess scope and impact
   - Contain the threat
   - Preserve evidence

2. **Investigation**
   - Analyze logs and audit trails
   - Identify attack vectors
   - Document findings

3. **Recovery**
   - Apply fixes
   - Monitor for recurrence
   - Update security measures

4. **Post-incident**
   - Conduct post-mortem
   - Update procedures
   - Train team on lessons learned

### Access Control

#### Service Accounts
- **Supabase Service Role**: Account management only
- **Anthropic API Key**: AI inference only
- **Database**: Connection pooled, least privilege
- **Redis**: Cache access only

#### Key Rotation
```bash
# 1. Generate new keys
# 2. Update environment variables
# 3. Deploy updated configuration
# 4. Verify service functionality
# 5. Revoke old keys
```

## Backup & Recovery

### Data Backup Strategy

#### Database Backups
- **Frequency**: Daily automated, weekly manual verification
- **Retention**: 30 days point-in-time recovery
- **Storage**: Encrypted backups in separate region
- **Testing**: Monthly restore tests

#### Configuration Backups
- **Environment Variables**: Stored in Doppler
- **Deployment Configs**: Version controlled in git
- **Secrets**: Encrypted backup in secure vault

### Recovery Procedures

#### Database Recovery
```bash
# 1. Stop application
# 2. Restore from backup
pg_restore -d $DATABASE_URL backup_file.dump

# 3. Verify data integrity
psql $DATABASE_URL -c "SELECT count(*) FROM users;"

# 4. Restart application
# 5. Run smoke tests
```

#### Configuration Recovery
```bash
# 1. Restore from Doppler
doppler secrets download --format env > .env

# 2. Verify configuration
scripts/validate-env-files.sh .env

# 3. Redeploy services
# 4. Run health checks
```

## Performance Tuning

### Database Optimization

#### Query Performance
```sql
-- Enable query logging
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_duration = on;

-- Analyze slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch 
FROM pg_stat_user_indexes 
ORDER BY idx_scan ASC;
```

#### Connection Pooling
```python
# Configure connection pool
DATABASE_POOL_SIZE = 20
DATABASE_MAX_OVERFLOW = 30
DATABASE_POOL_TIMEOUT = 30
```

### Application Performance

#### Memory Optimization
```bash
# Monitor memory usage
ps aux | grep uvicorn
free -h

# Profile memory usage
python -m memory_profiler app/main.py
```

#### Response Time Optimization
```bash
# Profile API endpoints
time curl -X POST https://api.distroiq.com/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'

# Check for N+1 queries
# Enable SQL logging and analyze patterns
```

### Caching Strategy

#### Redis Configuration
```bash
# Optimal Redis settings
redis-cli config set maxmemory 1gb
redis-cli config set maxmemory-policy allkeys-lru
redis-cli config set save "900 1 300 10 60 10000"
```

#### Application Caching
```python
# Cache frequently accessed data
@lru_cache(maxsize=1000)
def get_user_permissions(user_id: str):
    # Implementation
    pass
```

## Maintenance Procedures

### Routine Maintenance

#### Daily Tasks
- Review error logs and metrics
- Check backup completion
- Monitor resource usage
- Verify external service health

#### Weekly Tasks
- Review and clean up logs
- Update dependencies (security patches)
- Performance baseline analysis
- Capacity planning review

#### Monthly Tasks
- Security audit and penetration testing
- Disaster recovery testing
- Performance optimization review
- Documentation updates

### Dependency Updates

#### Security Updates
```bash
# Backend dependencies
cd backend
pip list --outdated
pip install --upgrade package-name

# Frontend dependencies
npm audit
npm update

# Check for vulnerabilities
npm audit --audit-level=high
```

#### Major Updates
1. **Planning**
   - Review breaking changes
   - Plan migration strategy
   - Schedule maintenance window

2. **Testing**
   - Test in staging environment
   - Run full test suite
   - Performance testing

3. **Deployment**
   - Deploy during low-traffic window
   - Monitor metrics closely
   - Have rollback plan ready

### Log Management

#### Log Rotation
```bash
# Configure logrotate (if self-hosted)
cat > /etc/logrotate.d/distroiq << EOF
/var/log/distroiq/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 app app
}
EOF
```

#### Log Analysis
```bash
# Error analysis
grep -E "(ERROR|CRITICAL)" backend/logs/app.log | \
  awk '{print $3}' | sort | uniq -c | sort -nr

# Performance analysis
grep "response_time" backend/logs/app.log | \
  awk '{print $5}' | \
  sort -n | awk '{a[i++]=$1} END {print a[int(i*0.95)]}'
```

## Emergency Procedures

### Service Outage Response

1. **Acknowledge the incident** (within 5 minutes)
2. **Assess the scope and impact**
3. **Communicate to stakeholders**
4. **Begin recovery procedures**
5. **Monitor progress and adjust**
6. **Conduct post-mortem**

### Communication Templates

#### Status Page Update
```
🔴 INVESTIGATING: Account deletion service experiencing issues

We're investigating reports of failed account deletions. 
New account deletion requests may fail during this time.

Updates: every 30 minutes
ETA: investigating

[Timestamp]
```

#### Resolution Update
```
✅ RESOLVED: Account deletion service restored

The account deletion service has been restored. Root cause 
was a configuration issue that has been fixed.

Next steps: monitoring for stability

[Timestamp]
```

## On-call Procedures

### Escalation Matrix

| Severity | Response Time | Escalation |
|---|---|---|
| Critical | 5 minutes | Immediate page |
| High | 30 minutes | Phone call |
| Medium | 2 hours | Slack/email |
| Low | Next business day | Ticket |

### On-call Checklist

#### New Incident
1. Acknowledge in monitoring system
2. Assess severity and impact
3. Begin investigation
4. Update status page if needed
5. Escalate if required

#### Handoff
1. Document current status
2. List ongoing issues
3. Note any scheduled maintenance
4. Brief next on-call engineer

---

**For additional support:**
- **Documentation**: `/docs` directory
- **Runbooks**: `/docs/*_RUNBOOK.md`
- **Emergency contacts**: [Your contact system]