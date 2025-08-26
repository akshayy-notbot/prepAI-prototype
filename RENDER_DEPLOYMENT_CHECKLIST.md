# 🚀 PrepAI Render Deployment Checklist

## Overview
This checklist covers all critical database-related issues and architectural considerations for deploying PrepAI to Render, especially considering the recent architectural changes to a Redis-based session management system.

## 🔍 Pre-Deployment Validation

### 1. Environment Variables Setup (Render Dashboard)
- [ ] **DATABASE_URL**: Set in Render PostgreSQL service
  - Automatically provided by Render PostgreSQL service
  - Format: `postgresql://username:password@host:port/database_name`
  - No manual configuration needed
  
- [ ] **REDIS_URL**: Set in Render Redis service
  - Automatically provided by Render Redis service
  - Format: `redis://host:port/database_number`
  - Critical for new architecture session management
  - No manual configuration needed
  
- [ ] **GOOGLE_API_KEY**: Set in Render environment variables
  - Must be a valid Google Gemini API key
  - Must not contain placeholder values
  - Must have sufficient quota for production use
  
- [ ] **ENVIRONMENT**: Set to `production` in Render
- [ ] **PYTHON_VERSION**: Set to `3.11.9` in Render

**Note**: All environment variables are managed through Render's dashboard. Do not commit actual values to version control.

### 2. Database Schema Validation
- [ ] Run `python verify_render_deployment.py` locally (with your local .env)
- [ ] Verify all required tables exist:
  - `interview_sessions` - Main interview data
  - `session_states` - Final session state (PostgreSQL)
  - `topic_graphs` - Reusable interview blueprints
  - `analysis_orchestrators` - Analysis coordination
  - `specialist_agents` - Individual analysis agents
  - `user_responses` - Individual responses
  - `analysis_results` - Analysis results
  - `skill_performance` - Skill tracking

### 3. Redis Functionality Test
- [ ] Test JSON operations (critical for new architecture)
- [ ] Test session state operations
- [ ] Verify connection pooling settings
- [ ] Test expiration and cleanup mechanisms

## 🏗️ Architecture-Specific Considerations

### New Two-Prompt System
- [ ] **RouterAgent**: Fast classification (< 750ms target)
  - Depends on Redis for session state
  - No PostgreSQL writes during interviews
  
- [ ] **GeneratorAgent**: Powerful question generation (< 3s target)
  - Only called when needed
  - Depends on Redis for conversation context
  
- [ ] **PersonaAgent**: Orchestration layer
  - Manages Redis session state
  - Only writes to PostgreSQL after interview completion

### Session State Management
- [ ] **Real-time State**: Stored in Redis only
  - Session progress
  - Conversation history
  - Topic completion status
  
- [ ] **Final State**: Persisted to PostgreSQL
  - Only after interview ends
  - Used for analytics and reporting

## 🗄️ Database Configuration

### PostgreSQL Settings
- [ ] Connection pooling configured
  - Pool size: 10
  - Max overflow: 20
  - Pool timeout: 30 seconds
  
- [ ] JSONB fields properly indexed
  - `topic_graph` in `interview_sessions`
  - `final_topic_progress` in `session_states`
  - `analysis_results` in `analysis_results`

### Redis Settings
- [ ] Memory policy: `allkeys-lru`
- [ ] Max connections: 20
- [ ] Socket timeout: 5 seconds
- [ ] Connection timeout: 5 seconds

## 🔧 Deployment Steps

### 1. Render Service Configuration
- [ ] PostgreSQL service created and running
- [ ] Redis service created and running
- [ ] Web service configured with correct environment variables
- [ ] Health check endpoint responding (`/health`)

### 2. Environment Variables in Render Dashboard
- [ ] **DATABASE_URL**: Automatically set by PostgreSQL service
- [ ] **REDIS_URL**: Automatically set by Redis service
- [ ] **GOOGLE_API_KEY**: Manually set with your actual API key
- [ ] **ENVIRONMENT**: Set to `production`
- [ ] **PYTHON_VERSION**: Set to `3.11.9`

### 3. Database Migration
- [ ] Run `python migrate_database.py` if needed
- [ ] Verify all tables created successfully
- [ ] Check table structure matches models.py

