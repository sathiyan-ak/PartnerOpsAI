# Phase 3.6.5: DEPLOY NOW

**Status:** Ready. All files committed. Deploy to Railway.

**Time required:** 5 minutes

---

## What to Do

### 1. Go to Railway

Visit: https://railway.app

### 2. Connect GitHub

- Click "New Project"
- Select "Deploy from GitHub"
- Search for "PartnerOpsAI"
- Click "Deploy"

Railway auto-detects:
- ✅ Dockerfile (from repo root)
- ✅ PostgreSQL service (add from Railway dashboard)

### 3. Add PostgreSQL

- In Railway dashboard
- "Add Service" → "PostgreSQL"
- Railway provisions automatically
- DATABASE_URL auto-set in environment

### 4. Configure Environment

Backend service → Variables:

```
ENVIRONMENT=production
DEBUG=false
```

DATABASE_URL: Already set by PostgreSQL service

### 5. Deploy

Click "Deploy" button. Wait 2-3 minutes.

Watch logs:
```
Waiting for database...
Applying database migrations...
Initializing demo user...
Starting FastAPI server...
✓ Server running on 0.0.0.0:8000
```

### 6. Capture URL

Deployments → Copy domain

Example: `https://partneropsa-production-abc123.up.railway.app`

---

## Verify Deployment

After URL is live, run:

```bash
YOUR_URL="https://your-railway-url"

# Test health
curl $YOUR_URL/health
# Expected: {"status":"ok",...}

# Load demo data
curl -X POST $YOUR_URL/api/seed-demo-data
# Expected: {"status":"ok","message":"..."}

# Test qualification
curl -X POST $YOUR_URL/api/qualify \
  -H "Content-Type: application/json" \
  -d '{"company_name":"TestCorp","company_size_employees":5000,"industry":"Technology","location":"SF","ai_maturity":"advanced","security_maturity":"advanced","icp_score":85,"design_partner_potential":90,"has_product_team":true}'
# Expected: {"opportunity_id":"...","qualification_score":...}

# Verify script
./verify-deployment.sh $YOUR_URL
# Expected: "✓ All checks passed!"
```

---

## Share Demo

After verification:

**API Docs:** `https://your-url/docs` (Swagger UI)

**Share with:** Reviewers, recruiters, team

---

## Done

Submit with:
- Demo URL (https://your-url)
- PORTFOLIO.md
- GitHub repo link
- Test metrics (54/55 passing, 98%, 71.5% coverage)

That's it.
