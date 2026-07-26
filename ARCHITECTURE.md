# System Architecture

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Next.js Frontend                        │
│          (React + Tailwind + shadcn/ui + Framer)          │
│                 - Dark-first dashboard                      │
│                 - Cmd+K command palette                     │
│                 - Real-time subscriptions                   │
└──────────────────────┬──────────────────────────────────────┘
                       │ (HTTPS)
┌──────────────────────▼──────────────────────────────────────┐
│              Next.js API Routes + Server Actions            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  /api/ai          (Provider-agnostic LLM routing)   │   │
│  │  /api/score       (Deterministic business logic)    │   │
│  │  /api/duplicates  (Similarity detection)            │   │
│  │  /api/activity    (Audit logging)                   │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│           Supabase (Postgres + Auth + Realtime)            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Tables:                                              │   │
│  │  - prospects (deals + context)                      │   │
│  │  - governance_items (compliance workflows)          │   │
│  │  - design_feedback (customer feedback)              │   │
│  │  - activity_log (audit trail)                       │   │
│  │  - scores (priority/impact calculations)            │   │
│  │  - users (auth + profiles)                          │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ RLS Policies:                                       │   │
│  │  - User can read own + shared items only            │   │
│  │  - User can write only own items                    │   │
│  │  - Activity log append-only                         │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│        External LLM Services (via /api/ai)                  │
│  - Ollama (local, default)                                 │
│  - OpenAI (via API key)                                    │
│  - Anthropic (via API key)                                 │
└──────────────────────────────────────────────────────────────┘
```

---

## Module Boundaries

### Frontend (`frontend/src/`)

**Responsibility:** Render UI, handle user input, subscribe to real-time updates.

**Structure:**
```
app/(dashboard)/
├── prospects/           # Phase 1: Enterprise prospect intelligence
├── governance/          # Phase 2: AI governance pipeline
└── design-partners/     # Phase 3: Design partner portal

components/
├── ui/                  # shadcn/ui primitives
├── features/            # Feature-specific components
├── common/              # Shared components
└── layout/              # Navigation, command palette

lib/
├── supabase/            # Supabase client setup
├── hooks/               # React hooks (useProspects, useScore, etc.)
├── utils/               # Helpers
└── theme.ts             # CSS variable management
```

**Key concerns:**
- Fetch data via server actions or useQuery
- Subscribe to realtime changes
- Respect theme preferences
- Handle loading/empty/error states

---

### Business Logic (`backend/lib/`)

**Responsibility:** All scoring, rules, LLM routing, audit logging.

**Modules:**
```
scoring.ts
├── calculatePriority()     # Deterministic algorithm
├── calculateImpact()
├── calculateConfidence()
└── aggregateScores()

ai.ts
├── route()                 # Provider-agnostic LLM handler
├── categorizeFeatures()    # LLM: Tag feedback
├── findDuplicates()        # LLM: Similarity + explanation
├── suggestRelease()        # LLM: Timing reasoning
└── summarizeDecision()     # LLM: Executive summary

activity.ts
├── logAction()             # Write to activity_log table
└── getAuditTrail()         # Read activity history
```

**Key principles:**
- Pure functions (same input → same output)
- No side effects except logging
- Explicit confidence + reasoning
- Every decision explainable

---

### Data Layer (Supabase)

**Responsibility:** Store state, enforce RLS, broadcast changes.

**Core tables:**

```sql
-- Users
users (id, email, created_at, theme, accent_color)

-- Phase 1: Enterprise Prospect Intelligence
prospects (
  id, owner_id, company_name, deal_size_usd,
  risk_factors, funding_sources, legal_status,
  created_at, updated_at, owner_id
)

-- Phase 2: AI Governance Pipeline
governance_items (
  id, prospect_id, category, status, priority_score,
  impact_score, confidence, reasoning, owner_id,
  created_at, updated_at
)

-- Phase 3: Design Partner Portal
design_feedback (
  id, prospect_id, category, status, priority_score,
  impact_score, confidence, similar_requests,
  suggested_release, product_decision, owner_id,
  created_at, updated_at
)

