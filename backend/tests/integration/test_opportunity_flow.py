"""Integration test: Full opportunity qualification flow."""

import pytest
from uuid import uuid4
from backend.domain import Opportunity, OpportunityStatus, MaturityLevel, ICPAlignment


@pytest.mark.integration
class TestOpportunityQualificationFlow:
    """Test complete opportunity lifecycle."""

    def test_opportunity_creation_and_validation(self, test_opportunity_data):
        """Test: Create opportunity and validate data."""
        opp = Opportunity(**test_opportunity_data)

        # Verify
        assert opp.company_name == test_opportunity_data["company_name"]
        assert opp.status == OpportunityStatus.PROSPECT
        assert opp.id is not None

        # Validate
        errors = opp.validate()
        assert len(errors) == 0, f"Validation errors: {errors}"

    def test_qualification_score_calculation(self, test_opportunity_data):
        """Test: Deterministic qualification scoring."""
        test_opportunity_data.update({
            "icp_score": 80,
            "ai_maturity": MaturityLevel.INTERMEDIATE,
            "security_maturity": MaturityLevel.ADVANCED,
            "design_partner_potential": 70,
        })

        opp = Opportunity(**test_opportunity_data)
        score = opp.calculate_qualification_score()

        # Formula: ICP 40% + AI 30% + Security 20% + DP 10%
        # 80*0.4 + 70*0.3 + 100*0.2 + 70*0.1 = 32 + 21 + 20 + 7 = 80
        assert score == 80, f"Expected 80, got {score}"

    def test_design_partner_eligibility(self, test_opportunity_data):
        """Test: Determine design partner eligibility."""
        test_opportunity_data.update({
            "icp_alignment": ICPAlignment.STRONG,
            "icp_score": 70,
            "ai_maturity": MaturityLevel.INTERMEDIATE,
            "security_maturity": MaturityLevel.INTERMEDIATE,
            "design_partner_potential": 70,
            "has_product_team": True,
        })

        opp = Opportunity(**test_opportunity_data)

        # Should be eligible
        assert opp.is_qualified_for_design_partner() is True

    def test_ineligible_low_score(self, test_opportunity_data):
        """Test: Reject low-score prospects."""
        test_opportunity_data.update({
            "icp_alignment": ICPAlignment.STRONG,
            "icp_score": 30,
            "has_product_team": True,
        })

        opp = Opportunity(**test_opportunity_data)
        assert opp.is_qualified_for_design_partner() is False

    def test_ineligible_no_product_team(self, test_opportunity_data):
        """Test: Reject if no product team."""
        test_opportunity_data.update({
            "icp_alignment": ICPAlignment.STRONG,
            "icp_score": 80,
            "has_product_team": False,
        })

        opp = Opportunity(**test_opportunity_data)
        assert opp.is_qualified_for_design_partner() is False

    def test_serialization_roundtrip(self, test_opportunity_data):
        """Test: to_dict/from_dict roundtrip."""
        opp1 = Opportunity(**test_opportunity_data)

        # Serialize
        data = opp1.to_dict()

        # Deserialize
        opp2 = Opportunity.from_dict(data)

        # Verify
        assert opp1.id == opp2.id
        assert opp1.company_name == opp2.company_name
        assert opp1.status == opp2.status
