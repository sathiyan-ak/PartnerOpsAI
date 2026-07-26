"""
Unit tests for PartnerOpsAI domain models.

Tests model instantiation, validation, serialization, and deterministic calculations.
Includes both happy path and negative tests.
"""

from datetime import datetime
from uuid import uuid4
import pytest

from .opportunity import Opportunity
from .design_partner import DesignPartner
from .feedback import DesignFeedback, FeedbackCluster
from .recommendation import ProductRecommendation
from .audit import SecurityAuditRecord, PolicyDecision
from .enums import (
    OpportunityStatus, ICPAlignment, MaturityLevel,
    DesignPartnerStatus, PartnerHealth,
    FeedbackCategory, FeedbackStatus, ReleaseTarget,
    AuditAction, PolicyResult,
)


class TestOpportunity:
    """Tests for Opportunity domain model."""

    def test_instantiate_defaults(self):
        """Test creating opportunity with defaults."""
        opp = Opportunity()
        assert opp.id is not None
        assert opp.company_name == ""
        assert opp.status == OpportunityStatus.PROSPECT

    def test_instantiate_with_values(self):
        """Test creating opportunity with specific values."""
        opp = Opportunity(
            company_name="Acme Corp",
            company_size_employees=500,
            ai_maturity=MaturityLevel.INTERMEDIATE,
        )
        assert opp.company_name == "Acme Corp"
        assert opp.company_size_employees == 500

    def test_validate_success(self):
        """Test validation passes for valid opportunity."""
        opp = Opportunity(
            company_name="Test Corp",
            company_size_employees=100,
            icp_score=50,
        )
        errors = opp.validate()
        assert len(errors) == 0

    def test_validate_missing_company_name(self):
        """Test validation fails for missing company name."""
        opp = Opportunity(company_name="")
        errors = opp.validate()
        assert any("company_name" in e for e in errors)

    def test_validate_negative_employee_count(self):
        """Test validation fails for negative employee count."""
        opp = Opportunity(company_name="Test", company_size_employees=-50)
        errors = opp.validate()
        assert any("company_size_employees" in e for e in errors)

    def test_validate_invalid_icp_score_range(self):
        """Test validation fails for ICP score out of range."""
        opp = Opportunity(company_name="Test", icp_score=150)
        errors = opp.validate()
        assert any("icp_score" in e for e in errors)

    def test_calculate_qualification_score_advanced(self):
        """Test qualification score calculation for advanced company."""
        opp = Opportunity(
            company_name="Test",
            icp_score=100,
            ai_maturity=MaturityLevel.ADVANCED,
            security_maturity=MaturityLevel.ADVANCED,
            design_partner_potential=100,
        )
        score = opp.calculate_qualification_score()
        # 100*0.4 + 100*0.3 + 100*0.2 + 100*0.1 = 100
        assert score == 100

    def test_calculate_qualification_score_beginner(self):
        """Test qualification score calculation for beginner company."""
        opp = Opportunity(
            company_name="Test",
            icp_score=20,
            ai_maturity=MaturityLevel.BEGINNER,
            security_maturity=MaturityLevel.BEGINNER,
            design_partner_potential=10,
        )
        score = opp.calculate_qualification_score()
        # 20*0.4 + 40*0.3 + 40*0.2 + 10*0.1 = 8 + 12 + 8 + 1 = 29
        assert score == 29

    def test_is_qualified_for_design_partner_true(self):
        """Test design partner qualification check passes."""
        opp = Opportunity(
            company_name="Test",
            icp_score=70,
            icp_alignment=ICPAlignment.STRONG,
            ai_maturity=MaturityLevel.INTERMEDIATE,
            security_maturity=MaturityLevel.INTERMEDIATE,
            design_partner_potential=70,
            has_product_team=True,
        )
        assert opp.is_qualified_for_design_partner() is True

    def test_is_qualified_for_design_partner_false_low_score(self):
        """Test design partner qualification fails for low score."""
        opp = Opportunity(
            company_name="Test",
            icp_score=20,
            icp_alignment=ICPAlignment.STRONG,
            has_product_team=True,
        )
        assert opp.is_qualified_for_design_partner() is False

    def test_is_qualified_for_design_partner_false_weak_alignment(self):
        """Test design partner qualification fails for weak alignment."""
        opp = Opportunity(
            company_name="Test",
            icp_score=80,
            icp_alignment=ICPAlignment.WEAK,
            has_product_team=True,
        )
        assert opp.is_qualified_for_design_partner() is False

    def test_is_qualified_for_design_partner_false_no_product_team(self):
        """Test design partner qualification fails without product team."""
        opp = Opportunity(
            company_name="Test",
            icp_score=80,
            icp_alignment=ICPAlignment.STRONG,
            has_product_team=False,
        )
        assert opp.is_qualified_for_design_partner() is False

    def test_serialization_roundtrip(self):
        """Test to_dict / from_dict roundtrip."""
        opp1 = Opportunity(
            company_name="Test Corp",
            company_size_employees=250,
            ai_maturity=MaturityLevel.INTERMEDIATE,
            icp_score=75,
        )
        data = opp1.to_dict()
        opp2 = Opportunity.from_dict(data)
        assert opp1.id == opp2.id
        assert opp1.company_name == opp2.company_name
        assert opp1.company_size_employees == opp2.company_size_employees
        assert opp1.ai_maturity == opp2.ai_maturity


