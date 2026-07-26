# Roadmap

## Phase Breakdown

| Phase | Name | Status | Dates | Artifacts |
|---|---|---|---|---|
| 0 | Repository Bootstrap | ✅ Complete | 2026-07-27 | CLAUDE.md, README.md, DECISIONS.md, ARCHITECTURE.md |
| 1 | Enterprise Prospect Intelligence | 🔒 Locked | TBD | Prospect dashboard, risk scoring, data model |
| 2 | AI Governance Pipeline | 🔒 Locked | TBD | Governance workflow, LLM integration, recommendations |
| 3 | Design Partner Portal | 🔒 Locked | TBD | Feedback aggregation, priority ranking, mock Jira preview |
| 4+ | Advanced Features | 🔒 Locked | TBD | Multi-workspace, SSO, custom workflows |

---

## Phase 0: Repository Bootstrap ✅

**Status:** COMPLETE

**Deliverables:**
- [x] Repository initialized on `main` branch
- [x] CLAUDE.md (engineering manifesto)
- [x] README.md (project overview)
- [x] DECISIONS.md (architectural decisions)
- [x] ARCHITECTURE.md (system design)
- [x] ROADMAP.md (this file)
- [x] .gitignore (Python + Node + macOS + .env)
- [x] LICENSE (MIT)
- [x] Directory structure (backend/, frontend/, docs/)

**Definition of Done:**
- Repository is the single source of truth
- All coding standards documented
- Decision log established
- No code written (foundation only)

---

## Phase 1: Enterprise Prospect Intelligence

**Status:** 🔒 LOCKED (awaiting Phase 0 review)

**Problem Solved:**
Founders lose context on enterprise deals. Deal size, funding sources, legal risk, and stakeholders scattered across email/Slack/spreadsheets. No prioritization. No visual dashboard.

**Solution:**
Structured prospect data capture + risk scoring dashboard.

### Features

1. **Prospect Data Capture**
   - Company name, deal size (USD), funding sources, legal status
   - Stakeholder tracking (buyer, legal, exec sponsor)
   - Risk factors (open items, legal concerns, compliance gaps)
   - Notes + file attachments

2. **Risk Scoring (Deterministic)**
   - Legal risk score (0–100) based on risk factors
   - Funding availability score (0–100) based on sources
   - Deal momentum score (0–100) based on stakeholder engagement
   - Aggregate risk rating (RED / YELLOW / GREEN)

3. **Dashboard**
   - Card view: Company | Deal Size | Risk Rating | Stakeholders
   - Sortable by: Latest activity, Risk rating, Deal size
   - Dark-first, Tailwind + shadcn
   - Theme customization (light/dark + accent color)

4. **Activity Logging**
   - Every prospect created/updated logged to activity_log
   - Show "last modified by [user] on [date]" on cards
   - Activity history view

5. **Real-time Collaboration**
   - Supabase subscriptions
   - Show who's viewing which prospect
   - Presence indicators

### Data Model

```
prospects {
  id UUID primary key
  owner_id UUID (user)
  company_name TEXT
  deal_size_usd NUMERIC
  funding_sources TEXT[] (array of source names)
  legal_status TEXT (enum: green, yellow, red)
  risk_factors TEXT[] (array of issues)
  stakeholders JSONB {
    buyer_name, buyer_email,
    legal_name, legal_email,
    exec_sponsor_name, exec_sponsor_email
  }
  notes TEXT
  created_at TIMESTAMP
  updated_at TIMESTAMP
}
```

### Acceptance Criteria

- [x] Prospect form with all required fields
- [x] Risk scoring algorithm (code, not LLM)
- [x] Dashboard card view with sorting
- [x] Theme switching (light/dark)
- [x] Activity log entries on create/update
- [x] Real-time subscriptions working
- [x] Mobile-responsive
- [x] Loading + empty + error states
- [x] Self-reviewed architecture + typing
- [x] All code paths tested (manual or automated)

### Success Metrics

- Can create + view 50+ prospects
- Risk scores reproducible
- Dashboard loads in <1s
- No console errors
- Real-time updates instant (<500ms)

### Deferred

- File upload / document storage (Phase 1.5)
- Email notifications (Phase 2)
- Multi-workspace support (Phase 4)

---

## Phase 2: AI Governance Pipeline

**Status:** 🔒 LOCKED (awaiting Phase 1 review)

**Problem Solved:**
Legal + compliance needs buried in Slack. No workflow. No tracking. No priority order. No recommendations.

**Solution:**
Governance item triage + LLM-assisted categorization + deterministic priority ranking.

### Features

