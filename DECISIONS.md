# Decision Log

Track all significant architectural and product decisions here.

---

## ADR Template

```
# ADR-XXX: [Decision Title]

**Date:** YYYY-MM-DD
**Owner:** [Name]
**Status:** ACCEPTED / DEFERRED / REJECTED

## Problem

[What problem does this solve?]

## Options Considered

1. [Option A] — Pros: [] Cons: []
2. [Option B] — Pros: [] Cons: []
3. [Option C] — Pros: [] Cons: []

## Decision

We choose [Option X] because [reasoning].

## Consequences

- [Positive consequence 1]
- [Positive consequence 2]
- [Tradeoff 1]
- [Tradeoff 2]

## Evidence

- [Supporting data or precedent]
```

---

## Accepted Decisions

### ADR-001: Next.js + TypeScript + Supabase

**Date:** 2026-07-27
**Owner:** Sathiyan Arulmurugan Karunambigai
**Status:** ACCEPTED

**Problem:**
Need a framework that supports real-time collaboration, RLS-based security, and a polished UI without reinventing auth/database.

**Decision:**
Use Next.js (App Router) + TypeScript + Supabase (Postgres + RLS + Realtime + Auth).

**Rationale:**
- Next.js: SSR + SSG + API routes + built-in optimizations
- TypeScript: Type safety without runtime overhead
- Supabase: Postgres + Row-Level Security + Realtime subscriptions + Auth
- Tailwind + shadcn: Rapid, consistent UI
- Vercel: Seamless Next.js hosting

**Consequences:**
- Fast iteration on UI
- Strong type safety
- Real-time features out of the box
- Vendor lock-in to Vercel (acceptable for now)
- Learning curve for RLS + Postgres

---

### ADR-002: Deterministic Scoring + LLM for Explanation Only

**Date:** 2026-07-27
**Owner:** Sathiyan Arulmurugan Karunambigai
**Status:** ACCEPTED

**Problem:**
AI decisions are hard to audit and explain. Non-deterministic scoring breaks consistency. Business rules must be law-like.

**Decision:**
All priority/impact/confidence scores computed deterministically in code.
LLM used only for: categorization, similarity explanation, release reasoning, decision summary.

**Rationale:**
- Reproducibility: Same input → same score
- Auditability: Score logic is code, not black box
- Speed: No LLM latency for scoring
- Confidence: Business can understand and trust the algorithm

**Consequences:**
- Longer backend code (explicit logic vs. learned patterns)
- Manual tuning if business rules change
- No end-to-end "just use AI for everything"
- Stronger audit trail

---

### ADR-003: Provider-Agnostic AI Layer (/api/ai)

**Date:** 2026-07-27
**Owner:** Sathiyan Arulmurugan Karunambigai
**Status:** ACCEPTED

**Problem:**
LLM landscape changes fast. Don't want to rewrite when switching from Ollama → OpenAI or vice versa.

**Decision:**
Abstract all LLM calls behind `/api/ai` route. Provider determined by env var (OPENAI_API_KEY, ANTHROPIC_API_KEY, or default Ollama).

**Rationale:**
- Swap providers without code changes
- Easy to A/B test models
- No "GPTfy" branding in UI (provider is implementation detail)
- Future-proof against model changes

**Consequences:**
- One extra HTTP layer (negligible latency)
- More abstraction to maintain
- Env var management complexity

---

### ADR-004: Three-Phase Rollout

**Date:** 2026-07-27
**Owner:** Sathiyan Arulmurugan Karunambigai
**Status:** ACCEPTED

**Phases:**
1. **Phase 1: Enterprise Prospect Intelligence** — Deal context capture + risk scoring
2. **Phase 2: AI Governance Pipeline** — Compliance workflow + recommendations
3. **Phase 3: Design Partner Portal** — Feedback aggregation + priority ranking

**Rationale:**
- Phase 1 establishes data model + auth
- Phase 2 tests LLM integration + business logic
- Phase 3 integrates feedback → decision engine

**Consequences:**
- Incremental value delivery
- Reduce risk per phase
- Founder can use Phase 1 standalone

---

### ADR-005: Real-Time via Supabase Subscriptions, Not WebSockets

**Date:** 2026-07-27
**Owner:** Sathiyan Arulmurugan Karunambigai
**Status:** ACCEPTED

**Problem:**
Need real-time updates without managing WebSocket infrastructure.

**Decision:**
Use Supabase Realtime (built-in subscriptions to table changes) + React Query cache invalidation.

**Rationale:**
- No extra infrastructure
- Automatic reconnection
- Built into Supabase client
- RLS rules apply to subscriptions too

**Consequences:**
- Supabase vendor lock-in
- Limited to Postgres row-level updates (not custom events)
- Simpler ops than self-managed WebSockets

---

## Deferred Decisions

### Offline-First Sync
**Status:** DEFERRED (Phase 4+)
Rationale: Assume always-online for SaaS. Revisit if mobile client needed.

### Multi-Workspace Support
**Status:** DEFERRED (Phase 4+)
Rationale: Single-user internal tool initially. Extend after Phase 3.

### Audit Log Retention Policy
**Status:** DEFERRED (Phase 2)
Rationale: Implement logging first, retention policy once data volume is clear.

### Custom LLM Fine-Tuning
**Status:** DEFERRED (Phase 4+)
Rationale: Use off-the-shelf models. Fine-tune only if signal warrants it.

---

## Rejected Decisions

### GraphQL Instead of REST
**Reason:** Over-engineered for internal tool. REST APIs sufficient.

### Prisma ORM
**Reason:** Supabase client + server actions simpler than ORM layer.

### Docker for Local Dev
**Reason:** Not needed for Next.js + local Ollama. Skip until CI/CD.

---

## Decision Template (Copy for New Decisions)

```
### ADR-XXX: [Decision Title]

**Date:** YYYY-MM-DD
**Owner:** [Name]
**Status:** ACCEPTED / DEFERRED / REJECTED

**Problem:**
[Brief statement of problem]

**Decision:**
[What was decided]

**Rationale:**
- [Reason 1]
- [Reason 2]
- [Reason 3]

**Consequences:**
- [Positive consequence]
- [Tradeoff]
```