class TestDesignPartner:
    """Tests for DesignPartner domain model."""

    def test_instantiate_defaults(self):
        """Test creating design partner with defaults."""
        dp = DesignPartner()
        assert dp.id is not None
        assert dp.onboarding_status == DesignPartnerStatus.ONBOARDING
        assert dp.health == PartnerHealth.GOOD

    def test_mark_onboarding_complete(self):
        """Test marking onboarding as complete."""
        dp = DesignPartner(company_name="Test")
        assert dp.onboarding_status == DesignPartnerStatus.ONBOARDING
        assert dp.onboarding_completed_at is None

        dp.mark_onboarding_complete()
        assert dp.onboarding_status == DesignPartnerStatus.ACTIVE
        assert dp.onboarding_completed_at is not None

    def test_update_engagement(self):
        """Test updating engagement metrics."""
        dp = DesignPartner(company_name="Test")
        assert dp.total_feedback_count == 0
        assert dp.feedback_count_this_quarter == 0

        dp.update_engagement(feedback_count=5)
        assert dp.total_feedback_count == 5
        assert dp.feedback_count_this_quarter == 5
        assert dp.last_engagement_at is not None

    def test_validate_success(self):
        """Test validation passes for valid design partner."""
        dp = DesignPartner(
            company_name="Test Corp",
            product_owner_email="owner@test.com",
        )
        errors = dp.validate()
        assert len(errors) == 0

    def test_validate_missing_company_name(self):
        """Test validation fails for missing company name."""
        dp = DesignPartner(company_name="")
        errors = dp.validate()
        assert any("company_name" in e for e in errors)

    def test_validate_missing_email(self):
        """Test validation fails for missing email."""
        dp = DesignPartner(company_name="Test", product_owner_email="")
        errors = dp.validate()
        assert any("product_owner_email" in e for e in errors)

    def test_validate_negative_feedback_count(self):
        """Test validation fails for negative feedback count."""
        dp = DesignPartner(
            company_name="Test",
            product_owner_email="owner@test.com",
            total_feedback_count=-5,
        )
        errors = dp.validate()
        assert any("total_feedback_count" in e for e in errors)


class TestDesignFeedback:
    """Tests for DesignFeedback domain model."""

    def test_instantiate_defaults(self):
        """Test creating feedback with defaults."""
        fb = DesignFeedback()
        assert fb.id is not None
        assert fb.category == FeedbackCategory.OTHER
        assert fb.status == FeedbackStatus.SUBMITTED

    def test_validate_success(self):
        """Test validation passes for valid feedback."""
        fb = DesignFeedback(
            customer_name="John Doe",
            description="Feature request",
            impact_score=50,
        )
        errors = fb.validate()
        assert len(errors) == 0

    def test_validate_missing_customer_name(self):
        """Test validation fails for missing customer name."""
        fb = DesignFeedback(customer_name="")
        errors = fb.validate()
        assert any("customer_name" in e for e in errors)

    def test_validate_missing_description(self):
        """Test validation fails for missing description."""
        fb = DesignFeedback(customer_name="John", description="")
        errors = fb.validate()
        assert any("description" in e for e in errors)

    def test_validate_invalid_impact_score(self):
        """Test validation fails for invalid impact score."""
        fb = DesignFeedback(
            customer_name="John",
            description="Test",
            impact_score=150,
        )
        errors = fb.validate()
        assert any("impact_score" in e for e in errors)

    def test_validate_invalid_confidence(self):
        """Test validation fails for invalid confidence."""
        fb = DesignFeedback(
            customer_name="John",
            description="Test",
            confidence=1.5,
        )
        errors = fb.validate()
        assert any("confidence" in e for e in errors)


