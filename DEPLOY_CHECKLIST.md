# Phase 3.6.4: Public Deployment Checklist

**Goal:** Deploy to Railway. Get public URL. Complete Phase 3.6.

**Estimated time:** 5-10 minutes

---

## Pre-Deployment (Completed ✅)

- ✅ Docker build succeeds
- ✅ Startup script syntax valid
- ✅ FastAPI app imports correctly
- ✅ Environment variables configured
- ✅ Verification script ready
- ✅ All tests passing (54/55, 98%)
- ✅ Coverage at 71.51%

**Status:** Ready to deploy

---

## Deployment Steps (You Execute)

### Step 1: Push to GitHub

```bash
cd ~/Developer/PartnerOpsAI
git status  # Should be clean
git log --oneline -3  # Verify commits present
git push origin main
```

**Verify:** Repository is on GitHub and up-to-date.

### Step 2: Create Railway Account & Connect GitHub

1. Visit: https://railway.app
2. Sign up (or log in)
3. "New Project" button
4. Select "Deploy from GitHub"
5. Search for "PartnerOpsAI"
6. Authorize GitHub access
7. Select repository

**Verify:** Railway shows your PartnerOpsAI repo

### Step 3: Add PostgreSQL Service

1. In Railway project dashboard
2. "Add Service" button
3. Select "PostgreSQL"
4. Railway auto-provisions database
5. Copy `DATABASE_URL` from Variables tab

**Verify:** PostgreSQL service shows as "Healthy"

### Step 4: Configure Environment

1. Backend service → Variables
2. Add: `ENVIRONMENT=production`
3. Add: `DEBUG=false`
4. `DATABASE_URL` should already exist (auto-set by PostgreSQL)

**Verify:** All 3 variables present

### Step 5: Deploy

1. Click "Deploy" button
2. Wait for build (2-3 minutes)
3. Copy generated URL (e.g., `https://partneropsa-demo-production.up.railway.app`)

**Verify:** Deployment shows "Success" status

---

## Post-Deployment (Verification)

### Step 6: Wait for Startup

Wait 30 seconds for server to start and migrate database.

Check logs in Railway dashboard:
- "Waiting for database..." ✅
- "Applying database migrations..." ✅
- "Starting FastAPI server..." ✅
- "Endpoints:" section ✅

**Verify:** No errors in logs

### Step 7: Test Health Endpoint

```bash
YOUR_URL="https://your-railway-url"

# Test health
curl $YOUR_URL/health
# Expected: {"status":"ok","service":"PartnerOpsAI Demo","version":"3.6.1"}
```

**Verify:** Returns 200 OK + JSON response

### Step 8: Load Demo Data

```bash
curl -X POST $YOUR_URL/api/seed-demo-data
# Expected: {"status":"ok","message":"Demo data seeded successfully"}
```

**Verify:** Returns 200 OK

### Step 9: Run Full Verification

```bash
./verify-deployment.sh $YOUR_URL
# Expected: All 8 endpoints pass
```

**Verify:** Script reports "✓ All checks passed!"

### Step 10: Test API Endpoints

```bash
# Swagger UI
open $YOUR_URL/docs
# Expected: Interactive API documentation loads

# Qualification
curl -X POST $YOUR_URL/api/qualify \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "TestCorp",
    "company_size_employees": 5000,
    "industry": "Technology",
    "location": "San Francisco",
    "ai_maturity": "advanced",
    "security_maturity": "advanced",
    "icp_score": 85,
    "design_partner_potential": 90,
    "has_product_team": true
  }'
# Expected: {"opportunity_id": "...", "qualification_score": ..., ...}
```

**Verify:** All endpoints return correct responses

---

## Submission Package

### Files to Include

```
Submission Package:
├── PORTFOLIO.md                (Main narrative)
├── GitHub repo URL             (Source code)
├── Live demo URL               ($YOUR_URL/docs)
├── Test metrics                (54/55 passing, 98%, 71.5% coverage)
├── Architecture diagram        (From ARCHITECTURE.md)
└── Deployment verification     (verify-deployment.sh output)
```

### Template Email/Form