### 4. Startup Validation
- [ ] Monitor startup logs for any errors
- [ ] Verify all validation checks pass
- [ ] Confirm Redis session operations working
- [ ] Test database connection pool

## 🧪 Post-Deployment Testing

### 1. Health Checks
- [ ] `/health` endpoint responding
- [ ] Database connection working
- [ ] Redis connection working
- [ ] All required services accessible

### 2. Interview Flow Test
- [ ] Create new interview session
- [ ] Verify Redis session state creation
- [ ] Test RouterAgent response classification
- [ ] Test GeneratorAgent question generation
- [ ] Verify session state persistence to PostgreSQL

### 3. Performance Monitoring
- [ ] RouterAgent latency < 750ms
- [ ] GeneratorAgent latency < 3s
- [ ] Database connection pool utilization
- [ ] Redis memory usage
- [ ] API response times

## 🚨 Critical Issues to Monitor

### Database Connection Issues
- [ ] Connection pool exhaustion
- [ ] Database timeout errors
- [ ] Connection string format issues
- [ ] SSL connection problems

### Redis Issues
- [ ] Memory pressure (allkeys-lru policy)
- [ ] Connection failures
- [ ] JSON serialization errors
- [ ] Session state corruption

### Architecture Issues
- [ ] Session state loss in Redis
- [ ] PostgreSQL write failures during completion
- [ ] Agent initialization failures
- [ ] Topic graph parsing errors

## 📊 Monitoring and Alerts

### Key Metrics
- [ ] Database connection count
- [ ] Redis memory usage
- [ ] API response times
- [ ] Error rates by endpoint
- [ ] Session completion rates

### Alert Thresholds
- [ ] Database connection pool > 80% utilization
- [ ] Redis memory > 80% usage
- [ ] API response time > 5 seconds
- [ ] Error rate > 5%

## 🔄 Rollback Plan

### If Database Issues Occur
1. Stop the web service
2. Check database connection and credentials in Render dashboard
3. Verify table structure integrity
4. Restart with corrected configuration

### If Redis Issues Occur
1. Check Redis service status in Render
2. Verify connection string format
3. Test Redis operations manually
4. Restart Redis service if needed

### If Architecture Issues Occur
1. Check startup validation logs
2. Verify all required tables exist
3. Test PersonaAgent initialization
4. Check Redis session operations

## 📋 Validation Commands

### Pre-Deployment (Local with .env)
```bash
# Validate environment and configuration
python verify_render_deployment.py

# Test database migration
python migrate_database.py

# Test startup process
python startup.py
```

### Post-Deployment
```bash
# Check service health
curl https://your-app.onrender.com/health

# Monitor logs
# Check Render dashboard for service logs

# Test interview flow
# Use the frontend to create a test interview
```

## 🎯 Success Criteria

- [ ] All validation checks pass
- [ ] Health endpoint responding within 1 second
- [ ] Interview creation working end-to-end
- [ ] Redis session management functioning
- [ ] PostgreSQL persistence working
- [ ] Performance targets met (Router < 750ms, Generator < 3s)
- [ ] No critical errors in logs
- [ ] All required tables accessible
- [ ] JSONB operations working correctly

## 📞 Support and Troubleshooting

### Common Issues
1. **Database Connection Refused**: Check Render PostgreSQL service status
2. **Redis Connection Failed**: Check Render Redis service status
3. **Table Not Found**: Run migration script and check startup logs
4. **JSONB Field Errors**: Verify PostgreSQL version supports JSONB

### Debug Commands
```bash
# Check database connection
python -c "from models import get_engine; print(get_engine())"

# Test Redis connection
python -c "import redis; r = redis.from_url('$REDIS_URL'); print(r.ping())"

# Verify table structure
python -c "from models import Base; print([t.name for t in Base.metadata.tables.values()])"
```

## 🔐 Security Notes

- **Environment Variables**: All sensitive data is managed through Render's secure environment variable system
- **No Credentials in Code**: Never commit actual API keys or database credentials to version control
- **Render Security**: Render automatically handles SSL, connection encryption, and access control
- **Local Development**: Use separate .env file for local development (not committed to git)

---

**Last Updated**: $(date)
**Version**: 2.0 (New Architecture)
**Status**: Ready for Render Deployment
**Environment Variables**: Managed through Render Dashboard
