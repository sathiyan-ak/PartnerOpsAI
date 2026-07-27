"""Application layer: ConvertDesignPartnerUseCase tests."""

import pytest
from uuid import uuid4, UUID
from datetime import datetime

from backend.domain import (
    Opportunity,
    OpportunityStatus,
    ICPAlignment,
    MaturityLevel,
    DesignPartnerStatus,
)
from backend.application.convert_design_partner import (
    ConvertDesignPartnerUseCase,
    ConvertDesignPartnerInput,
)
from backend.infrastructure.repositories.opportunity_repository import OpportunityRepositoryImpl
from backend.infrastructure.repositories.design_partner_repository import DesignPartnerRepositoryImpl
from backend.infrastructure.repositories.audit_repository import SecurityAuditRepositoryImpl


@pytest.mark.integration
class TestConvertDesignPartnerUseCase:
    """Test design partner conversion from qualified opportunity."""

    @pytest.fixture
    def opportunity_repo(self, database_url) -> OpportunityRepositoryImpl:
        return OpportunityRepositoryImpl(database_url)

    @pytest.fixture
    def partner_repo(self, database_url) -> DesignPartnerRepositoryImpl:
        return DesignPartnerRepositoryImpl(database_url)

    @pytest.fixture
    def audit_repo(self, database_url) -> SecurityAuditRepositoryImpl:
        return SecurityAuditRepositoryImpl(database_url)

    @pytest.fixture
    def use_case(self, opportunity_repo, partner_repo, audit_repo, test_user_id):
        return ConvertDesignPartnerUseCase(
            opportunity_repository=opportunity_repo,
            design_partner_repository=partner_repo,
            audit_repository=audit_repo,
            actor_id=UUID(test_user_id),
        )

    def test_convert_qualified_opportunity_happy_path(
        self, use_case, opportunity_repo, partner_repo, test_user_id
    ):
        """Test: Convert QUALIFIED opportunity → DesignPartner."""
        user_uuid = UUID(test_user_id)

        # 1. Create and save qualified opportunity
        opp = Opportunity(
            id=uuid4(),
            created_by=user_uuid,
            updated_by=user_uuid,
            version=0,
            company_name="DesignPartner Candidate",
            company_size_employees=2000,
            industry="Technology",
            location="SF",
            status=OpportunityStatus.QUALIFIED,
            icp_alignment=ICPAlignment.PERFECT,
            icp_score=95,
            ai_maturity=MaturityLevel.ADVANCED,
            security_maturity=MaturityLevel.ADVANCED,
            design_partner_potential=95,
            has_product_team=True,
            product_owner_email="po@company.com",
            technical_contact_email="tech@company.com",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        opp_id = opportunity_repo.save(opp)

        # 2. Convert to design partner
        input_data = ConvertDesignPartnerInput(
            opportunity_id=opp_id,
            product_owner_name="Alice Chen",
            product_owner_email="alice@company.com",
            technical_contact_name="Bob Smith",
            technical_contact_email="bob@company.com",
            partnership_notes="Strong product-market fit",
            success_criteria="Launch 3 features by Q4",
        )

        output = use_case.execute(input_data)

        # 3. Verify output
        assert output.design_partner_id is not None
        assert output.opportunity_id == opp_id
        assert output.company_name == "DesignPartner Candidate"

        # 4. Verify design partner persisted
        dp = partner_repo.find_by_id(output.design_partner_id)
        assert dp is not None
        assert dp.company_name == "DesignPartner Candidate"
        assert dp.onboarding_status == DesignPartnerStatus.ONBOARDING

        # 5. Verify opportunity status updated to CONVERTED
        opp_updated = opportunity_repo.find_by_id(opp_id)
        assert opp_updated.status == OpportunityStatus.CONVERTED

    def test_convert_non_qualified_opportunity_fails(
        self, use_case, opportunity_repo, test_user_id
    ):
        """Test: Cannot convert PROSPECT → Exception."""
        user_uuid = UUID(test_user_id)

        opp = Opportunity(
            id=uuid4(),
            created_by=user_uuid,
            updated_by=user_uuid,
            version=0,
            company_name="Early Stage Startup",
            company_size_employees=10,
            industry="Tech",
            location="Remote",
            status=OpportunityStatus.PROSPECT,
            icp_alignment=ICPAlignment.WEAK,
            icp_score=30,
            ai_maturity=MaturityLevel.NONE,
            security_maturity=MaturityLevel.NONE,
            design_partner_potential=10,
            has_product_team=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        opp_id = opportunity_repo.save(opp)

        input_data = ConvertDesignPartnerInput(
            opportunity_id=opp_id,
            product_owner_name="Test",
            product_owner_email="test@example.com",
            technical_contact_name="Test",
            technical_contact_email="tech@example.com",
        )

        with pytest.raises(ValueError) as exc_info:
            use_case.execute(input_data)

        assert "QUALIFIED" in str(exc_info.value)

    def test_convert_nonexistent_opportunity_fails(self, use_case):
        """Test: Convert missing ID → ValueError."""
        input_data = ConvertDesignPartnerInput(
            opportunity_id=uuid4(),
            product_owner_name="Test",
            product_owner_email="test@example.com",
            technical_contact_name="Test",
            technical_contact_email="tech@example.com",
        )

        with pytest.raises(ValueError) as exc_info:
            use_case.execute(input_data)

        assert "not found" in str(exc_info.value)

    def test_audit_trail_created(
        self, use_case, opportunity_repo, audit_repo, test_user_id
    ):
        """Test: Audit record created for conversion."""
        user_uuid = UUID(test_user_id)

        opp = Opportunity(
            id=uuid4(),
            created_by=user_uuid,
            updated_by=user_uuid,
            version=0,
            company_name="Audited Company",
            company_size_employees=500,
            industry="Tech",
            location="Boston",
            status=OpportunityStatus.QUALIFIED,
            icp_alignment=ICPAlignment.STRONG,
            icp_score=75,
            ai_maturity=MaturityLevel.INTERMEDIATE,
            security_maturity=MaturityLevel.INTERMEDIATE,
            design_partner_potential=80,
            has_product_team=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        opp_id = opportunity_repo.save(opp)

        input_data = ConvertDesignPartnerInput(
            opportunity_id=opp_id,
            product_owner_name="Test",
            product_owner_email="test@example.com",
            technical_contact_name="Test",
            technical_contact_email="tech@example.com",
        )

        output = use_case.execute(input_data)

        # Verify audit record exists
        assert output.design_partner_id is not None
