# Railway Configuration — Final Step

**Status:** Application ready. Waiting for DATABASE_URL injection.

---

## What to Set on Railway Dashboard

### Step 1: Access Backend Service Variables

1. Go to: https://railway.app/dashboard
2. Click **PartnerOpsAI** project
3. Click **Backend** service (GitHub icon)
4. Click **Variables** tab (should show existing vars like PORT)

### Step 2: Add PostgreSQL Connection

Create 3 new variables:

#### Variable 1: DATABASE_URL (Service Reference)
```
Name:  DATABASE_URL
Value: ${{Postgres.DATABASE_URL}}
```

**Why:** This tells Railway to inject the PostgreSQL service's connection string.

#### Variable 2: ENVIRONMENT
```
Name:  ENVIRONMENT
Value: production
```

#### Variable 3: DEBUG
```
Name:  DEBUG
Value: false
```

### Step 3: Deploy

Click **Deploy** button or wait for auto-redeploy on next git push.

---

## Verification

After Railway redeploys, run these curl commands:

### Test 1: Health (should already work)
```bash
curl https://partneropsai-production.up.railway.app/health
```
Expected: `{"status":"ok","service":"PartnerOpsAI Demo","version":"3.6.1"}`

### Test 2: Status (should already work)
```bash
curl https://partneropsai-production.up.railway.app/api/status
```
Expected: Service info with PostgreSQL database listed.

### Test 3: Seed Demo Data (currently fails, will work after config)
```bash
curl -X POST https://partneropsai-production.up.railway.app/api/seed-demo-data
```
Expected: `{"status":"ok","message":"Demo data seeded successfully"}`

### Test 4: Qualify a Company (currently fails, will work after config)
```bash
curl -X POST https://partneropsai-production.up.railway.app/api/qualify \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Acme Corp",
    "company_size_employees": 5000,
    "industry": "SaaS",
    "location": "US",
    "ai_maturity": "advanced",
    "security_maturity": "advanced",
    "icp_score": 85,
    "design_partner_potential": 90,
    "has_product_team": true
  }'
```
Expected: `{"opportunity_id":"...","qualification_score":82,"is_qualified_for_design_partner":true,"reasons":[...]}`

### Test 5: Get Opportunities (currently fails, will work after config)
```bash
curl https://partneropsai-production.up.railway.app/api/opportunities
```
Expected: List of opportunities (empty or with seeded data).

---

## Why This Matters

**Current State:**
- Backend code: ✅ 100% ready
- Database schema: ✅ Migrations ready
- API endpoints: ✅ 9 endpoints coded
- Tests: ✅ 55/61 passing locally
- Docker: ✅ Working
- Railway deployment: ✅ Live

**Missing:**
- DATABASE_URL environment variable: ⏳ Needs manual config

**After setting DATABASE_URL:**
- start.sh connects to Railway PostgreSQL
- Migrations run (tables created)
- Demo user initialized
- All 9 endpoints fully functional

---

## Expected Timeline

1. **Set variables:** 1 minute
2. **Railway redeploy:** 2-5 minutes
3. **Verify endpoints:** 1 minute
4. **Total:** ~5 minutes to full working demo

---

## What Railway Does Automatically

Once DATABASE_URL is set:
- Railway injects it into Backend container at startup
- start.sh reads it from environment
- Connects to Railway's PostgreSQL service
- Applies schema migrations
- Initializes demo data
- Starts FastAPI with all endpoints ready

---

## After Verification

Once all tests pass:
1. All 9 endpoints working ✅
2. Demo is production-ready ✅
3. Ready for recruiter submission ✅

Share: https://partneropsai-production.up.railway.app