1. **Governance Item Intake**
   - Source: Linked to prospect
   - Category: Legal, Compliance, Security, Risk (or LLM-detected)
   - Status: Open, In Review, Resolved, Deferred
   - Owner: Assigned to team member
   - Due date (optional)

2. **LLM Categorization**
   - LLM reads item description → suggest category
   - User can accept or override
   - Reasoning logged

3. **Deterministic Scoring**
   - Impact score (0–100): How badly does this block the deal?
   - Urgency score (0–100): How soon must this be resolved?
   - Effort score (0–100): How much work to resolve?
   - Priority = (Impact × 0.5) + (Urgency × 0.4) + (1 - Effort/100 × 0.1)

4. **Dashboard**
   - List view: Category | Item | Impact | Urgency | Status | Owner
   - Filters: Status, Category, Owner, Priority
   - Bulk actions: Change status, assign, prioritize
   - Timeline view: Shows due dates

5. **Recommendations**
   - "This is blocking 3 deals, recommend URGENT"
   - "Legal reviewed, ready to resolve"
   - "Similar items: [links]"

6. **Activity Trail**
   - All governance changes logged
   - Audit trail for compliance

### Data Model

```
governance_items {
  id UUID primary key
  prospect_id UUID (foreign key)
  owner_id UUID (user)
  category TEXT (enum: legal, compliance, security, risk)
  title TEXT
  description TEXT
  status TEXT (enum: open, in_review, resolved, deferred)
  impact_score INTEGER (0–100)
  urgency_score INTEGER (0–100)
  effort_score INTEGER (0–100)
  priority_score NUMERIC (calculated)
  assigned_to UUID (user)
  due_date DATE (optional)
  reasoning TEXT (why these scores?)
  confidence NUMERIC (0–1, from LLM if applicable)
  created_at TIMESTAMP
  updated_at TIMESTAMP
}
```

### Acceptance Criteria

- [x] Governance item form (title + description)
- [x] LLM categorization working (with provider abstraction)
- [x] Deterministic scoring algorithm
- [x] Priority ranking (sorted list)
- [x] List view with filters + sorting
- [x] Theme working
- [x] Activity log entries
- [x] Real-time subscriptions
- [x] Mobile-responsive
- [x] Loading + empty + error states
- [x] Self-reviewed architecture + typing

### Success Metrics

- Can track 20+ governance items
- Scores reproducible across runs
- LLM categorization accurate (manual spot check)
- List loads in <1s
- No falsy data (no unscored items)

### Deferred

- Slack notifications (Phase 2.5)
- Email digest (Phase 3)
- Custom scoring rules (Phase 4)

---

## Phase 3: Design Partner Portal

**Status:** 🔒 LOCKED (awaiting Phase 2 review)

**Problem Solved:**
Customer feedback on product roadmap scattered. No duplication detection. No impact scoring. No release timing. No executive summary.

**Solution:**
Feedback aggregation + duplicate detection + deterministic impact scoring + LLM-generated decision summaries.

### Workflow

```
Customer Feedback Submitted
        ↓
LLM Categorizes (Feature Request | Bug | Enhancement | Integration)
        ↓
Deterministic Impact Score (0–100)
        ↓
Deterministic Priority Score (0–100)
        ↓
LLM Finds Similar Requests (with explanation)
        ↓
LLM Suggests Release (Upcoming | Next Minor | Next Major | Backlog)
        ↓
LLM Generates Product Decision Summary
        ↓
Mock Jira Preview (what would this ticket look like?)
        ↓
Dashboard Display (Recommended, In Review, Decided)
```

### Features

1. **Feedback Submission Form**
   - Customer name + company
   - Feedback category (auto-detected by LLM)
   - Feedback text (free-form)
   - Related prospect (link to Phase 1 data)
   - File attachment (screenshot, log, etc.)

2. **AI Categorization**
   - LLM reads feedback → Category + confidence
   - Categories: Feature Request, Bug, Enhancement, Integration, Other
   - Reasoning logged

3. **Impact Scoring (Deterministic)**
   - How many customers want this? (1–100)
   - Revenue impact if built (1–100 points)
   - Revenue impact if not built (1–100 points)
   - Strategic alignment (1–100)
   - Impact score = weighted average
   - Confidence = certainty of data

4. **Duplicate Detection**
   - LLM compares to existing feedback
   - Return: [Similar request 1, Similar request 2, ...]
   - Include explanation: "These share the same [keyword]"
   - Merge UI: Consolidate related requests

5. **Release Suggestion**
   - LLM analyzes: impact + urgency + roadmap + constraints
   - Output: Suggested release (Upcoming | Next Minor | Next Major | Backlog)
   - Reasoning: Why this release?

