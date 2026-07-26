"""Qualify Enterprise Opportunity use case.

Qualifies a prospect for design partner potential by calculating
enterprise qualification score and assessing fit.
"""

from dataclasses import dataclass
from uuid import UUID
from typing import List, Tuple
from ..domain import Opportunity, OpportunityStatus, MaturityLevel
from .repositories import OpportunityRepository, SecurityAuditRepository
from ..domain.audit import SecurityAuditRecord
from ..domain.enums import AuditAction, PolicyResult


@dataclass
class QualifyOpportunityInput:
    """Input: opportunity data to qualify."""

    company_name: str
    company_size_employees: int
    industry: str
    location: str
    ai_maturity: MaturityLevel
    ai_maturity_evidence: str
    ai_investment_usd: int
    security_maturity: MaturityLevel
    security_certifications: List[str]
    compliance_needs: List[str]
    icp_score: int
    design_partner_potential: int
    has_product_team: bool
    product_owner_email: str
    technical_contact_email: str
    executive_sponsor_email: str
    qualification_evidence: str
    strategic_alignment: str


@dataclass
class QualifyOpportunityOutput:
    """Output: qualification result."""

    opportunity_id: UUID
    qualification_score: int  # 0-100
    is_qualified_for_design_partner: bool
    reasons: List[str]  # Why qualified/not qualified?


class QualifyOpportunityUseCase:
    """
    Assess enterprise opportunity for design partner potential.

    Responsibilities:
    - Validate input
    - Create opportunity domain model
    - Calculate qualification score
    - Determine design partner readiness
    - Persist opportunity
    - Audit the qualification
    """

    def __init__(
        self,
        opportunity_repository: OpportunityRepository,
        audit_repository: SecurityAuditRepository,
        actor_id: UUID,
    ):
        self.opportunity_repo = opportunity_repository
        self.audit_repo = audit_repository
        self.actor_id = actor_id

    def execute(self, input_data: QualifyOpportunityInput) -> QualifyOpportunityOutput:
        """Execute qualification use case."""

        # 1. Create domain model
        opportunity = Opportunity(
            created_by=self.actor_id,
            updated_by=self.actor_id,
            company_name=input_data.company_name,
            company_size_employees=input_data.company_size_employees,
            industry=input_data.industry,
            location=input_data.location,
            ai_maturity=input_data.ai_maturity,
            ai_maturity_evidence=input_data.ai_maturity_evidence,
            ai_investment_usd=input_data.ai_investment_usd,
            security_maturity=input_data.security_maturity,
            security_certifications=input_data.security_certifications,
            compliance_needs=input_data.compliance_needs,
            icp_score=input_data.icp_score,
            design_partner_potential=input_data.design_partner_potential,
            has_product_team=input_data.has_product_team,
            product_owner_email=input_data.product_owner_email,
            technical_contact_email=input_data.technical_contact_email,
            executive_sponsor_email=input_data.executive_sponsor_email,
            qualification_evidence=input_data.qualification_evidence,
            strategic_alignment=input_data.strategic_alignment,
        )

        # 2. Validate
        errors = opportunity.validate()
        if errors:
            raise ValueError(f"Opportunity validation failed: {errors}")

        # 3. Calculate scores (deterministic)
        qualification_score = opportunity.calculate_qualification_score()
        is_qualified = opportunity.is_qualified_for_design_partner()

        # 4. Build reasons
        reasons = self._build_qualification_reasons(
            opportunity, qualification_score, is_qualified
        )

        # 5. Set status based on qualification
        if is_qualified:
            opportunity.status = OpportunityStatus.QUALIFIED
        else:
            opportunity.status = OpportunityStatus.PROSPECT

        # 6. Persist
        opportunity_id = self.opportunity_repo.save(opportunity)

        # 7. Audit
        audit_record = SecurityAuditRecord(
            actor_id=self.actor_id,
            actor_role="qualification_engine",
            action=AuditAction.POLICY_EVALUATED,
            resource_type="opportunity",
            resource_id=opportunity_id,
            policy_name="enterprise_qualification",
            policy_result=(
                PolicyResult.APPROVED if is_qualified else PolicyResult.REVIEW_REQUIRED
            ),
            policy_evaluation_reasoning="; ".join(reasons),
            context_data={
                "qualification_score": qualification_score,
                "icp_score": opportunity.icp_score,
                "ai_maturity": opportunity.ai_maturity.value,
                "security_maturity": opportunity.security_maturity.value,
            },
        )
        self.audit_repo.append(audit_record)

        # 8. Return result
        return QualifyOpportunityOutput(
            opportunity_id=opportunity_id,
            qualification_score=qualification_score,
            is_qualified_for_design_partner=is_qualified,
            reasons=reasons,
        )

    def _build_qualification_reasons(
        self,
        opportunity: Opportunity,
        score: int,
        qualified: bool,
    ) -> List[str]:
        """Build human-readable qualification reasoning."""
        reasons = []

        reasons.append(f"Qualification score: {score}/100")

        if opportunity.icp_score >= 70:
            reasons.append(f"Strong ICP alignment ({opportunity.icp_score}/100)")
        elif opportunity.icp_score < 40:
            reasons.append(f"Weak ICP alignment ({opportunity.icp_score}/100)")

        if opportunity.ai_maturity == MaturityLevel.ADVANCED:
            reasons.append("Advanced AI maturity")
        elif opportunity.ai_maturity == MaturityLevel.NONE:
            reasons.append("No AI maturity (learning opportunity)")

        if opportunity.security_maturity == MaturityLevel.ADVANCED:
            reasons.append(
                f"Strong security posture ({len(opportunity.security_certifications)} certifications)"
            )

        if opportunity.has_product_team:
            reasons.append("Has dedicated product team")
        else:
            reasons.append("No dedicated product team (risk)")

        if not qualified:
            if score < 60:
                reasons.append("Score too low for design partner status")
            if opportunity.icp_score < 50:
                reasons.append("ICP alignment too weak")
            if not opportunity.has_product_team:
                reasons.append("Product team required")

        return reasons
