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

## Architecture Overview

**Three layers:**

```
UI Layer (Next.js + React)
    ↓
Business Logic (TypeScript + Supabase)
    ↓
Data Layer (Postgres + RLS)
    ↓
AI (Ollama/OpenAI via /api/ai)
```

**Key principles:**
- Deterministic scoring (code, not AI)
- AI for categorization + explanation only
- Real-time Supabase subscriptions
- Provider-agnostic LLM layer
- RLS for multi-tenant isolation

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

## Getting Started

```bash
cd ~/Developer/PartnerOpsAI
git status
git log
```

See `CLAUDE.md` for:
- Tech stack
- Coding standards
- Review process
- Definition of Done

---

## Current Status

**Phase 0:** ✅ Repository bootstrap complete
**Phase 1:** 🔒 Locked (Enterprise Prospect Intelligence)
**Phase 2:** 🔒 Locked (AI Governance Pipeline)
**Phase 3:** 🔒 Locked (Design Partner Portal)

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
