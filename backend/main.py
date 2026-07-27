"""PartnerOpsAI: Enterprise AI Product Decision Support Demo"""

import os
import sys
from uuid import uuid4, UUID
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from backend.infrastructure.repositories.opportunity_repository import OpportunityRepositoryImpl
from backend.infrastructure.repositories.audit_repository import SecurityAuditRepositoryImpl
from backend.application.qualify_opportunity import (
    QualifyOpportunityUseCase,
    QualifyOpportunityInput,
)
from backend.domain import MaturityLevel, Opportunity

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
    print(f"⚠ Using localhost database (development mode)", file=sys.stderr)
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
        raise HTTPException(status_code=500, detail=f"Seed error: {str(e)}")


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
    reasons: List[str]


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PartnerOpsAI — Enterprise Qualification Engine</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
                background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
                color: #e2e8f0;
                line-height: 1.6;
                min-height: 100vh;
            }

            .container { max-width: 1200px; margin: 0 auto; padding: 60px 20px; }

            header {
                text-align: center;
                margin-bottom: 80px;
                animation: fadeInDown 0.8s ease;
            }

            .logo { font-size: 48px; margin-bottom: 16px; }
            h1 { font-size: 48px; font-weight: 700; margin-bottom: 12px; background: linear-gradient(120deg, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
            .tagline { font-size: 20px; color: #94a3b8; margin-bottom: 8px; }
            .subtitle { font-size: 16px; color: #64748b; max-width: 600px; margin: 0 auto; }

            .cta-buttons { margin-top: 32px; display: flex; gap: 16px; justify-content: center; flex-wrap: wrap; }
            .btn {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 14px 32px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                text-decoration: none;
                border: none;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .btn-primary {
                background: linear-gradient(120deg, #3b82f6, #2563eb);
                color: white;
            }
            .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 12px 24px rgba(59, 130, 246, 0.4); }
            .btn-secondary {
                background: rgba(75, 85, 99, 0.3);
                color: #cbd5e1;
                border: 1px solid rgba(148, 163, 184, 0.2);
            }
            .btn-secondary:hover { background: rgba(75, 85, 99, 0.5); }

            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px; margin: 60px 0; }

            .card {
                background: rgba(51, 65, 85, 0.5);
                border: 1px solid rgba(148, 163, 184, 0.2);
                border-radius: 12px;
                padding: 32px;
                transition: all 0.3s ease;
                backdrop-filter: blur(10px);
            }
            .card:hover {
                background: rgba(51, 65, 85, 0.7);
                border-color: rgba(148, 163, 184, 0.4);
                transform: translateY(-4px);
            }

            .card-icon { font-size: 32px; margin-bottom: 16px; }
            .card h3 { font-size: 20px; margin-bottom: 12px; color: #f1f5f9; }
            .card p { color: #cbd5e1; font-size: 14px; }

            .features { margin-top: 60px; }
            .features h2 { font-size: 32px; margin-bottom: 32px; text-align: center; }
            .feature-list { list-style: none; }
            .feature-list li {
                padding: 12px 0;
                display: flex;
                align-items: center;
                gap: 12px;
                font-size: 16px;
            }
            .feature-list li:before { content: "✓"; color: #10b981; font-weight: bold; font-size: 20px; }

            .code-section { background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 8px; padding: 24px; margin: 40px 0; }
            .code-section h3 { margin-bottom: 16px; color: #f1f5f9; }
            pre {
                background: rgba(30, 27, 75, 0.8);
                padding: 16px;
                border-radius: 6px;
                overflow-x: auto;
                font-size: 13px;
                color: #a1d3b0;
                line-height: 1.5;
            }

            .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 40px 0; }
            .stat {
                text-align: center;
                padding: 24px;
                background: rgba(51, 65, 85, 0.3);
                border-radius: 8px;
            }
            .stat-value { font-size: 32px; font-weight: 700; color: #60a5fa; }
            .stat-label { color: #94a3b8; font-size: 14px; margin-top: 8px; }

            footer {
                text-align: center;
                margin-top: 80px;
                padding-top: 40px;
                border-top: 1px solid rgba(148, 163, 184, 0.1);
                color: #64748b;
                font-size: 14px;
            }

            footer a { color: #60a5fa; text-decoration: none; }
            footer a:hover { text-decoration: underline; }

            @keyframes fadeInDown {
                from { opacity: 0; transform: translateY(-20px); }
                to { opacity: 1; transform: translateY(0); }
            }

            @media (max-width: 768px) {
                h1 { font-size: 32px; }
                .tagline { font-size: 18px; }
                .cta-buttons { flex-direction: column; }
                .btn { width: 100%; justify-content: center; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <div class="logo">🎯</div>
                <h1>PartnerOpsAI</h1>
                <p class="tagline">Enterprise Qualification Engine</p>
                <p class="subtitle">Automatically score enterprise prospects for design partner potential. Deterministic AI scoring without LLM black boxes.</p>

                <div class="cta-buttons">
                    <a href="/docs" class="btn btn-primary">📖 Try the API</a>
                    <a href="/health" class="btn btn-secondary">💚 Health Check</a>
                </div>
            </header>

            <div class="grid">
                <div class="card">
                    <div class="card-icon">⚡</div>
                    <h3>Instant Qualification</h3>
                    <p>Score enterprise prospects in milliseconds. AI maturity, security posture, team readiness — all in one call.</p>
                </div>
                <div class="card">
                    <div class="card-icon">🔍</div>
                    <h3>Deterministic Scoring</h3>
                    <p>No LLM black boxes. All scoring is auditable code. Reproducible results every time.</p>
                </div>
                <div class="card">
                    <div class="card-icon">🗄️</div>
                    <h3>PostgreSQL Backed</h3>
                    <p>Immutable audit logs. Full RLS. Enterprise-ready data governance out of the box.</p>
                </div>
            </div>

            <div class="features">
                <h2>What You Get</h2>
                <ul class="feature-list">
                    <li>Qualify prospects by ICP score, AI maturity, security readiness, design partner potential</li>
                    <li>Deterministic scoring algorithm: ICP 40% + AI 30% + Security 20% + Partnership 10%</li>
                    <li>Immutable audit trail of every qualification decision</li>
                    <li>Clean Architecture: testable, swappable repositories</li>
                    <li>9 REST API endpoints for full workflow</li>
                    <li>Interactive Swagger UI for testing</li>
                </ul>
            </div>

            <div class="code-section">
                <h3>Quick Start</h3>
                <p style="margin-bottom: 16px;">POST /api/qualify with company details:</p>
                <pre>{
  "company_name": "Acme Corporation",
  "company_size_employees": 5000,
  "industry": "Technology",
  "location": "San Francisco",
  "ai_maturity": "advanced",
  "security_maturity": "advanced",
  "icp_score": 95,
  "design_partner_potential": 90,
  "has_product_team": true
}</pre>
                <p style="margin-top: 16px; color: #cbd5e1; font-size: 14px;"><strong>Response:</strong> qualification_score (0-100), is_qualified_for_design_partner (boolean), reasons array</p>
            </div>

            <div class="stats">
                <div class="stat">
                    <div class="stat-value">9</div>
                    <div class="stat-label">API Endpoints</div>
                </div>
                <div class="stat">
                    <div class="stat-value">100%</div>
                    <div class="stat-label">Audit Trail</div>
                </div>
                <div class="stat">
                    <div class="stat-value">Clean</div>
                    <div class="stat-label">Architecture</div>
                </div>
                <div class="stat">
                    <div class="stat-value">PostgreSQL</div>
                    <div class="stat-label">Database</div>
                </div>
            </div>

            <footer>
                <p>Phase 3.6.5 Demo | <a href="https://github.com/sathiyan-ak/PartnerOpsAI">View on GitHub</a></p>
            </footer>
        </div>
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
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


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
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


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
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


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
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
