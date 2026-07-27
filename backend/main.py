"""PartnerOpsAI: Enterprise AI Product Decision Support Demo"""

import os
import sys
from uuid import UUID

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from backend.application.qualify_opportunity import (
    QualifyOpportunityInput,
    QualifyOpportunityUseCase,
)
from backend.domain import MaturityLevel
from backend.infrastructure.repositories.audit_repository import (
    SecurityAuditRepositoryImpl,
)
from backend.infrastructure.repositories.opportunity_repository import (
    OpportunityRepositoryImpl,
)

app = FastAPI(
    title="PartnerOpsAI",
    description="Enterprise AI Product Decision Support Demo",
    version="3.6.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Try multiple possible database URL environment variable names
# Handle Railway's individual env vars (PGHOST, PGUSER, PGPASSWORD, PGDATABASE, PGPORT)
db_url = os.getenv("DATABASE_URL")
if not db_url:
    pghost = os.getenv("PGHOST")
    pguser = os.getenv("PGUSER")
    pgpassword = os.getenv("PGPASSWORD")
    pgdatabase = os.getenv("PGDATABASE")
    pgport = os.getenv("PGPORT", "5432")

    if all([pghost, pguser, pgpassword, pgdatabase]):
        db_url = f"postgresql://{pguser}:{pgpassword}@{pghost}:{pgport}/{pgdatabase}"

db_url = (
    db_url
    or os.getenv("POSTGRES_URL")  # Railway Postgres plugin alternate
    or os.getenv("PGURL")
    or "postgresql://test_user:test_password@localhost:5432/partneropsa_test"
)

# Log which database is being used
if "localhost" in db_url:
    print("⚠ Using localhost database (development mode)", file=sys.stderr)
else:
    print(f"✓ Using remote database: {db_url.split('@')[1][:50] if '@' in db_url else '...'}", file=sys.stderr)

opp_repo = OpportunityRepositoryImpl(db_url)
audit_repo = SecurityAuditRepositoryImpl(db_url)
actor_id = UUID("00000000-0000-0000-0000-000000000001")

# Initialize test user for demo
def _init_demo_user():
    try:
        import psycopg2
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (id, email) VALUES (%s, %s) ON CONFLICT (id) DO NOTHING",
            (str(actor_id), "demo@partneropsa.com")
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception:
        pass

_init_demo_user()


@app.post("/api/seed-demo-data")
async def seed_demo_data():
    """
    Populate database with realistic demo company (Acme Corp).
    Run once to load demo data, then use GET endpoints to retrieve.
    """
    try:
        from backend.seed import seed_demo_data as seed_func
        seed_func()
        return {"status": "ok", "message": "Demo data seeded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Seed error: {e!s}")


class QualifyRequest(BaseModel):
    company_name: str
    company_size_employees: int
    industry: str
    location: str
    ai_maturity: str
    security_maturity: str
    icp_score: int
    design_partner_potential: int
    has_product_team: bool


class QualifyResponse(BaseModel):
    opportunity_id: str
    qualification_score: int
    is_qualified_for_design_partner: bool
    reasons: list[str]


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Identify Your Design Partners | PartnerOps</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            html { scroll-behavior: smooth; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", sans-serif;
                background: #ffffff;
                color: #1f2937;
                line-height: 1.5;
                letter-spacing: -0.3px;
            }

            header {
                background: linear-gradient(135deg, #ffffff 0%, #f9fafb 100%);
                border-bottom: 1px solid #e5e7eb;
                padding: 24px 20px;
                position: sticky;
                top: 0;
                z-index: 100;
            }

            nav {
                max-width: 1280px;
                margin: 0 auto;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .logo-text { font-size: 20px; font-weight: 700; color: #000; }
            .logo-text span { color: #2563eb; }

            .nav-links { display: flex; gap: 32px; }
            .nav-links a { text-decoration: none; color: #6b7280; font-size: 14px; font-weight: 500; transition: color 0.2s; }
            .nav-links a:hover { color: #000; }

            .hero {
                max-width: 900px;
                margin: 0 auto;
                padding: 120px 20px 100px;
                text-align: center;
            }

            .hero h1 {
                font-size: 56px;
                font-weight: 800;
                line-height: 1.1;
                margin-bottom: 24px;
                color: #000;
            }

            .hero .highlight { color: #2563eb; }

            .hero p {
                font-size: 20px;
                color: #4b5563;
                margin-bottom: 40px;
                max-width: 600px;
                margin-left: auto;
                margin-right: auto;
            }

            .cta { display: flex; gap: 16px; justify-content: center; margin-bottom: 80px; flex-wrap: wrap; }
            .btn {
                padding: 14px 32px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 15px;
                border: none;
                cursor: pointer;
                text-decoration: none;
                transition: all 0.2s;
                display: inline-flex;
                align-items: center;
                gap: 8px;
            }

            .btn-primary {
                background: #2563eb;
                color: white;
            }
            .btn-primary:hover { background: #1d4ed8; transform: translateY(-1px); }

            .btn-secondary {
                background: #f3f4f6;
                color: #1f2937;
                border: 1px solid #d1d5db;
            }
            .btn-secondary:hover { background: #e5e7eb; }

            .features-grid {
                max-width: 1280px;
                margin: 0 auto;
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 32px;
                padding: 0 20px 100px;
            }

            .feature {
                background: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 32px;
                transition: all 0.3s;
            }

            .feature:hover {
                border-color: #2563eb;
                box-shadow: 0 10px 30px rgba(37, 99, 235, 0.1);
                transform: translateY(-2px);
            }

            .feature-icon { font-size: 32px; margin-bottom: 16px; }
            .feature h3 { font-size: 18px; font-weight: 700; margin-bottom: 12px; color: #000; }
            .feature p { color: #6b7280; font-size: 14px; line-height: 1.6; }

            .benefits {
                max-width: 1280px;
                margin: 0 auto;
                padding: 100px 20px;
                background: #f9fafb;
            }

            .benefits h2 {
                font-size: 36px;
                font-weight: 800;
                margin-bottom: 48px;
                text-align: center;
                color: #000;
            }

            .benefits-list {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
                gap: 32px;
            }

            .benefit-item {
                display: flex;
                gap: 12px;
            }

            .benefit-check {
                font-size: 20px;
                font-weight: 700;
                color: #10b981;
                flex-shrink: 0;
            }

            .benefit-item p {
                color: #374151;
                font-size: 15px;
                font-weight: 500;
            }

            .stats-section {
                max-width: 1280px;
                margin: 0 auto;
                padding: 80px 20px;
            }

            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 40px;
                text-align: center;
            }

            .stat { padding: 20px 0; }
            .stat-number { font-size: 40px; font-weight: 800; color: #2563eb; margin-bottom: 8px; }
            .stat-label { color: #6b7280; font-size: 14px; font-weight: 500; }

            .cta-final {
                max-width: 800px;
                margin: 0 auto;
                text-align: center;
                padding: 100px 20px;
            }

            .cta-final h2 {
                font-size: 40px;
                font-weight: 800;
                margin-bottom: 24px;
                color: #000;
            }

            .cta-final p {
                font-size: 16px;
                color: #6b7280;
                margin-bottom: 32px;
            }

            footer {
                background: #1f2937;
                color: #d1d5db;
                padding: 40px 20px;
                text-align: center;
                font-size: 13px;
            }

            footer a { color: #60a5fa; text-decoration: none; }
            footer a:hover { text-decoration: underline; }

            @media (max-width: 768px) {
                .hero h1 { font-size: 36px; }
                .hero p { font-size: 16px; }
                .nav-links { gap: 16px; font-size: 13px; }
                .benefits h2 { font-size: 28px; }
                .cta-final h2 { font-size: 28px; }
                .stats-number { font-size: 32px; }
            }
        </style>
    </head>
    <body>
        <header>
            <nav>
                <div class="logo-text">Partner<span>Ops</span></div>
                <div class="nav-links">
                    <a href="/docs">API Docs</a>
                    <a href="https://github.com/sathiyan-ak/PartnerOpsAI">GitHub</a>
                </div>
            </nav>
        </header>

        <main>
            <section class="hero">
                <h1>Identify Your Next <span class="highlight">Design Partners</span></h1>
                <p>Score enterprise prospects in real-time. Know instantly which customers are ready to partner with you.</p>
                <div class="cta">
                    <a href="/docs" class="btn btn-primary">Try the API</a>
                    <a href="/health" class="btn btn-secondary">Live Status</a>
                </div>
            </section>

            <section class="features-grid">
                <div class="feature">
                    <div class="feature-icon">⚡</div>
                    <h3>Instant Scoring</h3>
                    <p>Get qualification scores in milliseconds. No waiting. Know if a prospect is partnership-ready before your next call.</p>
                </div>
                <div class="feature">
                    <div class="feature-icon">🔒</div>
                    <h3>Transparent Logic</h3>
                    <p>Every decision is auditable code. No black boxes. See exactly why each prospect qualified or didn't.</p>
                </div>
                <div class="feature">
                    <div class="feature-icon">📊</div>
                    <h3>Enterprise-Grade</h3>
                    <p>ACID-compliant database. Immutable audit logs. Security-first architecture for regulated industries.</p>
                </div>
            </section>

            <section class="benefits">
                <h2>Why Partner Qualification Matters</h2>
                <div class="benefits-list">
                    <div class="benefit-item">
                        <div class="benefit-check">✓</div>
                        <p>Find customers with strong team maturity and clear product focus</p>
                    </div>
                    <div class="benefit-item">
                        <div class="benefit-check">✓</div>
                        <p>Score by ICP alignment, security posture, and growth readiness</p>
                    </div>
                    <div class="benefit-item">
                        <div class="benefit-check">✓</div>
                        <p>Automate prospect screening to focus sales on high-potential deals</p>
                    </div>
                    <div class="benefit-item">
                        <div class="benefit-check">✓</div>
                        <p>Track every decision with complete audit trail for compliance</p>
                    </div>
                    <div class="benefit-item">
                        <div class="benefit-check">✓</div>
                        <p>Reproducible results — same company gets same score every time</p>
                    </div>
                    <div class="benefit-item">
                        <div class="benefit-check">✓</div>
                        <p>REST API + Swagger UI for easy integration and testing</p>
                    </div>
                </div>
            </section>

            <section class="stats-section">
                <div class="stats-grid">
                    <div class="stat">
                        <div class="stat-number">9</div>
                        <div class="stat-label">API Endpoints</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">55+</div>
                        <div class="stat-label">Tests Passing</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">100%</div>
                        <div class="stat-label">Audit Logged</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">PostgreSQL</div>
                        <div class="stat-label">Enterprise DB</div>
                    </div>
                </div>
            </section>

            <section class="cta-final">
                <h2>Ready to Start Scoring?</h2>
                <p>Integrate our API in minutes. Works with your existing sales platform.</p>
                <div class="cta">
                    <a href="/docs" class="btn btn-primary">View API Documentation</a>
                </div>
            </section>
        </main>

        <footer>
            <p>PartnerOps Demo | <a href="https://github.com/sathiyan-ak/PartnerOpsAI">Source on GitHub</a></p>
        </footer>
    </body>
    </html>
    """


@app.get("/health")
async def health():
    return {"status": "ok", "service": "PartnerOpsAI Demo", "version": "3.6.1"}


@app.post("/api/qualify", response_model=QualifyResponse)
async def qualify(request: QualifyRequest):
    """
    Qualify an enterprise prospect for design partner potential.

    Returns qualification_score (0-100) and whether they qualify for design partner program.
    Scoring: ICP 40% + AI Maturity 30% + Security 20% + DP Potential 10%
    """
    try:
        input_data = QualifyOpportunityInput(
            company_name=request.company_name,
            company_size_employees=request.company_size_employees,
            industry=request.industry,
            location=request.location,
            ai_maturity=MaturityLevel(request.ai_maturity.lower()),
            ai_maturity_evidence=f"{request.company_name} AI maturity assessment",
            ai_investment_usd=100000,  # Default for demo
            security_maturity=MaturityLevel(request.security_maturity.lower()),
            security_certifications=[],
            compliance_needs=[],
            icp_score=request.icp_score,
            design_partner_potential=request.design_partner_potential,
            has_product_team=request.has_product_team,
            product_owner_email=f"po@{request.company_name.lower().replace(' ', '')}.com",
            technical_contact_email=f"tech@{request.company_name.lower().replace(' ', '')}.com",
            executive_sponsor_email=f"exec@{request.company_name.lower().replace(' ', '')}.com",
            qualification_evidence="Demo qualification",
            strategic_alignment="Demo assessment",
        )

        use_case = QualifyOpportunityUseCase(
            opportunity_repository=opp_repo,
            audit_repository=audit_repo,
            actor_id=actor_id,
        )

        output = use_case.execute(input_data)

        return QualifyResponse(
            opportunity_id=str(output.opportunity_id),
            qualification_score=output.qualification_score,
            is_qualified_for_design_partner=output.is_qualified_for_design_partner,
            reasons=output.reasons,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e!s}")


@app.get("/api/status")
async def status():
    """Service status and version info"""
    return {
        "service": "PartnerOpsAI",
        "version": "3.6.1",
        "phase": "3.6.1 Demo Build",
        "features": ["enterprise_qualification"],
        "database": "PostgreSQL",
        "architecture": "Clean Architecture (Domain → Application → Infrastructure)",
    }


class OpportunityResponse(BaseModel):
    opportunity_id: str
    company_name: str
    industry: str
    location: str
    company_size_employees: int
    icp_score: int
    design_partner_potential: int
    created_at: str


class AuditLogEntry(BaseModel):
    id: str
    action: str
    resource_type: str
    resource_id: str
    actor_id: str
    created_at: str
    context_data: dict


@app.post("/api/opportunities", response_model=OpportunityResponse)
async def create_opportunity(request: QualifyRequest):
    """
    Create a prospect opportunity (without qualification).
    Returns opportunity_id for later qualification.
    """
    try:
        input_data = QualifyOpportunityInput(
            company_name=request.company_name,
            company_size_employees=request.company_size_employees,
            industry=request.industry,
            location=request.location,
            ai_maturity=MaturityLevel(request.ai_maturity.lower()),
            ai_maturity_evidence=f"{request.company_name} AI maturity assessment",
            ai_investment_usd=100000,
            security_maturity=MaturityLevel(request.security_maturity.lower()),
            security_certifications=[],
            compliance_needs=[],
            icp_score=request.icp_score,
            design_partner_potential=request.design_partner_potential,
            has_product_team=request.has_product_team,
            product_owner_email=f"po@{request.company_name.lower().replace(' ', '')}.com",
            technical_contact_email=f"tech@{request.company_name.lower().replace(' ', '')}.com",
            executive_sponsor_email=f"exec@{request.company_name.lower().replace(' ', '')}.com",
            qualification_evidence="Demo opportunity",
            strategic_alignment="Demo assessment",
        )

        use_case = QualifyOpportunityUseCase(
            opportunity_repository=opp_repo,
            audit_repository=audit_repo,
            actor_id=actor_id,
        )

        output = use_case.execute(input_data)
        opp = opp_repo.find_by_id(output.opportunity_id)

        return OpportunityResponse(
            opportunity_id=str(output.opportunity_id),
            company_name=opp.company_name,
            industry=opp.industry,
            location=opp.location,
            company_size_employees=opp.company_size_employees,
            icp_score=opp.icp_score,
            design_partner_potential=opp.design_partner_potential,
            created_at=opp.created_at.isoformat() if opp.created_at else "",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e!s}")


@app.get("/api/opportunities/{opportunity_id}", response_model=OpportunityResponse)
async def get_opportunity(opportunity_id: str):
    """
    Retrieve opportunity details by ID.
    """
    try:
        opp = opp_repo.find_by_id(UUID(opportunity_id))
        if not opp:
            raise HTTPException(status_code=404, detail="Opportunity not found")

        return OpportunityResponse(
            opportunity_id=str(opp.id),
            company_name=opp.company_name,
            industry=opp.industry,
            location=opp.location,
            company_size_employees=opp.company_size_employees,
            icp_score=opp.icp_score,
            design_partner_potential=opp.design_partner_potential,
            created_at=opp.created_at.isoformat() if opp.created_at else "",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e!s}")


@app.get("/api/audit/{resource_id}")
async def get_audit_trail(resource_id: str):
    """
    Retrieve audit trail for a resource.
    Shows all security events logged for this opportunity.
    """
    try:
        # Fetch recent audit records for this resource
        import psycopg2
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, action, resource_type, resource_id, actor_id, created_at, context_data
            FROM security_audit_logs
            WHERE resource_id = %s
            ORDER BY created_at DESC
            LIMIT 50
            """,
            (resource_id,),
        )

        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        audit_entries = [
            {
                "id": str(row[0]),
                "action": row[1],
                "resource_type": row[2],
                "resource_id": str(row[3]),
                "actor_id": str(row[4]),
                "created_at": row[5].isoformat() if row[5] else "",
                "context_data": row[6] or {},
            }
            for row in rows
        ]

        return {
            "resource_id": resource_id,
            "audit_entries": audit_entries,
            "total_events": len(audit_entries),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e!s}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
