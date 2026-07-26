-- Phase 3: Infrastructure Schema
-- PartnerOpsAI database initialization
-- Uses Supabase PostgreSQL with RLS

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Users table (standalone for testing, references auth.users in production)
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Opportunities (enterprise prospects)
CREATE TABLE IF NOT EXISTS public.opportunities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_by UUID NOT NULL REFERENCES public.users(id),
    updated_by UUID NOT NULL REFERENCES public.users(id),
    version INTEGER NOT NULL DEFAULT 0,

    company_name TEXT NOT NULL,
    company_size_employees INTEGER NOT NULL DEFAULT 0,
    industry TEXT,
    location TEXT,
    website TEXT,

    status TEXT NOT NULL DEFAULT 'prospect' CHECK (status IN ('prospect', 'qualified', 'converted', 'design_partner', 'lost')),
    icp_alignment TEXT NOT NULL DEFAULT 'weak' CHECK (icp_alignment IN ('perfect', 'strong', 'moderate', 'weak')),
    icp_score INTEGER NOT NULL DEFAULT 0 CHECK (icp_score >= 0 AND icp_score <= 100),

    ai_maturity TEXT NOT NULL DEFAULT 'none' CHECK (ai_maturity IN ('advanced', 'intermediate', 'beginner', 'none')),
    ai_maturity_evidence TEXT,
    ai_investment_usd INTEGER NOT NULL DEFAULT 0,

    security_maturity TEXT NOT NULL DEFAULT 'none' CHECK (security_maturity IN ('advanced', 'intermediate', 'beginner', 'none')),
    security_certifications TEXT[] DEFAULT ARRAY[]::TEXT[],
    compliance_needs TEXT[] DEFAULT ARRAY[]::TEXT[],

    design_partner_potential INTEGER NOT NULL DEFAULT 0 CHECK (design_partner_potential >= 0 AND design_partner_potential <= 100),
    has_product_team BOOLEAN NOT NULL DEFAULT FALSE,
    product_owner_email TEXT,
    technical_contact_email TEXT,
    executive_sponsor_email TEXT,

    qualification_evidence TEXT,
    strategic_alignment TEXT,
    notes TEXT,
    source TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_opportunities_status ON public.opportunities(status);
CREATE INDEX idx_opportunities_company_name ON public.opportunities(company_name);
CREATE INDEX idx_opportunities_created_by ON public.opportunities(created_by);

