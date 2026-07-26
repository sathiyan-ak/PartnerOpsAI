"""
Unit tests for PartnerOpsAI domain models.

Tests:
- Model instantiation
- Validation logic
- Serialization (to_dict / from_dict)
- Deterministic helper methods
- Enum usage
"""

import pytest
from datetime import datetime
from uuid import uuid4
from models import (
    Opportunity, OpportunityStatus, RiskLevel,
    DesignFeedback, FeedbackCategory, FeedbackStatus, ReleaseTarget,
    PolicyDecision, PolicyDecisionStatus,
    ActivityLogEntry,
    FeedbackCluster,
)


class TestOpportunity:
    """Tests for Opportunity domain model."""

    def test_instantiate_with_defaults(self):
        """Test creating an opportunity with default values."""
        opp = Opportunity()
        assert opp.id is not None
        assert opp.owner_id is not None
        assert opp.company_name == ""
        assert opp.deal_size_usd == 0
        assert opp.status == OpportunityStatus.PROSPECTING
        assert opp.overall_risk_level == RiskLevel.GREEN

    def test_instantiate_with_values(self):
        """Test creating an opportunity with specific values."""
        owner_id = uuid4()
        opp = Opportunity(
            company_name="Acme Corp",
            deal_size_usd=500000,
            status=OpportunityStatus.QUALIFIED,
            legal_risk_score=60,
            funding_risk_score=40,
            momentum_score=70,
            owner_id=owner_id,
        )
        assert opp.company_name == "Acme Corp"
        assert opp.deal_size_usd == 500000
        assert opp.status == OpportunityStatus.QUALIFIED
        assert opp.owner_id == owner_id

    def test_validate_success(self):
        """Test validation passes for valid data."""
        opp = Opportunity(
            company_name="Test Corp",
            deal_size_usd=100000,
            legal_risk_score=50,
            funding_risk_score=30,
            momentum_score=40,
        )
        errors = opp.validate()
        assert len(errors) == 0

    def test_validate_missing_company_name(self):
        """Test validation fails for missing company name."""
        opp = Opportunity(company_name="")
        errors = opp.validate()
        assert any("company_name" in e for e in errors)

    def test_validate_invalid_deal_size(self):
        """Test validation fails for negative deal size."""
        opp = Opportunity(company_name="Test", deal_size_usd=-1000)
        errors = opp.validate()
        assert any("deal_size_usd" in e for e in errors)

    def test_validate_invalid_risk_scores(self):
        """Test validation fails for out-of-range risk scores."""
        opp = Opportunity(
            company_name="Test",
            legal_risk_score=150,  # > 100
        )
        errors = opp.validate()
        assert any("legal_risk_score" in e for e in errors)

    def test_calculate_overall_risk_green(self):
        """Test risk calculation returns GREEN for low scores."""
        opp = Opportunity(
            company_name="Test",
            legal_risk_score=30,
            funding_risk_score=40,
            momentum_score=20,
        )
        risk = opp.calculate_overall_risk()
        assert risk == RiskLevel.GREEN

    def test_calculate_overall_risk_yellow(self):
        """Test risk calculation returns YELLOW for medium scores."""
        opp = Opportunity(
            company_name="Test",
            legal_risk_score=60,
            funding_risk_score=40,
            momentum_score=20,
        )
        risk = opp.calculate_overall_risk()
        assert risk == RiskLevel.YELLOW

    def test_calculate_overall_risk_red(self):
        """Test risk calculation returns RED for high scores."""
        opp = Opportunity(
            company_name="Test",
            legal_risk_score=75,
            funding_risk_score=40,
            momentum_score=20,
        )
        risk = opp.calculate_overall_risk()
        assert risk == RiskLevel.RED

    def test_serialization_roundtrip(self):
        """Test to_dict / from_dict roundtrip preserves data."""
        opp1 = Opportunity(
            company_name="Test Corp",
            deal_size_usd=250000,
            legal_risk_score=50,
        )

        # Serialize
        data = opp1.to_dict()

        # Deserialize
        opp2 = Opportunity.from_dict(data)

        # Verify
        assert opp1.id == opp2.id
        assert opp1.company_name == opp2.company_name
        assert opp1.deal_size_usd == opp2.deal_size_usd
        assert opp1.legal_risk_score == opp2.legal_risk_score


