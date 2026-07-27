# PartnerOpsAI Deployment Guide

Deploy the internship demo to public internet in ~10 minutes.

---

## Option 1: Railway (Recommended — 5 min setup)

**Why:** Simplest. Auto-scales. Includes free PostgreSQL.

### Step 1: Prepare Repository

```bash
cd ~/Developer/PartnerOpsAI
git add .
git commit -m "Phase 3.6.3: Deployment configuration"
git push origin main
```

Ensure repo is on GitHub: `https://github.com/USERNAME/PartnerOpsAI`

### Step 2: Connect Railway

1. Visit https://railway.app
2. Sign up / log in
3. Click "New Project" → "Deploy from GitHub"
4. Select `PartnerOpsAI` repository
5. Approve

### Step 3: Add Services

**Database:**
- Click "Add Service" → "PostgreSQL"
- Railway auto-provisions (stores URL in `DATABASE_URL`)

**Backend:**
- Already detected from `Dockerfile`
- Automatically builds and deploys

### Step 4: Configure Environment

In Railway dashboard → Variables:
```
ENVIRONMENT=production
DEBUG=false
```

`DATABASE_URL` auto-populated by PostgreSQL service.

### Step 5: Deploy

Click "Deploy" button. Wait ~2 min.

**Get URL:**
- Dashboard → Backend service → Domains
- Copy `https://xxxxx.railway.app`

### Step 6: Initialize Database

```bash
# Run migration on Railway PostgreSQL
RAILWAY_URL=$(echo "your-railway-url-here")

# Load schema
curl https://$RAILWAY_URL/health  # Verify it's up

# Seed demo data
curl -X POST https://$RAILWAY_URL/api/seed-demo-data
```

### Step 7: Test

```bash
# Health check
curl https://$RAILWAY_URL/health

# Swagger docs
open https://$RAILWAY_URL/docs

# Try qualification
curl -X POST https://$RAILWAY_URL/api/qualify \
  -H "Content-Type: application/json" \
  -d '{"company_name": "TestCorp", "company_size_employees": 5000, "industry": "Tech", "location": "SF", "ai_maturity": "advanced", "security_maturity": "advanced", "icp_score": 85, "design_partner_potential": 90, "has_product_team": true}'
```

**Done.** URL: `https://xxxxx.railway.app`

---

## Option 2: Fly.io (10 min setup)

**Why:** Good alternative if Railway down. Auto-scales globally.

### Step 1: Install Fly CLI

```bash
curl -L https://fly.io/install.sh | sh
flyctl auth login
```

### Step 2: Create App

```bash
cd ~/Developer/PartnerOpsAI
flyctl launch

# Prompts:
# App name: partneropsa-demo
# Region: sjc (or closest to you)
# Postgres: yes (creates database)
# Deploy: no (we'll do manually)
```

### Step 3: Deploy

```bash
flyctl deploy
```

Wait ~3 min. Get URL from output.

### Step 4: Initialize Database

```bash
# SSH into app
flyctl ssh console

# Inside container:
python -c "
import subprocess
subprocess.run(['psql', os.environ['DATABASE_URL'], '-f', '/app/backend/infrastructure/migrations/001_init_schema.sql'])
"

# Or run from local machine:
flyctl proxy 5432 -a partneropsa-demo
psql postgresql://user:pass@localhost:5432/partneropsa < backend/infrastructure/migrations/001_init_schema.sql
```

### Step 5: Seed Data

```bash
curl -X POST https://partneropsa-demo.fly.dev/api/seed-demo-data
```

### Step 6: Test

```bash
curl https://partneropsa-demo.fly.dev/health
open https://partneropsa-demo.fly.dev/docs
```

**Done.** URL: `https://partneropsa-demo.fly.dev`

---

## Option 3: AWS (15 min setup)

**Why:** Most control. Scales to millions of requests.

### Step 1: Create ECR Repository

```bash
aws ecr create-repository --repository-name partneropsa --region us-east-1

# Output: repository URI (e.g., 123456789.dkr.ecr.us-east-1.amazonaws.com/partneropsa)
```

### Step 2: Build & Push Image

```bash
# Authenticate Docker to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

# Build and tag
docker build -t partneropsa:latest .
docker tag partneropsa:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/partneropsa:latest

# Push
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/partneropsa:latest
```

### Step 3: Create RDS PostgreSQL

```bash
# Via AWS Console or CLI:
aws rds create-db-instance \
  --db-instance-identifier partneropsa-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password [STRONG_PASSWORD] \
  --allocated-storage 20 \
  --region us-east-1
```

Wait ~5 min for database.

### Step 4: Create ECS Cluster

Use AWS Console → ECS → Create Cluster (Fargate).

### Step 5: Deploy Container

Create Task Definition:
- Image: ECR URI (from Step 2)
- CPU: 256
- Memory: 512
- Port: 8000

Environment Variables:
```
DATABASE_URL=postgresql://admin:PASSWORD@endpoint:5432/partneropsa
ENVIRONMENT=production
```