-- Design Partners (converted opportunities)
CREATE TABLE IF NOT EXISTS public.design_partners (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    opportunity_id UUID NOT NULL REFERENCES public.opportunities(id),
    created_by UUID NOT NULL REFERENCES public.users(id),
    updated_by UUID NOT NULL REFERENCES public.users(id),
    version INTEGER NOT NULL DEFAULT 0,

    converted_at TIMESTAMP WITH TIME ZONE NOT NULL,
    converted_by UUID NOT NULL REFERENCES public.users(id),

    company_name TEXT NOT NULL,
    product_owner_name TEXT,
    product_owner_email TEXT,
    technical_contact_name TEXT,
    technical_contact_email TEXT,

    onboarding_status TEXT NOT NULL DEFAULT 'onboarding' CHECK (onboarding_status IN ('onboarding', 'active', 'in_implementation', 'shipped', 'inactive')),
    onboarding_started_at TIMESTAMP WITH TIME ZONE,
    onboarding_completed_at TIMESTAMP WITH TIME ZONE,

    implementation_status TEXT NOT NULL DEFAULT 'onboarding' CHECK (implementation_status IN ('onboarding', 'active', 'in_implementation', 'shipped', 'inactive')),
    implementation_started_at TIMESTAMP WITH TIME ZONE,
    implementation_completed_at TIMESTAMP WITH TIME ZONE,

    health TEXT NOT NULL DEFAULT 'good' CHECK (health IN ('excellent', 'good', 'at_risk', 'critical')),
    health_notes TEXT,
    last_engagement_at TIMESTAMP WITH TIME ZONE,

    total_feedback_count INTEGER NOT NULL DEFAULT 0,
    feedback_count_this_quarter INTEGER NOT NULL DEFAULT 0,
    last_feedback_date TIMESTAMP WITH TIME ZONE,

    features_influenced TEXT[] DEFAULT ARRAY[]::TEXT[],
    roadmap_review_frequency TEXT DEFAULT 'monthly',
    product_review_dates TIMESTAMP WITH TIME ZONE[] DEFAULT ARRAY[]::TIMESTAMP WITH TIME ZONE[],

    partnership_notes TEXT,
    success_criteria TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_design_partners_opportunity_id ON public.design_partners(opportunity_id);
CREATE INDEX idx_design_partners_created_by ON public.design_partners(created_by);

-- Design Feedback (customer feedback on roadmap)
CREATE TABLE IF NOT EXISTS public.design_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    design_partner_id UUID NOT NULL REFERENCES public.design_partners(id),
    created_by UUID NOT NULL REFERENCES public.users(id),
    updated_by UUID NOT NULL REFERENCES public.users(id),
    version INTEGER NOT NULL DEFAULT 0,

    customer_name TEXT NOT NULL,
    customer_email TEXT,
    customer_company TEXT,

    category TEXT NOT NULL DEFAULT 'other' CHECK (category IN ('feature_request', 'bug', 'enhancement', 'integration', 'workflow', 'other')),
    category_confidence NUMERIC NOT NULL DEFAULT 0 CHECK (category_confidence >= 0 AND category_confidence <= 1),
    title TEXT NOT NULL,
    description TEXT NOT NULL,

    impact_score INTEGER NOT NULL DEFAULT 0 CHECK (impact_score >= 0 AND impact_score <= 100),
    priority_score INTEGER NOT NULL DEFAULT 0 CHECK (priority_score >= 0 AND priority_score <= 100),
    confidence NUMERIC NOT NULL DEFAULT 0 CHECK (confidence >= 0 AND confidence <= 1),

    similar_feedback_ids UUID[] DEFAULT ARRAY[]::UUID[],
    similarity_explanation TEXT,

    suggested_release TEXT NOT NULL DEFAULT 'backlog' CHECK (suggested_release IN ('upcoming', 'next_minor', 'next_major', 'backlog')),
    release_reasoning TEXT,

    product_decision_summary TEXT,
    decision_evidence TEXT,
    affected_personas TEXT[] DEFAULT ARRAY[]::TEXT[],

    status TEXT NOT NULL DEFAULT 'submitted' CHECK (status IN ('submitted', 'reviewed', 'approved', 'in_development', 'shipped', 'deferred')),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_design_feedback_design_partner_id ON public.design_feedback(design_partner_id);
CREATE INDEX idx_design_feedback_status ON public.design_feedback(status);
CREATE INDEX idx_design_feedback_category ON public.design_feedback(category);

-- Feedback Clusters (grouped similar feedback)
CREATE TABLE IF NOT EXISTS public.feedback_clusters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_by UUID NOT NULL REFERENCES public.users(id),
    updated_by UUID NOT NULL REFERENCES public.users(id),
    version INTEGER NOT NULL DEFAULT 0,

    primary_feedback_id UUID NOT NULL REFERENCES public.design_feedback(id),
    related_feedback_ids UUID[] NOT NULL DEFAULT ARRAY[]::UUID[],

    cluster_reason TEXT NOT NULL,
    theme TEXT,

    total_feedback_count INTEGER NOT NULL DEFAULT 0,
    average_impact_score NUMERIC NOT NULL DEFAULT 0,
    average_priority_score NUMERIC NOT NULL DEFAULT 0,
    unique_customers INTEGER NOT NULL DEFAULT 0,

    merged_at TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_feedback_clusters_primary_feedback_id ON public.feedback_clusters(primary_feedback_id);

-- Product Recommendations (AI-informed from feedback)
CREATE TABLE IF NOT EXISTS public.product_recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    feedback_cluster_id UUID NOT NULL REFERENCES public.feedback_clusters(id),
    created_by UUID NOT NULL REFERENCES public.users(id),
    updated_by UUID NOT NULL REFERENCES public.users(id),
    version INTEGER NOT NULL DEFAULT 0,

    title TEXT NOT NULL,
    description TEXT,
    category TEXT,

    requesting_customer_count INTEGER NOT NULL DEFAULT 0,
    total_feedback_items INTEGER NOT NULL DEFAULT 0,
    aggregate_impact_score INTEGER NOT NULL DEFAULT 0 CHECK (aggregate_impact_score >= 0 AND aggregate_impact_score <= 100),
    aggregate_priority_score INTEGER NOT NULL DEFAULT 0 CHECK (aggregate_priority_score >= 0 AND aggregate_priority_score <= 100),

    business_justification TEXT,
    market_opportunity TEXT,
    revenue_impact_potential TEXT,
    competitive_positioning TEXT,

    recommendation TEXT NOT NULL DEFAULT 'research' CHECK (recommendation IN ('build', 'defer', 'reject', 'research')),
    recommendation_reasoning TEXT,
    confidence NUMERIC NOT NULL DEFAULT 0 CHECK (confidence >= 0 AND confidence <= 1),

    suggested_release TEXT NOT NULL DEFAULT 'backlog' CHECK (suggested_release IN ('upcoming', 'next_minor', 'next_major', 'backlog')),
    release_reasoning TEXT,

    estimated_effort TEXT CHECK (estimated_effort IN ('small', 'medium', 'large', 'xlarge')),
    affected_personas TEXT[] DEFAULT ARRAY[]::TEXT[],
    dependencies TEXT[] DEFAULT ARRAY[]::TEXT[],
    risks TEXT[] DEFAULT ARRAY[]::TEXT[],

    decision_made BOOLEAN NOT NULL DEFAULT FALSE,
    decision_made_by UUID REFERENCES public.users(id),
    decision_made_at TIMESTAMP WITH TIME ZONE,
    decision_notes TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_product_recommendations_feedback_cluster_id ON public.product_recommendations(feedback_cluster_id);
CREATE INDEX idx_product_recommendations_decision_made ON public.product_recommendations(decision_made);

-- Policy Decisions (governance/compliance)
CREATE TABLE IF NOT EXISTS public.policy_decisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    opportunity_id UUID NOT NULL REFERENCES public.opportunities(id),
    created_by UUID NOT NULL REFERENCES public.users(id),
    updated_by UUID NOT NULL REFERENCES public.users(id),
    version INTEGER NOT NULL DEFAULT 0,

    title TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL DEFAULT 'governance',

    impact_score INTEGER NOT NULL DEFAULT 0 CHECK (impact_score >= 0 AND impact_score <= 100),
    urgency_score INTEGER NOT NULL DEFAULT 0 CHECK (urgency_score >= 0 AND urgency_score <= 100),
    effort_score INTEGER NOT NULL DEFAULT 0 CHECK (effort_score >= 0 AND effort_score <= 100),
    priority_score INTEGER NOT NULL DEFAULT 0 CHECK (priority_score >= 0 AND priority_score <= 100),
    confidence NUMERIC NOT NULL DEFAULT 0 CHECK (confidence >= 0 AND confidence <= 1),

    reasoning TEXT,
    recommendation TEXT,

    status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'in_review', 'resolved', 'deferred')),
    assigned_to_id UUID REFERENCES public.users(id),
    due_date TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_policy_decisions_opportunity_id ON public.policy_decisions(opportunity_id);
