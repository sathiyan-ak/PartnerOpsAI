# PartnerOpsAI

**Enterprise AI product decision support system for Series A startup.**

Turns customer feedback → Prioritized product work → Mock release planning.

---

## What This Is

A premium dashboard that helps founders, PMs, and legal teams make better product decisions faster.

**Three integrated capabilities:**
1. Enterprise Prospect Intelligence — Capture deal context + risk factors
2. AI Governance Pipeline — Process + score compliance actions
3. Design Partner Portal — Aggregate feedback → priority recommendations

**Not:**
- A ticketing system
- A feedback collector
- A generic survey tool

**Yes:**
- A decision engine
- Deterministic scoring
- Real-time collaboration
- Audit-logged every change

---

## Why It Exists

Founders drown in customer feedback. No signal/noise. No duplication detection. No business impact scoring. No release reasoning.

PartnerOpsAI automates decision support so you can ship faster.

---

## Why Use PartnerOpsAI?

**Problem:** Founders spend 40+ hours/week processing customer feedback, governance requests, and deal context manually. No signal/noise. No priority. No release timeline.

**Solution:** PartnerOpsAI automates decision support. Feed customer feedback → Get prioritized recommendations with reasoning → Make better product decisions faster.

**Time saved:** 5+ hours/week per founder (conservative).

---

## Architecture Overview

**Three independent layers:**

```
Frontend (Next.js + React)
    ↓
Backend API (FastAPI)
    ↓
Database (Supabase Postgres)
    ↓
LLM Provider (Groq/OpenAI/Anthropic)
```

**Key principles:**
- Deterministic scoring (business logic, not AI)
- AI for categorization + explanation only
- Provider-agnostic LLM abstraction
- RLS for data isolation
- FastAPI for business logic (independent of frontend)

---

## Repository Layout

```
PartnerOpsAI/
├── backend/        # Business logic + API routes
├── frontend/       # Next.js dashboard (not created yet)
├── docs/           # Architecture decisions + plan
├── CLAUDE.md       # Engineering manifesto
├── README.md       # This file
├── DECISIONS.md    # Decision log
├── ARCHITECTURE.md # High-level design
├── ROADMAP.md      # Phase breakdown
└── .gitignore
```

---

## Development Workflow

1. **Create feature branch** from `main`
2. **Implement** (one feature per commit)
3. **Self-review** (architecture + typing)
4. **Paste output** to human reviewer
5. **Review** (9-point rubric)
6. **Merge** to `main`
7. **Deploy** (Vercel)

---

## Getting Started (Local Demo)

```bash
# Setup database
createdb partneropsa_test
psql partneropsa_test < backend/infrastructure/migrations/001_init_schema.sql

# Install dependencies
pip install -r requirements.txt

# Copy environment
cp .env.example .env.local

# Run demo server
python -m uvicorn backend.main:app --reload --port 8000

# In another terminal, seed demo data
python -m backend.seed

# Visit
open http://localhost:8000
```

Try the API:
```bash
# Qualify a prospect
curl -X POST http://localhost:8000/api/qualify \
  -H "Content-Type: application/json" \
  -d '{"company_name": "Acme Corp", "company_size_employees": 5000, "industry": "Technology", "location": "San Francisco", "ai_maturity": "advanced", "security_maturity": "advanced", "icp_score": 85, "design_partner_potential": 90, "has_product_team": true}'

# View Swagger docs
open http://localhost:8000/docs
```

## Documentation

| Document | Purpose |
|---|---|
| [PORTFOLIO.md](PORTFOLIO.md) | Internship demo release (this is what to share) |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Quick start + architecture overview |
| CLAUDE.md | Engineering manifesto + coding standards |
| DECISIONS.md | Architectural decision log |
| ARCHITECTURE.md | System design + data flow |
| ROADMAP.md | Phase breakdown + timeline

---

## Current Status

**Phase 3.6.0:** ✅ Integration test closure (54/55 tests passing, 71.51% coverage)
**Phase 3.6.1:** ✅ Demo release candidate (FastAPI server + Swagger docs)
**Phase 3.6.2:** ✅ Internship demo deployment (API routes + seed data + portfolio docs)

**Next:**
**Phase 3.7:** Design Partner Portal frontend (Next.js + real-time subscriptions)

---

## Key Files

| File | Purpose |
|---|---|
| CLAUDE.md | Engineering manifesto + coding standards |
| DECISIONS.md | Architectural decision log |
| ARCHITECTURE.md | System design + data flow |
| ROADMAP.md | Phase breakdown + timeline |

---

## Secret Management

- `.env.local` (gitignored, local development)
- Vercel env vars (production)
- Never commit keys, URLs, or project IDs

See `.env.example` for required variables.

---

## Questions?

See CLAUDE.md for architecture, coding standards, and review process.
