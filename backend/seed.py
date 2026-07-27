"""Demo seed data for PartnerOpsAI internship demo."""

import os
from datetime import datetime
from uuid import uuid4

import psycopg2

DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://test_user:test_password@localhost:5432/partneropsa_test",
)

def seed_demo_data():
    """Populate database with realistic demo company."""
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()

    try:
        # 1. Create demo user
        user_id = "00000000-0000-0000-0000-000000000001"
        cursor.execute(
            "INSERT INTO users (id, email) VALUES (%s, %s) ON CONFLICT (id) DO NOTHING",
            (user_id, "demo@partneropsa.com"),
        )

        # 2. Create demo opportunity (Acme Corp)
        opp_id = str(uuid4())
        cursor.execute(
            """
            INSERT INTO opportunities (
                id, created_by, updated_by, version,
                company_name, industry, location, company_size_employees,
                ai_maturity, ai_maturity_evidence, ai_investment_usd,
                security_maturity, security_certifications, compliance_needs,
                icp_score, design_partner_potential, has_product_team,
                product_owner_email, technical_contact_email, executive_sponsor_email,
                qualification_evidence, strategic_alignment,
                created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s,
                %s, %s
            )
            """,
            (
                opp_id, user_id, user_id, 1,
                "Acme Corp", "Enterprise Software", "San Francisco", 5000,
                "advanced", "Acme uses ML in product recommendations and analytics", 500000,
                "advanced", ["SOC2", "ISO27001"], ["GDPR", "CCPA"],
                85, 90, True,
                "alice@acme.com", "bob@acme.com", "carol@acme.com",
                "Strong ICP alignment: 5000+ employees, tech-forward, heavy AI investment",
                "Enterprise customer, high-value partnership opportunity",
                datetime.utcnow(), datetime.utcnow(),
            ),
        )
        print(f"✅ Created opportunity: {opp_id}")

        # 3. Create design partner conversion
        partner_id = str(uuid4())
        cursor.execute(
            """
            INSERT INTO design_partners (
                id, opportunity_id, created_by, updated_by, version,
                status, engagement_model, contract_value_usd,
                trial_start_date, trial_end_date, trial_focus_areas,
                primary_contact_name, primary_contact_email, primary_contact_phone,
                secondary_contact_name, secondary_contact_email,
                product_team_size, existing_platform_users,
                created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s,
                %s, %s,
                %s, %s
            )
            """,
            (
                partner_id, opp_id, user_id, user_id, 1,
                "onboarding", "design_partner", 250000,
                "2026-07-27", "2026-10-27", '["Dashboard customization", "API feedback", "Performance optimization"]',
                "Alice Chen", "alice@acme.com", "+1-555-1234",
                "Bob Smith", "bob@acme.com",
                12, 150,
                datetime.utcnow(), datetime.utcnow(),
            ),
        )
        print(f"✅ Created design partner: {partner_id}")

        # 4. Create sample feedback
        feedback_id = str(uuid4())
        cursor.execute(
            """
            INSERT INTO design_feedback (
                id, design_partner_id, created_by, updated_by, version,
                customer_name, customer_email, customer_company,
                category, title, description,
                impact_score, priority_score, status,
                created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s
            )
            """,
            (
                feedback_id, partner_id, user_id, user_id, 1,
                "Alice Chen", "alice@acme.com", "Acme Corp",
                "feature_request", "Dashboard Customization",
                "Users want to customize dashboard layout and color scheme. Currently fixed to default design.",
                82, 85, "submitted",
                datetime.utcnow(), datetime.utcnow(),
            ),
        )
        print(f"✅ Created feedback: {feedback_id}")

        # 5. Create feedback cluster
        cluster_id = str(uuid4())
        cursor.execute(
            """
            INSERT INTO feedback_clusters (
                id, created_by, updated_by, version,
                primary_feedback_id, related_feedback_ids, cluster_reason,
                theme, total_feedback_count, average_impact_score,
                created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s
            )
            """,
            (
                cluster_id, user_id, user_id, 1,
                feedback_id, "{}", "Primary feedback only in demo",
                "Dashboard Customization", 1, 82.0,
                datetime.utcnow(), datetime.utcnow(),
            ),
        )
        print(f"✅ Created feedback cluster: {cluster_id}")

        # 6. Create product recommendation
        rec_id = str(uuid4())
        cursor.execute(
            """
            INSERT INTO product_recommendations (
                id, feedback_cluster_id, created_by, updated_by, version,
                title, description, category,
                requesting_customer_count, total_feedback_items,
                aggregate_impact_score, aggregate_priority_score,
                business_justification, market_opportunity,
                revenue_impact_potential, competitive_positioning,
                recommendation, recommendation_reasoning,
                confidence, suggested_release, release_reasoning,
                estimated_effort, affected_personas, dependencies, risks,
                decision_made, decision_made_by, decision_made_at, decision_notes,
                created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s,
                %s, %s,
                %s, %s,
                %s, %s,
                %s, %s,
                %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s
            )
            """,
            (
                rec_id, cluster_id, user_id, user_id, 1,
                "Dashboard Customization", "Allow users to customize dashboard layout and theme", "UI",
                1, 1,
                82, 85,
                "High-value design partner requesting this feature; strong impact on user retention",
                "Competitive feature; Tableau and Looker offer extensive customization",
                "$500K ARR from Acme renewal contingent on this feature",
                "Differentiator in enterprise segment",
                "build", "High demand + revenue impact + competitive advantage",
                0.88, "Q4_2026", "Can be built in 6-8 weeks with existing design system",
                "large", '["Dashboard Admins", "Power Users"]', '["Design System", "Authentication"]', '["Timeline compression", "Scope creep"]',
                False, None, None, "",
                datetime.utcnow(), datetime.utcnow(),
            ),
        )
        print(f"✅ Created recommendation: {rec_id}")

        # 7. Create audit log entries
        audit_events = [
            ("opportunity_created", "opportunity", opp_id, "Acme Corp opportunity created"),
            ("opportunity_qualified", "opportunity", opp_id, "Qualification score: 82 (qualified for DP)"),
            ("partner_onboarding", "design_partner", partner_id, "Acme Corp onboarded as design partner"),
            ("feedback_submitted", "feedback", feedback_id, "Dashboard customization feedback submitted"),
            ("cluster_created", "feedback_cluster", cluster_id, "Feedback clustered with theme: Dashboard Customization"),
            ("recommendation_generated", "recommendation", rec_id, "Product recommendation generated: BUILD"),
        ]

        for action, res_type, res_id, context in audit_events:
            cursor.execute(
                """
                INSERT INTO security_audit_logs (
                    id, actor_id, actor_role, action, resource_type, resource_id,
                    policy_result, context_data, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    str(uuid4()), user_id, "admin", action, res_type, res_id,
                    "approved", f'{{"event": "{context}"}}', datetime.utcnow(),
                ),
            )
        print(f"✅ Created {len(audit_events)} audit log entries")

        conn.commit()
        print("\n✅ Demo data seeded successfully!")
        print(f"\nDemo Opportunity ID: {opp_id}")
        print(f"Try: GET /api/opportunities/{opp_id}")
        print(f"Try: GET /api/audit/{opp_id}")

    except Exception as e:
        conn.rollback()
        print(f"❌ Error seeding data: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    seed_demo_data()