class TestDesignFeedback:
    """Tests for DesignFeedback domain model."""

    def test_instantiate_with_defaults(self):
        """Test creating feedback with default values."""
        fb = DesignFeedback()
        assert fb.id is not None
        assert fb.category == FeedbackCategory.OTHER
        assert fb.status == FeedbackStatus.SUBMITTED
        assert fb.suggested_release == ReleaseTarget.BACKLOG

    def test_instantiate_with_values(self):
        """Test creating feedback with specific values."""
        fb = DesignFeedback(
            customer_name="John Doe",
            customer_company="Acme",
            category=FeedbackCategory.FEATURE_REQUEST,
            description="Add dark mode",
            impact_score=85,
        )
        assert fb.customer_name == "John Doe"
        assert fb.category == FeedbackCategory.FEATURE_REQUEST
        assert fb.impact_score == 85

    def test_validate_success(self):
        """Test validation passes for valid feedback."""
        fb = DesignFeedback(
            customer_name="John",
            description="Good feedback",
            impact_score=50,
            priority_score=60,
        )
        errors = fb.validate()
        assert len(errors) == 0

    def test_validate_missing_required_fields(self):
        """Test validation fails for missing required fields."""
        fb = DesignFeedback(customer_name="", description="")
        errors = fb.validate()
        assert any("customer_name" in e for e in errors)
        assert any("description" in e for e in errors)

    def test_validate_invalid_scores(self):
        """Test validation fails for out-of-range scores."""
        fb = DesignFeedback(
            customer_name="John",
            description="Test",
            impact_score=150,  # > 100
            confidence=1.5,  # > 1.0
        )
        errors = fb.validate()
        assert any("impact_score" in e for e in errors)
        assert any("confidence" in e for e in errors)

    def test_serialization_roundtrip(self):
        """Test to_dict / from_dict roundtrip."""
        fb1 = DesignFeedback(
            customer_name="Jane",
            customer_company="Beta Inc",
            category=FeedbackCategory.BUG,
            description="System crashes on login",
            impact_score=95,
            priority_score=90,
            confidence=0.85,
        )

        data = fb1.to_dict()
        fb2 = DesignFeedback.from_dict(data)

        assert fb1.id == fb2.id
        assert fb1.customer_name == fb2.customer_name
        assert fb1.category == fb2.category
        assert fb1.impact_score == fb2.impact_score


class TestPolicyDecision:
    """Tests for PolicyDecision domain model."""

    def test_instantiate_with_defaults(self):
        """Test creating policy decision with defaults."""
        pd = PolicyDecision()
        assert pd.id is not None
        assert pd.status == PolicyDecisionStatus.OPEN
        assert pd.priority_score == 0

    def test_instantiate_with_values(self):
        """Test creating policy decision with values."""
        pd = PolicyDecision(
            title="GDPR Compliance Review",
            description="Need to audit data handling",
            category="compliance",
            impact_score=90,
            urgency_score=80,
            effort_score=40,
        )
        assert pd.title == "GDPR Compliance Review"
        assert pd.category == "compliance"
        assert pd.impact_score == 90

    def test_validate_success(self):
        """Test validation passes for valid policy."""
        pd = PolicyDecision(
            title="Legal Review",
            impact_score=50,
            urgency_score=60,
            effort_score=30,
        )
        errors = pd.validate()
        assert len(errors) == 0

    def test_validate_missing_title(self):
        """Test validation fails for missing title."""
        pd = PolicyDecision(title="")
        errors = pd.validate()
        assert any("title" in e for e in errors)

    def test_calculate_priority(self):
        """Test deterministic priority calculation."""
        pd = PolicyDecision(
            title="Test",
            impact_score=100,
            urgency_score=80,
            effort_score=50,
        )
        # Formula: (impact * 0.5) + (urgency * 0.4) + (1 - effort/100) * 0.1
        # (100 * 0.5) + (80 * 0.4) + (1 - 0.5) * 0.1 * 100
        # 50 + 32 + 5 = 87
        priority = pd.calculate_priority()
        assert priority == 87

    def test_calculate_priority_bounds(self):
        """Test priority calculation stays within 0-100."""
        pd = PolicyDecision(
            title="Test",
            impact_score=100,
            urgency_score=100,
            effort_score=0,
        )
        priority = pd.calculate_priority()
        assert 0 <= priority <= 100

    def test_serialization_roundtrip(self):
        """Test to_dict / from_dict roundtrip."""
        pd1 = PolicyDecision(
            title="Security Audit",
            description="Need SOC 2 compliance",
            impact_score=85,
            urgency_score=70,
            effort_score=60,
            confidence=0.75,
        )

        data = pd1.to_dict()
        pd2 = PolicyDecision.from_dict(data)

        assert pd1.id == pd2.id
        assert pd1.title == pd2.title
        assert pd1.impact_score == pd2.impact_score


