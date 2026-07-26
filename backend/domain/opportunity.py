"""Enterprise opportunity model focused on qualification, not CRM."""

from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from .enums import OpportunityStatus, ICPAlignment, MaturityLevel


@dataclass
class Opportunity:
    """
    Enterprise opportunity representing AI governance qualification.

    NOT a sales CRM opportunity. Represents a qualified prospect who could
    become a design partner. Focuses on:
    - Enterprise qualification
    - AI maturity + readiness
    - Security/compliance posture
    - Design partner potential
    """
    id: UUID = field(default_factory=uuid4)
    created_by: UUID = field(default_factory=uuid4)
    updated_by: UUID = field(default_factory=uuid4)
    version: int = 0

    # Company profile
    company_name: str = ""
    company_size_employees: int = 0  # headcount
    industry: str = ""
    location: str = ""
    website: str = ""

    # Qualification
    status: OpportunityStatus = OpportunityStatus.PROSPECT
    icp_alignment: ICPAlignment = ICPAlignment.WEAK
    icp_score: int = 0  # 0-100

    # AI maturity & readiness
    ai_maturity: MaturityLevel = MaturityLevel.NONE
    ai_maturity_evidence: str = ""
    ai_investment_usd: int = 0  # annual spend on AI/ML

    # Security & compliance posture
    security_maturity: MaturityLevel = MaturityLevel.NONE
    security_certifications: List[str] = field(default_factory=list)  # SOC2, ISO27001, etc.
    compliance_needs: List[str] = field(default_factory=list)  # GDPR, HIPAA, etc.

    # Design partner readiness
    design_partner_potential: int = 0  # 0-100: likelihood they'd be good design partner
    has_product_team: bool = False
    product_owner_email: str = ""
    technical_contact_email: str = ""
    executive_sponsor_email: str = ""

    # Qualification evidence
    qualification_evidence: str = ""  # Why qualified?
    strategic_alignment: str = ""  # How aligned with our vision?

    # Context
    notes: str = ""
    source: str = ""  # Where did this opportunity come from?

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def validate(self) -> List[str]:
        """Validate opportunity data."""
        errors = []
        if not self.company_name.strip():
            errors.append("company_name: required")
        if self.company_size_employees < 0:
            errors.append("company_size_employees: must be >= 0")
        if not 0 <= self.icp_score <= 100:
            errors.append("icp_score: must be 0-100")
        if not 0 <= self.design_partner_potential <= 100:
            errors.append("design_partner_potential: must be 0-100")
        if self.ai_investment_usd < 0:
            errors.append("ai_investment_usd: must be >= 0")
        return errors

    def calculate_qualification_score(self) -> int:
        """
        Deterministic: Calculate overall qualification score (0-100).

        Weights:
        - ICP alignment: 40%
        - AI maturity: 30%
        - Security posture: 20%
        - Design partner potential: 10%
        """
        icp_points = self.icp_score * 0.4

        ai_points = {
            MaturityLevel.ADVANCED: 100,
            MaturityLevel.INTERMEDIATE: 70,
            MaturityLevel.BEGINNER: 40,
            MaturityLevel.NONE: 0,
        }.get(self.ai_maturity, 0) * 0.3

        security_points = {
            MaturityLevel.ADVANCED: 100,
            MaturityLevel.INTERMEDIATE: 70,
            MaturityLevel.BEGINNER: 40,
            MaturityLevel.NONE: 0,
        }.get(self.security_maturity, 0) * 0.2

        dp_points = self.design_partner_potential * 0.1

        total = int(min(100, max(0, icp_points + ai_points + security_points + dp_points)))
        return total

    def is_qualified_for_design_partner(self) -> bool:
        """Deterministic: Should this opportunity become a design partner?"""
        return (
            self.calculate_qualification_score() >= 60
            and self.icp_alignment != ICPAlignment.WEAK
            and self.has_product_team
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        data = asdict(self)
        data['id'] = str(self.id)
        data['created_by'] = str(self.created_by)
        data['updated_by'] = str(self.updated_by)
        data['status'] = self.status.value
        data['icp_alignment'] = self.icp_alignment.value
        data['ai_maturity'] = self.ai_maturity.value
        data['security_maturity'] = self.security_maturity.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Opportunity':
        """Deserialize from dictionary."""
        data = data.copy()
        data['id'] = UUID(data['id']) if isinstance(data['id'], str) else data['id']
        data['created_by'] = UUID(data['created_by']) if isinstance(data['created_by'], str) else data['created_by']
        data['updated_by'] = UUID(data['updated_by']) if isinstance(data['updated_by'], str) else data['updated_by']
        data['status'] = OpportunityStatus(data['status']) if isinstance(data['status'], str) else data['status']
        data['icp_alignment'] = ICPAlignment(data['icp_alignment']) if isinstance(data['icp_alignment'], str) else data['icp_alignment']
        data['ai_maturity'] = MaturityLevel(data['ai_maturity']) if isinstance(data['ai_maturity'], str) else data['ai_maturity']
        data['security_maturity'] = MaturityLevel(data['security_maturity']) if isinstance(data['security_maturity'], str) else data['security_maturity']
        data['created_at'] = datetime.fromisoformat(data['created_at']) if isinstance(data['created_at'], str) else data['created_at']
        data['updated_at'] = datetime.fromisoformat(data['updated_at']) if isinstance(data['updated_at'], str) else data['updated_at']
        return cls(**data)
