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
    <html>
    <head>
        <title>PartnerOpsAI Demo</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto; max-width: 900px; margin: 40px auto; padding: 20px; }
            h1 { color: #1e40af; }
            code { background: #f3f4f6; padding: 2px 6px; border-radius: 3px; }
            .button { background: #1e40af; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; display: inline-block; margin: 10px 0; }
            .section { margin: 30px 0; padding: 20px; border: 1px solid #e5e7eb; border-radius: 8px; }
            pre { background: #f9fafb; padding: 15px; border-radius: 5px; overflow-x: auto; }
        </style>
    </head>
    <body>
        <h1>🎯 PartnerOpsAI Demo</h1>
        <p><strong>Enterprise AI Product Decision Support — Qualification Engine</strong></p>

        <div class="section">
            <h2>What's This?</h2>
            <p>PartnerOpsAI qualifies enterprise prospects as design partners using deterministic business logic (no LLM for scoring).</p>
            <p><strong>MVP Status:</strong> This demo exposes the proven qualification workflow. Full product includes feedback clustering, recommendations, and policy evaluation.</p>
        </div>

        <div class="section">
            <h2>Try It</h2>
            <p><a href="/docs" class="button">📖 Interactive API Docs (Swagger UI)</a></p>
            <p><a href="/health" class="button">💚 Health Check</a></p>
        </div>

        <div class="section">
            <h2>How to Qualify</h2>
            <p>POST to <code>/api/qualify</code> with:</p>
            <pre>{
  "company_name": "Acme Corp",
  "company_size_employees": 5000,
  "industry": "Technology",
  "location": "San Francisco",
  "ai_maturity": "advanced",
  "security_maturity": "advanced",
  "icp_score": 85,
  "design_partner_potential": 90,
  "has_product_team": true
}</pre>
            <p><strong>Returns:</strong> qualification_score (0-100), is_qualified_for_design_partner (boolean), reasons</p>
        </div>

        <div class="section">
            <h2>Architecture</h2>
            <ul>
                <li><strong>Domain:</strong> Enterprise opportunity + qualification logic</li>
                <li><strong>Application:</strong> Clean use case pattern</li>
                <li><strong>Infrastructure:</strong> PostgreSQL with RLS</li>
                <li><strong>AI:</strong> Deterministic scoring (no LLM for qualification)</li>
            </ul>
        </div>

        <div class="section">
            <h2>Verification</h2>
            <ul>
                <li>✅ Qualification engine: 100% test coverage, 6/6 tests passing</li>
                <li>✅ Opportunity model: 96% coverage</li>
                <li>✅ Repository pattern: Verified with PostgreSQL</li>
                <li>🟡 Full product: 62.94% coverage (feedback clustering, recommendations pending)</li>
            </ul>
        </div>

        <hr>
        <p style="color: #666; font-size: 14px;">Phase 3.6.1 Demo Build | Code: <a href="https://github.com/sathiyan5092/PartnerOpsAI">GitHub</a></p>
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