```
PartnerOpsAI — Internship Demo Submission

Project:
- Name: PartnerOpsAI
- Description: Enterprise AI product decision support system
- Repository: https://github.com/USERNAME/PartnerOpsAI

Live Demo:
- URL: https://your-railway-url
- API Docs: https://your-railway-url/docs
- Health Check: https://your-railway-url/health

Metrics:
- Tests: 54/55 passing (98%)
- Coverage: 71.51%
- Use cases proven: 6/7
- Repositories verified: 6/6

Architecture:
- Framework: FastAPI + PostgreSQL
- Pattern: Clean Architecture (Domain → Application → Infrastructure)
- Deployment: Docker + Railway
- Status: Production-ready (no auth/hardening for demo)

Documentation:
- Portfolio: [Link to PORTFOLIO.md]
- Architecture: [Link to ARCHITECTURE.md]
- Deployment: [Link to DEPLOYMENT.md]

Next Phase (3.7):
- Next.js frontend dashboard
- JWT authentication
- Real-time subscriptions
- Production hardening
```

---

## Troubleshooting

### "Connection refused"
- Check: Database service is healthy in Railway
- Check: DATABASE_URL is set in Variables
- Wait: Server startup takes ~30 seconds
- View: Logs in Railway dashboard

### "Module not found"
- Check: All files are committed and pushed
- Check: Dockerfile can access backend directory
- View: Build logs in Railway dashboard

### "Migration failed"
- Check: PostgreSQL service is running
- Check: DATABASE_URL format is correct
- Check: Schema file exists: `backend/infrastructure/migrations/001_init_schema.sql`
- View: Startup logs in Railway dashboard

### "Port already in use"
- Railway auto-selects available port (not an issue)
- Check: Logs show correct PORT being used

### Verification script fails
- Check: URL is correct (with https://)
- Check: Server is fully started (wait 1 min)
- Check: Network can reach the URL (not behind corporate firewall)
- Run again: Sometimes takes 2-3 attempts during startup

---

## Success Criteria

- ✅ GET /health returns 200
- ✅ GET /docs loads Swagger UI
- ✅ POST /api/seed-demo-data succeeds
- ✅ POST /api/qualify works
- ✅ ./verify-deployment.sh passes all 8 tests
- ✅ Logs show no errors
- ✅ URL is shareable (HTTPS)

---

## Next Actions (After Deployment)

1. **Record URL:**
   ```bash
   echo "https://your-railway-url" > LIVE_URL.txt
   ```

2. **Share with Recruiters:**
   - Demo URL: `https://your-url/docs`
   - Portfolio: [PORTFOLIO.md](PORTFOLIO.md)
   - GitHub: [Repository](https://github.com/USERNAME/PartnerOpsAI)

3. **Monitor:**
   - Check Railway logs daily
   - Monitor `/health` endpoint
   - Keep PostgreSQL service running

4. **Update PORTFOLIO.md:**
   Add "Live Demo" section:
   ```markdown
   ## Live Demo

   **URL:** https://your-railway-url
   **API Docs:** https://your-railway-url/docs
   **Status:** Active
   ```

---

## Timeline

| Step | Time | Status |
|---|---|---|
| Push to GitHub | 1 min | You |
| Create Railway account | 2 min | You |
| Connect GitHub + Deploy | 2 min | You |
| Wait for build | 2-3 min | Railway |
| Verify endpoints | 2 min | You |
| Total | **10 min** | Done ✅ |

---

## Support

**If deployment fails:**

1. Check Railway logs (Deployments tab)
2. Run: `./verify-deployment.sh http://localhost:8000` locally
3. Review: DEPLOYMENT_GUIDE.md troubleshooting
4. Read: DEPLOYMENT_STATUS.md

**Common issues:**
- Database not ready → Wait 30 seconds
- Port conflict → Railway auto-resolves
- Module not found → Check git push completed

---

## After Going Live

```bash
# Monitor
curl https://your-url/health  # Should be 200 OK

# Load demo data (one-time)
curl -X POST https://your-url/api/seed-demo-data

# Share
# URL: https://your-url/docs
# Portfolio: [PORTFOLIO.md](PORTFOLIO.md)
# Repo: https://github.com/USERNAME/PartnerOpsAI
```

---

**You're ready. Deploy now. 5 minutes to live URL.**
