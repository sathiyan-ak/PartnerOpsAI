"""Application layer: GenerateRecommendationUseCase tests."""

import pytest
from uuid import uuid4, UUID
from datetime import datetime

from backend.domain import (
    ReleaseTarget, FeedbackCluster, DesignFeedback, FeedbackCategory, FeedbackStatus
)
from backend.application.generate_recommendation import (
    GenerateRecommendationUseCase,
    GenerateRecommendationInput,
)
from backend.infrastructure.repositories.feedback_repository import (
    FeedbackClusterRepositoryImpl, DesignFeedbackRepositoryImpl
)
from backend.infrastructure.repositories.recommendation_repository import ProductRecommendationRepositoryImpl
from backend.infrastructure.repositories.audit_repository import SecurityAuditRepositoryImpl


@pytest.mark.integration
class TestGenerateRecommendationUseCase:
    """Test product recommendation generation."""

    @pytest.fixture
    def feedback_repo(self, database_url) -> DesignFeedbackRepositoryImpl:
        return DesignFeedbackRepositoryImpl(database_url)

    @pytest.fixture
    def cluster_repo(self, database_url) -> FeedbackClusterRepositoryImpl:
        return FeedbackClusterRepositoryImpl(database_url)

    @pytest.fixture
    def recommendation_repo(self, database_url) -> ProductRecommendationRepositoryImpl:
        return ProductRecommendationRepositoryImpl(database_url)

    @pytest.fixture
    def audit_repo(self, database_url) -> SecurityAuditRepositoryImpl:
        return SecurityAuditRepositoryImpl(database_url)

    @pytest.fixture
    def use_case(self, cluster_repo, recommendation_repo, audit_repo, test_user_id):
        return GenerateRecommendationUseCase(
            cluster_repository=cluster_repo,
            recommendation_repository=recommendation_repo,
            audit_repository=audit_repo,
            actor_id=UUID(test_user_id),
        )

    def test_generate_recommendation_happy_path(
        self, use_case, feedback_repo, cluster_repo, recommendation_repo, test_user_id, test_design_partner_id
    ):
        """Test: Generate recommendation from cluster."""
        user_uuid = UUID(test_user_id)

        # 1. Create feedback (required for FK constraint)
        primary_fb = DesignFeedback(
            id=uuid4(),
            design_partner_id=test_design_partner_id,
            created_by=user_uuid,
            updated_by=user_uuid,
            customer_name="Customer",
            customer_email="test@example.com",
            customer_company="Co",
            category=FeedbackCategory.FEATURE_REQUEST,
            title="Dashboard Customization",
            description="Need customizable dashboard",
            impact_score=82,
            priority_score=80,
            status=FeedbackStatus.SUBMITTED,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        primary_id = feedback_repo.save(primary_fb)

        # 2. Create cluster with real feedback IDs (FK constraint)
        cluster = FeedbackCluster(
            id=uuid4(),
            created_by=user_uuid,
            updated_by=user_uuid,
            primary_feedback_id=primary_id,
            related_feedback_ids=[uuid4(), uuid4()],
            cluster_reason="Multiple requests",
            theme="Dashboard Customization",
            total_feedback_count=3,
            average_impact_score=82.5,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        cluster_id = cluster_repo.save(cluster)

        # 2. Generate recommendation
        input_data = GenerateRecommendationInput(
            cluster_id=cluster_id,
            aggregate_impact_score=85,
            aggregate_priority_score=88,
            requesting_customer_count=3,
            total_feedback_items=5,
            business_justification="High-value customers demanding customization",
            market_opportunity="Competitive advantage in enterprise segment",
            revenue_impact_potential="$500K ARR from these customers alone",
            competitive_positioning="Competitors lack this feature",
            recommendation="BUILD",
            recommendation_reasoning="High demand + revenue impact",
            suggested_release=ReleaseTarget.NEXT_MINOR,
            release_reasoning="Can be built in 8 weeks",
            estimated_effort="large",
            affected_personas=["Enterprise Admin", "Power User"],
            dependencies=["Authentication refactor", "New DB schema"],
            risks=["Timeline risk", "Complexity risk"],
        )

        output = use_case.execute(input_data)

        # 3. Verify output
        assert output.recommendation_id is not None
        assert output.business_score is not None
        assert output.confidence is not None
        assert output.recommendation == "BUILD"

        # 4. Verify persisted
        rec = recommendation_repo.find_by_id(output.recommendation_id)
        assert rec is not None
        assert rec.title == "Dashboard Customization"
        assert rec.recommendation == "BUILD"

    def test_generate_recommendation_defer_decision(
        self, use_case, feedback_repo, cluster_repo, recommendation_repo, test_user_id, test_design_partner_id
    ):
        """Test: Generate DEFER recommendation."""
        user_uuid = UUID(test_user_id)

        # Create feedback first
        primary_fb = DesignFeedback(
            id=uuid4(),
            design_partner_id=test_design_partner_id,
            created_by=user_uuid,
            updated_by=user_uuid,
            customer_name="Customer",
            customer_email="test@example.com",
            customer_company="Co",
            category=FeedbackCategory.FEATURE_REQUEST,
            title="Advanced Analytics",
            description="Need advanced analytics",
            impact_score=35,
            priority_score=40,
            status=FeedbackStatus.SUBMITTED,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        primary_id = feedback_repo.save(primary_fb)

        cluster = FeedbackCluster(
            id=uuid4(),
            created_by=user_uuid,
            updated_by=user_uuid,
            primary_feedback_id=primary_id,
            related_feedback_ids=[uuid4()],
            cluster_reason="Niche request",
            theme="Advanced Analytics",
            total_feedback_count=2,
            average_impact_score=35.0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        cluster_id = cluster_repo.save(cluster)

        input_data = GenerateRecommendationInput(
            cluster_id=cluster_id,
            aggregate_impact_score=35,
            aggregate_priority_score=40,
            requesting_customer_count=1,
            total_feedback_items=2,
            business_justification="Niche feature requested by power users",
            market_opportunity="Limited market opportunity",
            revenue_impact_potential="Minimal",
            competitive_positioning="Not a differentiator",
            recommendation="DEFER",
            recommendation_reasoning="Revisit after raising Series B",
            suggested_release=ReleaseTarget.BACKLOG,
            release_reasoning="Defer to later roadmap",
            estimated_effort="large",
            affected_personas=["Power User"],
            dependencies=[],
            risks=[],
        )

        output = use_case.execute(input_data)

        # Verify recommendation is DEFER
        rec = recommendation_repo.find_by_id(output.recommendation_id)
        assert rec.recommendation == "DEFER"

    def test_generate_recommendation_missing_cluster_fails(self, use_case):
        """Test: Missing cluster → ValueError."""
        input_data = GenerateRecommendationInput(
            cluster_id=uuid4(),  # Nonexistent
            aggregate_impact_score=50,
            aggregate_priority_score=50,
            requesting_customer_count=1,
            total_feedback_items=1,
            business_justification="Test",
            market_opportunity="Test",
            revenue_impact_potential="Test",
            competitive_positioning="Test",
            recommendation="BUILD",
            recommendation_reasoning="Test",
            suggested_release=ReleaseTarget.NEXT_MINOR,
            release_reasoning="Test",
            estimated_effort="small",
            affected_personas=[],
            dependencies=[],
            risks=[],
        )

        with pytest.raises(ValueError) as exc_info:
            use_case.execute(input_data)

        assert "not found" in str(exc_info.value)

    def test_generate_recommendation_deterministic_scoring(
        self, use_case, feedback_repo, cluster_repo, recommendation_repo, test_user_id, test_design_partner_id
    ):
        """Test: Same inputs produce same scores."""
        user_uuid = UUID(test_user_id)

        # Create two identical clusters with real feedback
        for _ in range(2):
            primary_fb = DesignFeedback(
                id=uuid4(),
                design_partner_id=test_design_partner_id,
                created_by=user_uuid,
                updated_by=user_uuid,
                customer_name="Customer",
                customer_email="test@example.com",
                customer_company="Co",
                category=FeedbackCategory.FEATURE_REQUEST,
                title="Test Feature",
                description="Test",
                impact_score=75,
                priority_score=80,
                status=FeedbackStatus.SUBMITTED,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            primary_id = feedback_repo.save(primary_fb)

            cluster = FeedbackCluster(
                id=uuid4(),
                created_by=user_uuid,
                updated_by=user_uuid,
                primary_feedback_id=primary_id,
                related_feedback_ids=[uuid4()],
                cluster_reason="Test",
                theme="Test Feature",
                total_feedback_count=2,
                average_impact_score=75.0,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            cluster_id = cluster_repo.save(cluster)

            input_data = GenerateRecommendationInput(
                cluster_id=cluster_id,
                aggregate_impact_score=75,
                aggregate_priority_score=80,
                requesting_customer_count=2,
                total_feedback_items=3,
                business_justification="Medium priority",
                market_opportunity="Good market fit",
                revenue_impact_potential="$100K",
                competitive_positioning="Differentiator",
                recommendation="BUILD",
                recommendation_reasoning="Strong demand",
                suggested_release=ReleaseTarget.NEXT_MINOR,
                release_reasoning="6-week build",
                estimated_effort="medium",
                affected_personas=["User"],
                dependencies=[],
                risks=[],
            )

            use_case.execute(input_data)

        # Both should have identical scores due to deterministic calculation
        all_recs = recommendation_repo.list_all(limit=10)
        assert len(all_recs) >= 2
        # Check last 2 are same
        last_recs = all_recs[-2:]
        assert last_recs[0].confidence == last_recs[1].confidence