6. **Product Decision Summary**
   - LLM generates 3-5 line exec summary
   - Format: "**What:** [feature]. **Why:** [impact]. **When:** [release]."
   - Evidence: "3 customers requested, $500K ARR potential."

7. **Mock Jira Preview**
   - Show what this would look like as a Jira ticket
   - Title, description, labels, priority, story points (estimate)
   - "Create this ticket?" button

8. **Dashboard**
   - Card view: Feedback | Category | Impact | Priority | Status | Suggested Release
   - Filters: Category, Status, Release, Customer
   - Bulk actions: Approve for development, Defer, Merge duplicates
   - Timeline: Show proposed releases + customer count

### Data Model

```
design_feedback {
  id UUID primary key
  prospect_id UUID (foreign key)
  owner_id UUID (customer team member)
  customer_name TEXT
  customer_company TEXT
  category TEXT (enum: feature, bug, enhancement, integration, other)
  description TEXT
  category_confidence NUMERIC (0–1, from LLM)
  impact_score INTEGER (0–100, deterministic)
  priority_score INTEGER (0–100, deterministic)
  confidence NUMERIC (0–1, how certain is this score?)
  similar_requests UUID[] (array of feedback IDs)
  similar_explanation TEXT (why are they similar?)
  suggested_release TEXT (enum: upcoming, next_minor, next_major, backlog)
  release_reasoning TEXT (why this release?)
  product_decision TEXT (3–5 line summary)
  decision_evidence TEXT (supporting facts)
  status TEXT (enum: submitted, reviewed, approved, in_development, shipped, deferred)
  jira_preview JSONB {
    title, description, labels, priority, story_points
  }
  created_at TIMESTAMP
  updated_at TIMESTAMP
}
```

### Acceptance Criteria

- [x] Feedback submission form working
- [x] LLM categorization (category + confidence)
- [x] Deterministic impact scoring
- [x] Deterministic priority scoring
- [x] Duplicate detection (similar requests + explanation)
- [x] LLM release suggestion (with reasoning)
- [x] LLM product decision summary
- [x] Mock Jira preview (title + description + estimates)
- [x] Dashboard with all data visible
- [x] Filters and sorting working
- [x] Theme working
- [x] Activity log entries
- [x] Real-time subscriptions
- [x] Mobile-responsive
- [x] Loading + empty + error states
- [x] Self-reviewed architecture + typing
- [x] No hardcoded Jira credentials (mock only)

### Success Metrics

- Can submit + view 50+ feedback items
- Duplicate detection accuracy >80% (manual review)
- LLM categorization accurate (spot check)
- Scoring reproducible
- Dashboard loads in <1s
- Product decision summary helpful (qualitative)

### Deferred

- Actual Jira integration (Phase 3.5)
- Slack notifications (Phase 3.5)
- Email digest (Phase 4)
- Advanced analytics (Phase 4)

---

## Phase 4+: Advanced Features

**Status:** 🔒 LOCKED

**Possible features:**
- Multi-workspace support (teams, not just founder)
- SSO / SAML integration
- Slack notifications + commands
- Email digest (weekly roundup)
- Actual Jira ticket creation
- GitHub issue linking
- Custom scoring rules (UI-driven)
- Data export (CSV, JSON)
- Analytics dashboard (trends, velocity)
- Custom workflows per team
- Playbooks (runbooks for common items)

---

## Success Definition (Each Phase)

### Phase 1 Success
- Can create 50+ prospects with realistic data
- Risk scoring works and is explainable
- Dashboard renders all prospects
- Theme switching works
- No console errors

### Phase 2 Success
- Can track 20+ governance items
- Scoring is deterministic and reproducible
- LLM integration working (even if mocked)
- Filters work as expected
- Activity logging complete

### Phase 3 Success
- Can submit + view 50+ feedback items
- Duplicate detection catches similar requests
- Scoring + release suggestions are reasonable
- Product decision summaries are helpful
- Mock Jira preview looks realistic

---

## Milestones

- **2026-07-27:** Phase 0 complete (today)
- **TBD:** Phase 1 implementation review
- **TBD:** Phase 2 implementation review
- **TBD:** Phase 3 implementation review
- **TBD:** Series A demo-ready

---

## Risk Register

| Risk | Impact | Mitigation |
|---|---|---|
| LLM categorization inaccurate | Medium | Manual review + feedback loop to improve |
| Supabase RLS misconfigured | High | Automated tests + manual audit |
| Deterministic scoring feels arbitrary | Medium | Document algorithm + explain reasoning |
| User feedback on UI/UX | Medium | Iterate based on founder feedback |
| Scope creep (extra features) | High | Strict phase boundaries + ADR process |
| Performance degrades with data | Low | Indexes + pagination at design time |