Create Service:
- Cluster: partneropsa
- Task Definition: partneropsa
- Desired Count: 1
- Load Balancer: Application Load Balancer

### Step 6: Run Migration

```bash
# Via ECS Exec:
aws ecs execute-command --cluster partneropsa --task [TASK_ID] --container partneropsa --interactive --command "/bin/bash"

# Inside:
psql $DATABASE_URL -f /app/backend/infrastructure/migrations/001_init_schema.sql
```

### Step 7: Get URL

AWS Console → ECS → Service → Load Balancer → DNS name

**Done.** URL: `http://partneropsa-alb-xxxxx.us-east-1.elb.amazonaws.com`

---

## Verify Deployment

All platforms: Run this checklist.

### 1. Health Check
```bash
curl https://YOUR_URL/health
# Expected: {"status":"ok","service":"PartnerOpsAI Demo","version":"3.6.1"}
```

### 2. Swagger Docs
```bash
open https://YOUR_URL/docs
# Should load interactive API documentation
```

### 3. Service Status
```bash
curl https://YOUR_URL/api/status
# Expected: version, phase, features, database
```

### 4. Qualification (Without Seed Data)
```bash
curl -X POST https://YOUR_URL/api/qualify \
  -H "Content-Type: application/json" \
  -d '{"company_name":"TestCorp","company_size_employees":5000,"industry":"Technology","location":"San Francisco","ai_maturity":"advanced","security_maturity":"advanced","icp_score":85,"design_partner_potential":90,"has_product_team":true}'

# Expected: opportunity_id + qualification_score + is_qualified_for_design_partner
```

### 5. Load Demo Data
```bash
curl -X POST https://YOUR_URL/api/seed-demo-data
# Expected: {"status":"ok","message":"Demo data seeded successfully"}
```

### 6. Retrieve Demo Opportunity
```bash
# First, seed data to get opportunity_id
curl -X POST https://YOUR_URL/api/seed-demo-data

# Then use the Acme Corp ID from seed response:
curl https://YOUR_URL/api/opportunities/[ACME_ID]
```

### 7. View Audit Trail
```bash
curl https://YOUR_URL/api/audit/[ACME_ID]
# Expected: audit_entries array with 6 events
```

---

## Troubleshooting

### "Connection refused" / "Cannot reach database"
- Verify DATABASE_URL is set correctly
- Check database is running and accessible from container
- Verify security groups / firewalls allow inbound connections

### "Module not found: backend"
- Ensure PYTHONPATH includes app root
- Verify Dockerfile COPY command includes all files
- Check working directory in container

### "Port already in use"
- Railway/Fly auto-select available port
- Locally: change to different port: `--port 8001`

### "Migration fails"
- Verify DATABASE_URL format: `postgresql://user:pass@host:port/db`
- Ensure database exists (create if needed)
- Check schema file path is correct

### Tests fail after deployment
- Tests run against local PostgreSQL
- Deployment runs against cloud PostgreSQL
- If cloud DB differs, run seed endpoint via curl

---

## Monitoring & Logs

### Railway
```bash
# View logs
flyctl logs -a partneropsa

# Or via dashboard: Deployments → Logs
```

### Fly.io
```bash
flyctl logs -a partneropsa-demo
```

### AWS ECS
```bash
aws logs tail /ecs/partneropsa --follow
```

---

## Update Deployment

After code changes:

### Railway
```bash
git push origin main
# Auto-redeploys from main branch
```

### Fly.io
```bash
git push origin main
flyctl deploy
```

### AWS
```bash
docker build -t partneropsa:latest .
docker tag partneropsa:latest [ECR_URI]:latest
docker push [ECR_URI]:latest

# Update ECS service to redeploy
aws ecs update-service --cluster partneropsa --service partneropsa --force-new-deployment
```

---

## Costs

| Platform | Free Tier | After |
|---|---|---|
| Railway | $5/month | Pay-as-you-go (~$10-50/month for demo) |
| Fly.io | $5/month + free DB | Pay-as-you-go (~$10-30/month) |
| AWS | 12 months free (limited) | T3.micro ~$10/month + RDS ~$20/month |

**Recommendation:** Use Railway for internship demo. Cheapest. Simplest.

---

## Summary

| Step | Railway | Fly.io | AWS |
|---|---|---|---|
| Setup | 2 min | 5 min | 10 min |
| Deploy | Click button | `flyctl deploy` | ECR + ECS |
| Database | Auto-provisioned | Auto-provisioned | Manual RDS |
| Monitoring | Dashboard | CLI | CloudWatch |
| Cost | $5+/month | $5+/month | $30+/month |
| Complexity | Easiest | Easy | Hard |

**Choose Railway. 5 minutes to live URL.**

---

## After Deployment

1. **Test with curl** (above checklist)
2. **Share URL** with recruiters
3. **Update PORTFOLIO.md** with live link
4. **Add screenshots** (localhost, then public)
5. **Monitor logs** for errors
6. **Celebrate 🎉** — demo is live