-- Audit trail
activity_log (
  id, user_id, action, table_name, record_id,
  old_value, new_value, created_at
) [append-only]

-- Scores (denormalized for fast reads)
scores (
  id, table_name, record_id, priority, impact,
  confidence, algorithm_version, created_at
)
```

**RLS rules:**
```
Default: Users can read/write only own records + shared records
Activity log: Append-only (no updates/deletes)
Scores: Read-only to users (computed server-side)
```

---

## Data Flow

### Phase 1: Prospect Intelligence
```
User enters prospect data
        ↓
Server validates input
        ↓
Calculates risk scores (deterministic)
        ↓
Stores in prospects table
        ↓
Activity log entry
        ↓
Realtime subscription pushes to UI
```

### Phase 2: Governance Pipeline
```
Governance item flagged
        ↓
LLM categorizes (via /api/ai)
        ↓
Deterministic scoring (code)
        ↓
Suggest recommended action
        ↓
Store governance_items + activity
        ↓
Realtime update to dashboard
```

### Phase 3: Design Partner Portal
```
Customer feedback submitted
        ↓
LLM categorizes (keywords + intent)
        ↓
Deterministic: impact score, priority
        ↓
LLM finds similar requests (explanation)
        ↓
Suggest release (with reasoning)
        ↓
Product decision summary
        ↓
Store + activity log + realtime update
```

---

## Integration Points

### Frontend ↔ Backend
- Server Actions: Mutations (create, update, delete)
- useQuery: Fetching with caching
- Supabase subscriptions: Real-time push

### Backend ↔ Database
- Supabase client with RLS
- No direct SQL (use Supabase APIs)

### Backend ↔ LLM
- `/api/ai` abstracts provider
- Returns: `{ output, reasoning, confidence }`
- Fallback if no API key

### Database ↔ Realtime
- Row-level subscriptions
- Activity log as system of record

---

## Error Handling

**Client:**
- Show error boundary if fetch fails
- Retry with exponential backoff
- Display meaningful error message

**Server:**
- Log error + context to activity log
- Return structured error response
- Never leak internal details to client

**LLM:**
- If unavailable, degrade gracefully (no categorization)
- Use fallback category
- Log the failure

---

## Security

**Authentication:**
- Supabase Auth (email + password for now)
- JWT in HTTP-only cookie (Supabase sets this)

**Authorization:**
- RLS policies enforce user isolation
- Server-side checks before mutation
- No client-side-only auth

**Secrets:**
- `.env.local` for development
- Vercel env vars for production
- Never commit keys

---

## Performance

**Database:**
- Indexes on frequently queried columns (owner_id, prospect_id, status)
- Denormalized scores table for fast ranking
- Pagination for large result sets (100 items per page)

**Frontend:**
- React Query caching
- Code splitting by route
- CSS-in-JS (Tailwind) for zero runtime overhead

**API:**
- Lightweight JSON payloads (no nested relations unless needed)
- Gzip compression
- Cache headers for immutable responses

---

## Observability

**Logging:**
- activity_log table: all meaningful state changes
- Server logs: errors, LLM requests
- Client logs: React errors, perf metrics

**Monitoring (Future):**
- API response times
- LLM latency + cost
- Error rates by endpoint
- User adoption metrics

---

## Deployment

**Frontend:**
- Vercel (automatic deployments from git)
- Environment variables via Vercel dashboard

**Backend:**
- Next.js API routes on Vercel
- Serverless functions (cold start acceptable for this use case)

**Database:**
- Supabase hosted Postgres
- Automated backups
- RLS enforces security at database level

---

## Scalability Considerations

**Short-term (Phase 1-3):**
- Single-user (founder + team)
- No horizontal scaling needed

**Medium-term (Post-Series A):**
- Multi-workspace support (defer to Phase 4)
- May need connection pooling (Supabase PgBouncer)

**Long-term (Enterprise):**
- SSO / SAML integration
- Audit log archival
- Custom data retention policies