class TestProductRecommendation:
    """Tests for ProductRecommendation domain model."""

    def test_calculate_business_score_high(self):
        """Test business score calculation for high-value feature."""
        rec = ProductRecommendation(
            title="Dark Mode",
            requesting_customer_count=15,  # 15 * 5 * 0.4 = 30
            aggregate_priority_score=90,  # 90 * 0.3 = 27
            estimated_effort="small",  # 100 * 0.2 = 20
            aggregate_impact_score=85,  # 85 * 0.1 = 8.5
        )
        score = rec.calculate_business_score()
        # 30 + 27 + 20 + 8.5 = 85.5 → 85
        assert score >= 80

    def test_calculate_business_score_low(self):
        """Test business score calculation for low-value feature."""
        rec = ProductRecommendation(
            title="Obscure Feature",
            requesting_customer_count=1,
            aggregate_priority_score=20,
            estimated_effort="xlarge",
            aggregate_impact_score=15,
        )
        score = rec.calculate_business_score()
        assert score < 30

    def test_make_decision(self):
        """Test recording a decision on recommendation."""
        rec = ProductRecommendation(title="Test")
        decision_by = uuid4()

        assert rec.decision_made is False
        rec.make_decision(decision_by=decision_by, notes="Approved for Q3")
        assert rec.decision_made is True
        assert rec.decision_made_by == decision_by
        assert rec.decision_notes == "Approved for Q3"
        assert rec.decision_made_at is not None

    def test_validate_success(self):
        """Test validation passes for valid recommendation."""
        rec = ProductRecommendation(
            title="New Feature",
            aggregate_impact_score=50,
            aggregate_priority_score=60,
            requesting_customer_count=5,
        )
        errors = rec.validate()
        assert len(errors) == 0

    def test_validate_missing_title(self):
        """Test validation fails for missing title."""
        rec = ProductRecommendation(title="")
        errors = rec.validate()
        assert any("title" in e for e in errors)

    def test_validate_invalid_scores(self):
        """Test validation fails for invalid scores."""
        rec = ProductRecommendation(
            title="Test",
            aggregate_impact_score=150,
            confidence=1.5,
        )
        errors = rec.validate()
        assert any("aggregate_impact_score" in e for e in errors)
        assert any("confidence" in e for e in errors)


class TestSecurityAuditRecord:
    """Tests for SecurityAuditRecord domain model."""

    def test_instantiate(self):
        """Test creating audit record."""
        actor_id = uuid4()
        rec = SecurityAuditRecord(
            actor_id=actor_id,
            actor_role="admin",
            action=AuditAction.POLICY_EVALUATED,
            resource_type="opportunity",
        )
        assert rec.actor_id == actor_id
        assert rec.action == AuditAction.POLICY_EVALUATED

    def test_validate_success(self):
        """Test validation passes."""
        rec = SecurityAuditRecord(
            action=AuditAction.CREATED,
            resource_type="feedback",
        )
        errors = rec.validate()
        assert len(errors) == 0

    def test_validate_missing_resource_type(self):
        """Test validation fails for missing resource type."""
        rec = SecurityAuditRecord(
            action=AuditAction.CREATED,
            resource_type="",
        )
        errors = rec.validate()
        assert any("resource_type" in e for e in errors)


class TestPolicyDecision:
    """Tests for PolicyDecision domain model."""

    def test_calculate_priority(self):
        """Test priority calculation."""
        pd = PolicyDecision(
            title="GDPR Compliance",
            impact_score=100,
            urgency_score=80,
            effort_score=50,
        )
        priority = pd.calculate_priority()
        # (100*0.5) + (80*0.4) + ((1-0.5)*0.1*100) = 50 + 32 + 5 = 87
        assert priority == 87

    def test_validate_success(self):
        """Test validation passes."""
        pd = PolicyDecision(
            title="Legal Review",
            impact_score=50,
            urgency_score=60,
        )
        errors = pd.validate()
        assert len(errors) == 0

    def test_validate_missing_title(self):
        """Test validation fails for missing title."""
        pd = PolicyDecision(title="")
        errors = pd.validate()
        assert any("title" in e for e in errors)

    def test_validate_invalid_confidence(self):
        """Test validation fails for invalid confidence."""
        pd = PolicyDecision(
            title="Test",
            confidence=1.5,
        )
        errors = pd.validate()
        assert any("confidence" in e for e in errors)


class TestFeedbackCluster:
    """Tests for FeedbackCluster domain model."""

    def test_add_related(self):
        """Test adding related feedback."""
        cluster = FeedbackCluster()
        fb1 = uuid4()
        fb2 = uuid4()

        cluster.add_related(fb1)
        cluster.add_related(fb2)

        assert fb1 in cluster.related_feedback_ids
        assert fb2 in cluster.related_feedback_ids
        assert len(cluster.related_feedback_ids) == 2

    def test_add_related_no_duplicates(self):
        """Test adding same feedback twice."""
        cluster = FeedbackCluster()
        fb = uuid4()

        cluster.add_related(fb)
        cluster.add_related(fb)

        assert cluster.related_feedback_ids.count(fb) == 1

    def test_calculate_aggregate_impact(self):
        """Test aggregate impact calculation."""
        cluster = FeedbackCluster()
        scores = [80, 90, 70]
        avg = cluster.calculate_aggregate_impact(scores)
        assert avg == 80  # (80 + 90 + 70) / 3

    def test_calculate_aggregate_impact_empty(self):
        """Test aggregate impact with empty list."""
        cluster = FeedbackCluster()
        avg = cluster.calculate_aggregate_impact([])
        assert avg == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
