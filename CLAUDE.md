# PartnerOpsAI: Engineering Manifesto

## Vision

PartnerOpsAI is an **enterprise AI product decision support system** for a Series A startup building AI governance.

Not a ticketing app. Not a feedback collector. A **decision engine** that turns customer feedback into prioritized product work.

**Three phases:**
1. **Enterprise Prospect Intelligence** — Capture deal context, funding sources, risk factors
2. **AI Governance Pipeline** — Process, score, and recommend legal/compliance actions
3. **Design Partner Portal** — Aggregate customer feedback → Priority recommendations → Mock release planning

---

## Problem We Solve

Founders + PMs + Legal drown in customer feedback.
- No signal/noise separation
- No duplication detection
- No business impact scoring
- No release timeline reasoning

PartnerOpsAI automates decision support.

---

## Architecture Principles

**Deterministic business logic.**
- AI categorizes, explains, summarizes only.
- All scoring, prioritization, aggregation computed in code.
- Every AI output includes reasoning + confidence + evidence.

**Provider-agnostic AI.**
- Default: Ollama (local llama3.1/qwen2.5) via `/api/ai`
- Swappable: OpenAI, Anthropic by env var
- No vendor lock-in. No GPTfy branding in code.

**Single source of truth.**
- Supabase Postgres (RLS-protected)
- Real-time subscriptions for live updates
- Audit logs for everything

**Premium product feel.**
- Dark-first dashboard (Linear/Vercel aesthetic)
- Smooth Framer Motion transitions
- Cmd+K command palette
- CSS variable theming (light/dark + custom accent)

---

## Coding Standards

**TypeScript everywhere.**
- Strict mode: `"strict": true`
- No `any` types
- Discriminated unions for tagged data

**Component structure:**
- `src/app/(dashboard)/<section>/` — feature routes
- `src/components/ui/` — shadcn primitives
- `src/components/<feature>/` — feature-specific components
- `src/lib/` — utilities (`ai.ts`, `scoring.ts`, `types.ts`, etc.)

**Server-side data:**
- Supabase server client + RLS for all database operations
- Never expose service-role key to client
- Prefer server actions over API routes where possible

**AI integration:**
- All LLM calls through `/api/ai` with provider abstraction
- Structured outputs with validation
- Confidence scores on all predictions

**Definition of Done:**
- Reads/writes real Supabase data
- Respects user theme (light/dark/accent)
- Loading + empty + error states handled
- Mobile-responsive (Tailwind breakpoints)
- Activity log entry for meaningful actions
- Realtime updates via Supabase subscriptions
- Self-reviewed for architecture/typing/product fit

---

## Tech Stack (Fixed)

| Layer | Choice |
|---|---|
| Framework | Next.js (App Router, TypeScript) |
| Database | Supabase Postgres + RLS + Auth + Storage + Realtime |
| Styling | Tailwind CSS + shadcn/ui (Radix primitives) |
| Icons | lucide-react |
| Animation | framer-motion |
| Tables | @tanstack/react-table |
| Forms | react-hook-form + zod |
| State | @tanstack/react-query (client) + server actions |
| Command palette | cmdk |
| Charts | recharts |
| Dates | date-fns |
| AI | Ollama (local) via `/api/ai` |
| Hosting | Vercel |

**Do not deviate without written approval.**

---

## Repository Structure

```
PartnerOpsAI/
├── backend/
│   ├── api/
│   │   ├── ai.ts (LLM routing layer)
│   │   ├── scoring.ts (deterministic algorithms)
│   │   └── ...
│   └── lib/ (business logic)
│
├── frontend/
│   ├── src/
│   │   ├── app/(dashboard)/
│   │   │   ├── prospects/
│   │   │   ├── governance/
│   │   │   └── design-partners/
│   │   ├── components/
│   │   ├── lib/
│   │   └── types/
│   └── package.json
│
├── docs/
│   ├── architecture.md
│   ├── decisions.md
│   └── plan.md
│
├── CLAUDE.md (this file)
├── README.md
├── DECISIONS.md
├── ARCHITECTURE.md
├── ROADMAP.md
└── .gitignore
```

---

## Review Process

**Every feature goes through:**
1. Self-review (architecture, typing, product fit)
2. Paste output here
3. Human review (9-point rubric)
4. PASS / FAIL
5. Git commit
6. Next feature

**Review rubric:**
- Executive Summary (≤5 lines)
- Verdict (PASS / FAIL / PASS WITH FIXES)
- Architecture Review
- Engineering Review (typing, imports, testing)
- Product Review (solves the problem?)
- Enterprise Review (would a founder use it?)
- Technical Debt (what's deferred?)
- Score (8 dimensions, /10 each)
- Unlock (next phase or blockers)

---

## Commands

```bash
# Install
npm install

# Dev server
npm run dev

# Type check
npm run type-check

# Build
npm run build

# Test (when we have tests)
npm run test

# Deploy
npm run deploy
```

---

## Secrets & Config

**Never commit secrets.**
- Use `.env.local` (gitignored)
- Supabase keys in Vercel/local env only
- Document all required env vars in `.env.example`

**No hardcoded:**
- API keys
- Project IDs
- URLs
- Account-specific values

---

## Definition of Done (Phase Level)

Before considering a phase complete:
- All user-facing features work end-to-end
- Real Supabase data (no mocks)
- Realtime subscriptions active
- Activity logging for all state changes
- Dark + light theme working
- Mobile-responsive
- Empty states + error states handled
- Self-reviewed architecture + typing
- Commit message explains why, not what
- No dead code or commented-out lines
- No references to GPTfy or other projects

---

## Governance

**Owner:** Sathiyan Arulmurugan Karunambigai

Every record has an owner. Decisions are logged. No shortcuts.

**Never reference:** "Diddy" (governance rule)

---

## Next Steps

Phase 0 (Bootstrap): Create repo structure + CLAUDE.md ✅
Phase 1: Enterprise Prospect Intelligence
Phase 2: AI Governance Pipeline  
Phase 3: Design Partner Portal
