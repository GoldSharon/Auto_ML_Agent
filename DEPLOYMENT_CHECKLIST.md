# AutoML Platform - Deployment Checklist

## Pre-Deployment Verification

### Step 1: Environment Setup ✓
- [ ] Python 3.10+ installed
- [ ] Node.js 18+ installed
- [ ] Git configured
- [ ] Google API key obtained from https://ai.google.dev

### Step 2: Local Testing ✓

**Backend Tests:**
```bash
cd backend
pip install -r requirements.txt
python main.py
# Should show "Uvicorn running on http://0.0.0.0:8000"
# Visit http://localhost:8000/docs in browser
```
- [ ] Backend starts without errors
- [ ] Swagger UI accessible at /docs
- [ ] Health check works: http://localhost:8000/api/health

**Frontend Tests:**
```bash
npm install
npm run dev
# Should show "Local:   http://localhost:3000"
```
- [ ] Frontend starts without errors
- [ ] Can access http://localhost:3000
- [ ] No console errors in DevTools

**End-to-End Tests:**
- [ ] Upload test CSV (included in examples/)
- [ ] System detects data correctly
- [ ] LLM can be configured
- [ ] Training starts and shows progress
- [ ] Results are saved
- [ ] Can view projects list
- [ ] Can make predictions

### Step 3: Configuration Validation ✓

**Environment Variables:**
```bash
# Check .env file exists
ls -la .env

# Verify required variables
grep "LLM_MODEL_NAME" .env
grep "LLM_API_KEY" .env
grep "NEXT_PUBLIC_API_URL" .env
```
- [ ] .env file exists
- [ ] LLM_MODEL_NAME is set
- [ ] LLM_API_KEY is valid (test with curl)
- [ ] NEXT_PUBLIC_API_URL points to backend

**Backend Configuration:**
- [ ] All ML modules imported successfully
- [ ] GPU detection working (if applicable)
- [ ] File permissions set correctly
- [ ] projects/ directory is writable

**Frontend Configuration:**
- [ ] Environment variables loaded
- [ ] API_URL configured correctly
- [ ] Build succeeds: `npm run build`

### Step 4: Data Verification ✓

**Test Datasets:**
- [ ] Sample CSV files in examples/
- [ ] Variety of data types (numeric, categorical)
- [ ] Include missing values for testing
- [ ] Different file sizes (small, medium, large)

**Preprocessing Validation:**
- [ ] Missing value handling works
- [ ] Categorical encoding produces expected output
- [ ] Feature scaling doesn't cause errors
- [ ] Model training completes successfully

### Step 5: Error Handling ✓

**Simulate Common Errors:**
- [ ] Upload invalid CSV → get clear error
- [ ] Missing target column → validation error
- [ ] Invalid API key → caught and reported
- [ ] Network disconnect → graceful handling
- [ ] Out of memory (if possible) → fallback to CPU
- [ ] Training interruption → can be resumed

### Step 6: Performance Baselines ✓

**Measure Typical Performance:**
- [ ] Small dataset (1K rows): < 2 minutes
- [ ] Medium dataset (10K rows): < 10 minutes
- [ ] GPU speed-up verified (if GPU available)
- [ ] Memory usage reasonable
- [ ] CPU usage acceptable

### Step 7: Security Verification ✓

