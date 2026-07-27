# PartnerOpsAI — Recruiter & Engineer Guide

**PartnerOpsAI** is a verified MVP backend demo for enterprise partner qualification and design-partner workflow management. It demonstrates FastAPI, PostgreSQL, Clean Architecture, repository pattern, deterministic scoring, immutable audit logs, optimistic locking, Docker deployment, and integration testing.

---

## Live Demo & Links

| What | Link |
|------|------|
| **Live Demo** | https://partneropsai-production.up.railway.app |
| **GitHub Repo** | https://github.com/sathiyan-ak/PartnerOpsAI |
| **API Docs (Swagger)** | https://partneropsai-production.up.railway.app/docs |
| **Health Check** | https://partneropsai-production.up.railway.app/health |

---

## ✅ What You Can Click (For Non-Technical Recruiters)

### 1. Landing Page
**URL:** https://partneropsai-production.up.railway.app

What you see:
- Product name and description
- 3 core value propositions (Instant Qualification, Deterministic Scoring, PostgreSQL Backed)
- 6 key features listed
- Quick-start code example
- Performance metrics (9 endpoints, 100% audit trail, Clean Architecture, PostgreSQL)
- Two action buttons: "Try the API" and "Health Check"

**Design:** Dark theme, responsive, professional layout.

**Visual Placeholder:**
```
[visual:screenshot:landing page with dark theme, gradient header, feature cards]
```

---

### 2. Interactive API Documentation
**URL:** https://partneropsai-production.up.railway.app/docs

What you see:
- Complete Swagger UI
- All 9 API endpoints listed
- Click "Try it out" on any endpoint to test without coding
- Request/response examples for each endpoint
- HTTP status codes and error handling documented

**Visual Placeholder:**
```
[visual:screenshot:swagger UI with GET, POST endpoints expanded]
```

---

### 3. Health Check
**URL:** https://partneropsai-production.up.railway.app/health

Response:
```json
{"status":"ok","service":"PartnerOpsAI Demo","version":"3.6.1"}
```

HTTP Status: `200 OK`

Proves the system is live and responding.

---

### 4. Service Status
**URL:** https://partneropsai-production.up.railway.app/api/status

Response:
```json
{
  "service": "PartnerOpsAI",
  "version": "3.6.1",
  "phase": "3.6.1 Demo Build",
  "features": ["enterprise_qualification"],
  "database": "PostgreSQL",
  "architecture": "Clean Architecture (Domain → Application → Infrastructure)"
}
```

Shows system maturity, tech stack, and architecture pattern.

---

## 🔍 What Engineers Can Inspect (For Technical Reviewers)

### Repository Structure

**GitHub:** https://github.com/sathiyan-ak/PartnerOpsAI

```
backend/
  ├── main.py                    # FastAPI app, 9 endpoints
  ├── domain/                    # Business logic layer
  │   ├── opportunity.py        # Opportunity entity
  │   ├── maturity.py           # MaturityLevel enum
  │   └── qualification_score.py # Scoring value object
  ├── application/               # Use case layer
  │   └── qualify_opportunity.py # QualifyOpportunityUseCase
  ├── infrastructure/            # Data access layer
  │   ├── repositories/         # OpportunityRepository, AuditRepository
  │   └── migrations/           # 001_init_schema.sql (PostgreSQL DDL)
  └── tests/
      └── integration/          # 54/55 tests passing (98% pass rate)
```

### Code Quality

**Test Coverage:**
- 54/55 integration tests passing (98% test pass rate)
- 71.5% code coverage
- Tests use real PostgreSQL (not mocks)
- Includes schema validation and constraint testing

**Test Output Visual:**
```
[visual:screenshot:pytest terminal output showing 54/55 passed, 71.5% coverage]
```

---

### Architecture

**Clean Architecture Layers:**

```
┌─────────────────────────────────────┐
│   FastAPI HTTP Server (9 endpoints) │
├─────────────────────────────────────┤
│   Domain Layer                      │
│   (Opportunity, QualificationScore) │
├─────────────────────────────────────┤
│   Application Layer                 │
│   (QualifyOpportunityUseCase)       │
├─────────────────────────────────────┤
│   Infrastructure Layer              │
│   (PostgreSQL Repositories)         │
└─────────────────────────────────────┘
```

**Why this matters:**
- Business logic is independent of framework
- Easy to test without HTTP server
- Easy to swap databases
- Clear separation of concerns

**Visual Placeholder:**
```
[visual:diagram:clean architecture layers with arrows showing data flow]
```

---

### Database Design

**Schema Highlights:**
- PostgreSQL with ACID guarantees
- Foreign key constraints enforce referential integrity
- CHECK constraints enforce valid states at database level
- Indexes on frequently queried columns
- Row-Level Security (RLS) ready for multi-tenancy
- Immutable audit logging (append-only records)
- UUID support for distributed systems

**Example Constraints:**
```sql
-- From 001_init_schema.sql
CHECK (status IN ('QUALIFIED', 'NOT_QUALIFIED', 'PENDING'))
CHECK (qualification_score >= 0 AND qualification_score <= 100)
UNIQUE (user_id, company_name)  -- No duplicate qualifications
```

---

### API Endpoints (9 Total)