class TestActivityLogEntry:
    """Tests for ActivityLogEntry domain model."""

    def test_instantiate(self):
        """Test creating activity log entry."""
        user_id = uuid4()
        record_id = uuid4()
        entry = ActivityLogEntry(
            user_id=user_id,
            action="created",
            table_name="opportunities",
            record_id=record_id,
        )
        assert entry.user_id == user_id
        assert entry.action == "created"
        assert entry.table_name == "opportunities"

    def test_validate_success(self):
        """Test validation passes."""
        entry = ActivityLogEntry(
            action="updated",
            table_name="feedback",
        )
        errors = entry.validate()
        assert len(errors) == 0

    def test_validate_missing_action(self):
        """Test validation fails for missing action."""
        entry = ActivityLogEntry(action="", table_name="test")
        errors = entry.validate()
        assert any("action" in e for e in errors)

    def test_serialization(self):
        """Test to_dict serialization."""
        entry = ActivityLogEntry(
            action="deleted",
            table_name="opportunities",
        )
        data = entry.to_dict()
        assert data['action'] == "deleted"
        assert data['table_name'] == "opportunities"


class TestFeedbackCluster:
    """Tests for FeedbackCluster domain model."""

    def test_instantiate(self):
        """Test creating feedback cluster."""
        primary_id = uuid4()
        cluster = FeedbackCluster(
            primary_feedback_id=primary_id,
            cluster_reason="same keyword: 'dark mode'",
        )
        assert cluster.primary_feedback_id == primary_id
        assert cluster.cluster_reason == "same keyword: 'dark mode'"

    def test_add_related(self):
        """Test adding related feedback."""
        cluster = FeedbackCluster()
        fb_id1 = uuid4()
        fb_id2 = uuid4()

        cluster.add_related(fb_id1)
        cluster.add_related(fb_id2)

        assert fb_id1 in cluster.related_feedback_ids
        assert fb_id2 in cluster.related_feedback_ids
        assert len(cluster.related_feedback_ids) == 2

    def test_add_related_no_duplicates(self):
        """Test adding same feedback twice doesn't create duplicates."""
        cluster = FeedbackCluster()
        fb_id = uuid4()

        cluster.add_related(fb_id)
        cluster.add_related(fb_id)

        assert cluster.related_feedback_ids.count(fb_id) == 1


class TestEnums:
    """Tests for domain enums."""

    def test_opportunity_status_values(self):
        """Test OpportunityStatus enum values."""
        assert OpportunityStatus.PROSPECTING.value == "prospecting"
        assert OpportunityStatus.WON.value == "won"

    def test_feedback_category_values(self):
        """Test FeedbackCategory enum values."""
        assert FeedbackCategory.FEATURE_REQUEST.value == "feature_request"
        assert FeedbackCategory.BUG.value == "bug"

    def test_risk_level_values(self):
        """Test RiskLevel enum values."""
        assert RiskLevel.GREEN.value == "green"
        assert RiskLevel.RED.value == "red"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