**API Security:**
- [ ] CORS configured properly
- [ ] No sensitive data in logs
- [ ] API keys not exposed in frontend
- [ ] WebSocket connection secure (wss:// in prod)
- [ ] File upload validation in place

**Data Security:**
- [ ] User data isolated in projects/
- [ ] Models saved securely
- [ ] No credentials in git history
- [ ] .env file in .gitignore

**Code Security:**
- [ ] No SQL injection vulnerabilities
- [ ] Input validation on all endpoints
- [ ] File path traversal prevention
- [ ] Command injection prevention

## Deployment Scenarios

### Scenario A: Local Development
```bash
# Start both servers
./start.sh  # Linux/Mac
# or
start.bat   # Windows

# Run on localhost
Frontend: http://localhost:3000
Backend: http://localhost:8000
```

**Checklist:**
- [ ] Both processes running
- [ ] Can access both URLs
- [ ] WebSocket working
- [ ] Models saving to projects/

### Scenario B: Docker Local
```bash
docker-compose up

# Access via
Frontend: http://localhost:3000
Backend: http://localhost:8000
```

**Checklist:**
- [ ] Images build successfully
- [ ] Containers start without errors
- [ ] Network between containers works
- [ ] Volumes mounted correctly
- [ ] .env loaded into containers

### Scenario C: Production Deployment

#### Frontend (Vercel)
```bash
npm run build
vercel deploy
```

**Checklist:**
- [ ] Build succeeds locally
- [ ] No TypeScript errors
- [ ] Environment variables set in Vercel
- [ ] NEXT_PUBLIC_API_URL points to prod backend
- [ ] Deployment successful
- [ ] Frontend accessible
- [ ] Can connect to backend

#### Backend (Cloud Platform - Example: Railway)
```bash
# 1. Push to GitHub
git add .
git commit -m "Deploy AutoML"
git push origin main

# 2. Connect to Railway
# - Create new project
# - Connect GitHub repo
# - Set environment variables

# 3. Verify
# - Backend running
# - Health check passing
# - Models folder writable
```

**Checklist:**
- [ ] Repository pushed to GitHub
- [ ] Platform project created
- [ ] Environment variables set:
  - [ ] LLM_MODEL_NAME
  - [ ] LLM_API_KEY
  - [ ] NEXT_PUBLIC_API_URL (if needed)
- [ ] Deployment successful
- [ ] Backend accessible at production URL
- [ ] Database/storage configured (if using)
- [ ] Health check endpoint working

### Scenario D: Hybrid (Frontend on Vercel, Backend on Server)
```bash
# Frontend on Vercel (see Scenario C)

# Backend on your server (e.g., DigitalOcean, AWS EC2)
# 1. SSH into server
ssh user@your-server.com

# 2. Clone repo and setup
git clone your-repo
cd automl-platform/backend
pip install -r requirements.txt

# 3. Create systemd service
sudo nano /etc/systemd/system/automl.service
# [Service]
# ExecStart=/usr/bin/python3 /home/user/automl-platform/backend/main.py
# WorkingDirectory=/home/user/automl-platform/backend

# 4. Start service
sudo systemctl start automl
sudo systemctl enable automl

# 5. Setup reverse proxy (nginx/Apache)
# Point domain/server:8000 to application
```

**Checklist:**
- [ ] Server provisioned and accessible
- [ ] Python dependencies installed
- [ ] .env configured with LLM keys
- [ ] Backend running via systemd
- [ ] Reverse proxy configured
- [ ] SSL certificate installed
- [ ] Firewall allows port 8000 (or proxied port)
- [ ] Frontend updated with correct backend URL

## Post-Deployment Testing

### API Endpoints Verification
```bash
# Test health
curl http://your-backend-url/api/health

# Test LLM status  
curl http://your-backend-url/api/env-status

# Test Swagger UI
# Visit: http://your-backend-url/docs
```

**Checklist:**
- [ ] GET /api/health returns 200
- [ ] GET /api/env-status shows correct config
- [ ] Swagger UI accessible
- [ ] Can make test request via Swagger

### Full Workflow Test
1. [ ] Upload test CSV from frontend
2. [ ] Analyze data
3. [ ] Configure training
4. [ ] Watch progress via WebSocket
5. [ ] Download results
6. [ ] View project in history
7. [ ] Make predictions

### Performance Monitoring
- [ ] Response times acceptable
- [ ] No memory leaks (check over time)
- [ ] CPU usage reasonable
- [ ] GPU utilization (if applicable)
- [ ] Disk space available for projects/

### Error Scenarios
- [ ] Invalid CSV upload → clear error
- [ ] Missing LLM key → helpful message
- [ ] Network timeout → proper handling
- [ ] Large dataset → doesn't crash
- [ ] Simultaneous requests → queued properly

## Rollback Plan

If something goes wrong in production:

### Immediate Actions
1. [ ] Check error logs
2. [ ] Verify database/storage connectivity
3. [ ] Check LLM API status
4. [ ] Verify GPU/memory availability

### Rollback Steps
```bash
# If using Git
git revert <commit-hash>
git push

# If using Docker
docker-compose down
docker pull latest-image
docker-compose up

# If using cloud platform
# - Go to deployment history
# - Click "Rollback" on previous working version
```

**Checklist:**
- [ ] Have rollback commit/version ready
- [ ] Previous version tested and known to work
- [ ] Rollback procedure documented
- [ ] Database backups available (if applicable)

## Maintenance Schedule

### Daily
- [ ] Monitor error logs
- [ ] Check disk space
- [ ] Verify API endpoints responding

### Weekly
- [ ] Review project counts and sizes
- [ ] Check performance metrics
- [ ] Test backup/recovery (if applicable)

### Monthly
- [ ] Update dependencies
- [ ] Review security logs
- [ ] Optimize database (if using)
- [ ] Update documentation

## Monitoring & Alerts

### Setup Monitoring
- [ ] Backend health checks (automated)
- [ ] API response time tracking
- [ ] Error rate monitoring
- [ ] Disk space alerts
- [ ] GPU memory monitoring (if applicable)

### Recommended Tools
- **Application Monitoring**: Sentry, DataDog
- **Infrastructure**: Prometheus, Grafana
- **Logs**: ELK Stack, CloudWatch, Papertrail
- **Uptime**: UptimeRobot, Pingdom

## Security Hardening

### Pre-Production
- [ ] API key rotation schedule
- [ ] Rate limiting configured
- [ ] CORS properly restricted
- [ ] Input validation comprehensive
- [ ] HTTPS/TLS enabled
- [ ] Security headers configured

### Post-Deployment
- [ ] Monitor for suspicious activity
- [ ] Regular security audits
- [ ] Dependency vulnerability scanning
- [ ] Access logs reviewed regularly

## Documentation Deployed
- [ ] README.md accessible
- [ ] API docs at /docs endpoint
- [ ] Setup guide included
- [ ] Troubleshooting guide provided
- [ ] Contact/support info available

## Sign-Off

- [ ] All tests passed
- [ ] Performance acceptable
- [ ] Security verified
- [ ] Team trained on system
- [ ] Monitoring configured
- [ ] Documentation complete
- [ ] Rollback plan ready
- [ ] **READY FOR PRODUCTION** ✓

---

**Date Deployed:** _______________
**Deployed By:** _______________
**Environment:** Development / Staging / Production
**Notes:** 

---

Once you've checked all boxes above, your AutoML platform is ready for production use!