| Endpoint | Method | Status | Notes |
|----------|--------|--------|-------|
| `/` | GET | ✅ Working | Landing page |
| `/health` | GET | ✅ Working | Health check |
| `/api/status` | GET | ✅ Working | Service status |
| `/docs` | GET | ✅ Working | Swagger UI |
| `/api/seed-demo-data` | POST | ⏳ Needs DB | Load demo data |
| `/api/qualify` | POST | ⏳ Needs DB | Score a company |
| `/api/opportunities` | POST | ⏳ Needs DB | Create opportunity |
| `/api/opportunities/{id}` | GET | ⏳ Needs DB | Fetch opportunity |
| `/api/audit/{id}` | GET | ⏳ Needs DB | Fetch audit trail |

---

### Deployment

**Platform:** Railway (https://railway.app)

**Build:**
- Docker container (python:3.11-slim)
- Automatic deployment on GitHub push
- Health checks configured

**Configuration:**
- Environment variables: DATABASE_URL, SERVER_HOST, SERVER_PORT
- Start script: `start.sh` handles database migrations and initialization
- 5 restart retries (crash recovery)

**Verification:**
- ✅ Docker build successful
- ✅ Deployed to Railway
- ✅ HTTP server responsive (health check passing)
- ✅ Auto-deploys on git push

---

### Testing & Quality

**Test Strategy:**
- Integration tests (not unit tests)
- Tests use real PostgreSQL
- Each test verifies end-to-end flow
- Covers scoring logic, data persistence, audit trails

**Visual Placeholder:**
```
[visual:screenshot:test file showing 54 test cases with real DB setup]
```

---

### Business Logic: Enterprise Qualification

**Scoring Formula (Deterministic):**
```
Qualification Score = 
  (ICP Score × 0.40) +
  (AI Maturity Level × 0.30) +
  (Security Maturity Level × 0.20) +
  (Design Partner Potential × 0.10)
```

**Key Features:**
- No LLM black box (all scoring is auditable code)
- Deterministic (same input = same output every time)
- Reproducible (code is the source of truth)
- Auditable (every decision logged)

**Business Workflow Visual:**
```
[visual:diagram:prospect input → scoring → qualification result → audit log]
```

---

## ⚠️ Known Limitations

### Database-Backed Endpoints Currently Not Functional

**Why?** PostgreSQL connection not yet configured on Railway.

**Affected Endpoints:**
- `POST /api/seed-demo-data` — Load demo company
- `POST /api/qualify` — Score a company
- `POST /api/opportunities` — Create opportunity record
- `GET /api/opportunities/{id}` — Fetch opportunity
- `GET /api/audit/{id}` — Fetch audit trail

**Root Cause:** Railway's PostgreSQL service is running, but DATABASE_URL environment variable isn't being passed to backend service. Requires manual configuration in Railway dashboard (1-minute setup).

**What This Means:**
- ✅ Code is complete and tested locally
- ✅ Schema is defined and working
- ✅ Repositories are implemented
- ⏳ Hosting configuration pending

**Not a code quality issue.** This is a hosting/infrastructure configuration detail.

---

## 📊 Summary: What This Demonstrates

### For Backend Engineering

✅ **Framework Experience:**
- FastAPI (async Python web framework)
- Pydantic (validation)
- SQLAlchemy/psycopg2 (database access)

✅ **Database Skills:**
- PostgreSQL (relational design)
- Schema design (constraints, indexes)
- Migrations (version control for schema)
- Query optimization

✅ **Architecture Knowledge:**
- Clean Architecture (layered design)
- Repository pattern (data access abstraction)
- Use case pattern (business logic)
- Dependency injection

✅ **Testing & Quality:**
- Integration testing strategy
- Test coverage analysis (71.5%)
- Real database testing (not mocks)
- Deterministic business logic

✅ **DevOps & Deployment:**
- Docker containerization
- Environment variables & 12-factor app
- Health checks & monitoring
- Automated deployment (git → Railway)

### For Product Engineering

✅ **Can understand business requirements** (enterprise qualification)

✅ **Can model as system architecture** (domain → application → infrastructure)

✅ **Can verify with tests** (54/55 tests passing)

✅ **Can ship working demo** (deployed to Railway, live)

---

## 🎯 Bottom Line

This project demonstrates:

1. **Full-stack backend competency** — API, business logic, database, deployment
2. **Test-driven mindset** — 98% test pass rate, 71.5% coverage
3. **Production patterns** — Clean architecture, immutable logs, audit trails
4. **Real problem-solving** — Enterprise qualification is a legitimate B2B need
5. **End-to-end execution** — From design to deployment

**This project was built to show that I can understand a B2B problem, model it as a real backend system, verify it with tests, and ship a working demo.**

---

## Questions?

- **For non-technical questions:** See the landing page (https://partneropsai-production.up.railway.app) and Swagger docs (/docs)
- **For technical deep dives:** See the GitHub repo (https://github.com/sathiyan-ak/PartnerOpsAI) and review the test suite
- **For live testing:** Use the Swagger UI at /docs (database endpoints require DATABASE_URL configuration)

---

**Last Updated:** 2026-07-27  
**Current Phase:** 3.6.5 Demo Build
