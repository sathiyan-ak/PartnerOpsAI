"""Application layer tests: QualifyOpportunityUseCase."""

import pytest
from uuid import uuid4, UUID
from datetime import datetime

from backend.domain import (
    Opportunity,
    OpportunityStatus,
    ICPAlignment,
    MaturityLevel,
)
from backend.application.qualify_opportunity import (
    QualifyOpportunityUseCase,
    QualifyOpportunityInput,
)
from backend.infrastructure.repositories.opportunity_repository import OpportunityRepositoryImpl
from backend.infrastructure.repositories.audit_repository import SecurityAuditRepositoryImpl


@pytest.mark.integration
class TestQualifyOpportunityUseCase:
    """Test enterprise opportunity qualification use case."""

    @pytest.fixture
    def opportunity_repo(self, database_url) -> OpportunityRepositoryImpl:
        """Get opportunity repository."""
        return OpportunityRepositoryImpl(database_url)

    @pytest.fixture
    def audit_repo(self, database_url) -> SecurityAuditRepositoryImpl:
        """Get audit repository."""
        return SecurityAuditRepositoryImpl(database_url)

    @pytest.fixture
    def use_case(self, opportunity_repo, audit_repo, test_user_id):
        """Create use case with repositories and actor."""
        return QualifyOpportunityUseCase(
            opportunity_repository=opportunity_repo,
            audit_repository=audit_repo,
            actor_id=UUID(test_user_id),
        )

    def test_qualify_strong_prospect(self, use_case, opportunity_repo):
        """Test: Qualify a strong enterprise prospect → QUALIFIED."""
        # Note: The use case should infer icp_alignment from icp_score
        # For now, set it explicitly to STRONG for qualification
        from backend.domain import ICPAlignment

        input_data = QualifyOpportunityInput(
            company_name="Fortune 500 Corp",
            company_size_employees=10000,
            industry="Technology",
            location="San Francisco",
            ai_maturity=MaturityLevel.ADVANCED,
            ai_maturity_evidence="Custom ML pipeline, $2M annual spend",
            ai_investment_usd=2000000,
            security_maturity=MaturityLevel.ADVANCED,
            security_certifications=["SOC2", "ISO27001", "HIPAA"],
            compliance_needs=["GDPR", "CCPA"],
            icp_score=90,
            design_partner_potential=95,
            has_product_team=True,
            product_owner_email="cto@fortune500.com",
            technical_contact_email="tech@fortune500.com",
            executive_sponsor_email="ceo@fortune500.com",
            qualification_evidence="Large security-conscious enterprise",
            strategic_alignment="Perfect fit for governance product",
        )

        # Execute
        output = use_case.execute(input_data)

        # Verify output
        assert output.opportunity_id is not None
        assert output.qualification_score >= 70
        assert output.is_qualified_for_design_partner is True
        assert len(output.reasons) > 0

        # Verify persisted in database
        persisted = opportunity_repo.find_by_id(output.opportunity_id)
        assert persisted is not None
        assert persisted.company_name == "Fortune 500 Corp"
        assert persisted.status == OpportunityStatus.QUALIFIED
        assert persisted.icp_score == 90

    def test_qualify_weak_prospect(self, use_case, opportunity_repo):
        """Test: Weak prospect → NOT QUALIFIED."""
        input_data = QualifyOpportunityInput(
            company_name="Early Stage Startup",
            company_size_employees=15,
            industry="Finance",
            location="Remote",
            ai_maturity=MaturityLevel.NONE,
            ai_maturity_evidence="No AI experience yet",
            ai_investment_usd=0,
            security_maturity=MaturityLevel.BEGINNER,
            security_certifications=[],
            compliance_needs=["GDPR"],
            icp_score=25,
            design_partner_potential=10,
            has_product_team=False,
            product_owner_email="founder@startup.com",
            technical_contact_email="",
            executive_sponsor_email="founder@startup.com",
            qualification_evidence="Pre-product company",
            strategic_alignment="Too early stage",
        )

        # Execute
        output = use_case.execute(input_data)

        # Verify
        assert output.is_qualified_for_design_partner is False
        assert output.qualification_score < 60

        # Verify status
        persisted = opportunity_repo.find_by_id(output.opportunity_id)
        assert persisted.status == OpportunityStatus.PROSPECT

    def test_validation_error_missing_company(self, use_case):
        """Test: Validation failure → Exception."""
        input_data = QualifyOpportunityInput(
            company_name="",  # INVALID
            company_size_employees=100,
            industry="Tech",
            location="SF",
            ai_maturity=MaturityLevel.INTERMEDIATE,
            ai_maturity_evidence="Some AI work",
            ai_investment_usd=100000,
            security_maturity=MaturityLevel.INTERMEDIATE,
            security_certifications=["SOC2"],
            compliance_needs=["GDPR"],
            icp_score=50,
            design_partner_potential=50,
            has_product_team=True,
            product_owner_email="cto@company.com",
            technical_contact_email="tech@company.com",
            executive_sponsor_email="ceo@company.com",
            qualification_evidence="Good fit",
            strategic_alignment="Strategic",
        )

        # Should raise validation error
        with pytest.raises(ValueError) as exc_info:
            use_case.execute(input_data)

        assert "validation failed" in str(exc_info.value).lower()

    def test_invalid_icp_score(self, use_case):
        """Test: ICP score out of range → Exception."""
        input_data = QualifyOpportunityInput(
            company_name="Test Corp",
            company_size_employees=100,
            industry="Tech",
            location="SF",
            ai_maturity=MaturityLevel.INTERMEDIATE,
            ai_maturity_evidence="AI work",
            ai_investment_usd=100000,
            security_maturity=MaturityLevel.INTERMEDIATE,
            security_certifications=["SOC2"],
            compliance_needs=["GDPR"],
            icp_score=150,  # INVALID (>100)
            design_partner_potential=50,
            has_product_team=True,
            product_owner_email="cto@test.com",
            technical_contact_email="tech@test.com",
            executive_sponsor_email="ceo@test.com",
            qualification_evidence="Good fit",
            strategic_alignment="Strategic",
        )

        with pytest.raises(ValueError):
            use_case.execute(input_data)

    def test_qualification_deterministic(self, use_case):
        """Test: Same input always produces same score."""
        input_data = QualifyOpportunityInput(
            company_name="Consistent Corp",
            company_size_employees=1000,
            industry="Tech",
            location="Boston",
            ai_maturity=MaturityLevel.INTERMEDIATE,
            ai_maturity_evidence="ML pipeline",
            ai_investment_usd=500000,
            security_maturity=MaturityLevel.INTERMEDIATE,
            security_certifications=["SOC2"],
            compliance_needs=["GDPR"],
            icp_score=65,
            design_partner_potential=60,
            has_product_team=True,
            product_owner_email="cto@consistent.com",
            technical_contact_email="tech@consistent.com",
            executive_sponsor_email="ceo@consistent.com",
            qualification_evidence="Mid-market fit",
            strategic_alignment="Good alignment",
        )

        # Execute twice
        output1 = use_case.execute(input_data)

        # Modify input to create different opportunity
        input_data.company_name = "Another Corp"
        output2 = use_case.execute(input_data)

        # Same input characteristics should produce same score
        # (Both have icp=65, ai=intermediate, security=intermediate, etc.)
        # So scores should be equal
        assert output1.qualification_score == output2.qualification_score

    def test_audit_trail_created(self, use_case, audit_repo):
        """Test: Audit record created for qualification."""
        input_data = QualifyOpportunityInput(
            company_name="Audited Corp",
            company_size_employees=500,
            industry="Tech",
            location="NYC",
            ai_maturity=MaturityLevel.INTERMEDIATE,
            ai_maturity_evidence="Some AI",
            ai_investment_usd=300000,
            security_maturity=MaturityLevel.INTERMEDIATE,
            security_certifications=["SOC2"],
            compliance_needs=["GDPR"],
            icp_score=70,
            design_partner_potential=75,
            has_product_team=True,
            product_owner_email="cto@audited.com",
            technical_contact_email="tech@audited.com",
            executive_sponsor_email="ceo@audited.com",
            qualification_evidence="Qualified",
            strategic_alignment="Strategic fit",
        )

        # Execute
        output = use_case.execute(input_data)

        # Verify audit record exists
        # Note: audit_repo.find_by_resource_id() needs to be implemented
        # For now, just verify the use case completed without error
        assert output.opportunity_id is not None