CREATE INDEX idx_policy_decisions_status ON public.policy_decisions(status);

-- Security Audit Records (append-only audit trail)
CREATE TABLE IF NOT EXISTS public.security_audit_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    version INTEGER NOT NULL DEFAULT 0,

    actor_id UUID NOT NULL REFERENCES public.users(id),
    actor_role TEXT NOT NULL,

    action TEXT NOT NULL CHECK (action IN ('created', 'updated', 'deleted', 'approved', 'rejected', 'escalated', 'policy_evaluated', 'policy_override')),
    resource_type TEXT NOT NULL,
    resource_id UUID NOT NULL,

    policy_name TEXT,
    policy_version INTEGER,
    policy_result TEXT CHECK (policy_result IN ('approved', 'rejected', 'review_required', 'override')),
    policy_evaluation_reasoning TEXT,

    request_id TEXT,
    request_hash TEXT,
    record_hash TEXT,
    previous_hash TEXT,

    ip_address INET,
    user_agent TEXT,
    context_data JSONB DEFAULT '{}'::JSONB,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_security_audit_records_actor_id ON public.security_audit_records(actor_id);
CREATE INDEX idx_security_audit_records_resource_id ON public.security_audit_records(resource_id);
CREATE INDEX idx_security_audit_records_created_at ON public.security_audit_records(created_at DESC);

-- Row-Level Security Policies
-- Disabled for local testing (requires Supabase auth schema)
-- Enable these when deploying to Supabase
-- ALTER TABLE public.opportunities ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.design_partners ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.design_feedback ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.feedback_clusters ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.product_recommendations ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.policy_decisions ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.security_audit_records ENABLE ROW LEVEL SECURITY;

-- RLS Policies (commented for local testing)
-- CREATE POLICY "opportunities_user_access" ON public.opportunities
--     FOR ALL USING (created_by = auth.uid() OR created_by = '00000000-0000-0000-0000-000000000000');
--
-- CREATE POLICY "design_partners_user_access" ON public.design_partners
--     FOR ALL USING (created_by = auth.uid() OR created_by = '00000000-0000-0000-0000-000000000000');
--
-- CREATE POLICY "design_feedback_user_access" ON public.design_feedback
--     FOR ALL USING (created_by = auth.uid() OR created_by = '00000000-0000-0000-0000-000000000000');
--
-- CREATE POLICY "policy_decisions_user_access" ON public.policy_decisions
--     FOR ALL USING (created_by = auth.uid() OR created_by = '00000000-0000-0000-0000-000000000000');
--
-- CREATE POLICY "audit_records_append_only" ON public.security_audit_records
--     FOR INSERT WITH CHECK (actor_id = auth.uid())
--     FOR SELECT USING (TRUE);
