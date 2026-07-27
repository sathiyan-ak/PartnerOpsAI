"""Application layer: ClusterFeedbackUseCase tests."""

import pytest
from uuid import uuid4, UUID
from datetime import datetime

from backend.domain import FeedbackCategory, FeedbackStatus, DesignPartner, DesignPartnerStatus
from backend.application.cluster_feedback import (
    ClusterFeedbackUseCase,
    ClusterFeedbackInput,
)
from backend.domain.feedback import DesignFeedback
from backend.infrastructure.repositories.design_partner_repository import DesignPartnerRepositoryImpl
from backend.infrastructure.repositories.feedback_repository import DesignFeedbackRepositoryImpl
from backend.infrastructure.repositories.feedback_repository import FeedbackClusterRepositoryImpl
from backend.infrastructure.repositories.audit_repository import SecurityAuditRepositoryImpl


@pytest.mark.integration
class TestClusterFeedbackUseCase:
    """Test feedback clustering."""

    @pytest.fixture
    def partner_repo(self, database_url) -> DesignPartnerRepositoryImpl:
        return DesignPartnerRepositoryImpl(database_url)

    @pytest.fixture
    def feedback_repo(self, database_url) -> DesignFeedbackRepositoryImpl:
        return DesignFeedbackRepositoryImpl(database_url)

    @pytest.fixture
    def cluster_repo(self, database_url) -> FeedbackClusterRepositoryImpl:
        return FeedbackClusterRepositoryImpl(database_url)

    @pytest.fixture
    def audit_repo(self, database_url) -> SecurityAuditRepositoryImpl:
        return SecurityAuditRepositoryImpl(database_url)

    @pytest.fixture
    def use_case(self, feedback_repo, cluster_repo, audit_repo, test_user_id):
        return ClusterFeedbackUseCase(
            feedback_repository=feedback_repo,
            cluster_repository=cluster_repo,
            audit_repository=audit_repo,
            actor_id=UUID(test_user_id),
        )

    def test_cluster_feedback_happy_path(
        self, use_case, partner_repo, feedback_repo, cluster_repo, test_user_id, test_opportunity_id
    ):
        """Test: Cluster similar feedback items."""
        user_uuid = UUID(test_user_id)

        # 1. Create partner
        dp = DesignPartner(
            id=uuid4(),
            opportunity_id=test_opportunity_id,
            created_by=user_uuid,
            updated_by=user_uuid,
            converted_by=user_uuid,
            company_name="Cluster Test Co",
            converted_at=datetime.utcnow(),
            onboarding_status=DesignPartnerStatus.ONBOARDING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        dp_id = partner_repo.save(dp)

        # 2. Create feedback items
        primary_fb = DesignFeedback(
            id=uuid4(),
            design_partner_id=dp_id,
            created_by=user_uuid,
            updated_by=user_uuid,
            customer_name="Customer A",
            customer_email="a@example.com",
            customer_company="Co A",
            category=FeedbackCategory.FEATURE_REQUEST,
            title="Collaboration features",
            description="Need real-time editing",
            impact_score=85,
            priority_score=90,
            status=FeedbackStatus.SUBMITTED,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        primary_id = feedback_repo.save(primary_fb)

        related_ids = []
        for i in range(2):
            related_fb = DesignFeedback(
                id=uuid4(),
                design_partner_id=dp_id,
                created_by=user_uuid,
                updated_by=user_uuid,
                customer_name=f"Customer {i}",
                customer_email=f"customer{i}@example.com",
                customer_company=f"Co {i}",
                category=FeedbackCategory.FEATURE_REQUEST,
                title="Collaboration features",
                description=f"Need collaborative editing {i}",
                impact_score=80 + i,
                priority_score=85 + i,
                status=FeedbackStatus.SUBMITTED,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            related_ids.append(feedback_repo.save(related_fb))

        # 3. Cluster them
        input_data = ClusterFeedbackInput(
            primary_feedback_id=primary_id,
            related_feedback_ids=related_ids,
            cluster_reason="All requesting real-time collaboration",
            theme="Collaboration & Real-time Features",
        )

        output = use_case.execute(input_data)

        # 4. Verify output
        assert output.cluster_id is not None
        assert output.primary_feedback_id == primary_id
        assert output.related_count == 2

        # 5. Verify persisted
        cluster = cluster_repo.find_by_id(output.cluster_id)
        assert cluster is not None
        assert cluster.total_feedback_count == 3
        assert cluster.theme == "Collaboration & Real-time Features"

    def test_cluster_missing_primary_feedback_fails(self, use_case):
        """Test: Primary feedback not found → ValueError."""
        input_data = ClusterFeedbackInput(
            primary_feedback_id=uuid4(),  # Nonexistent
            related_feedback_ids=[uuid4()],
            cluster_reason="Test",
            theme="Test",
        )

        with pytest.raises(ValueError) as exc_info:
            use_case.execute(input_data)

        assert "not found" in str(exc_info.value)

    def test_cluster_with_no_related_feedback(
        self, use_case, partner_repo, feedback_repo, cluster_repo, test_user_id, test_opportunity_id
    ):
        """Test: Cluster with only primary feedback."""
        user_uuid = UUID(test_user_id)

        dp = DesignPartner(
            id=uuid4(),
            opportunity_id=test_opportunity_id,
            created_by=user_uuid,
            updated_by=user_uuid,
            converted_by=user_uuid,
            company_name="Single Feedback Co",
            converted_at=datetime.utcnow(),
            onboarding_status=DesignPartnerStatus.ONBOARDING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        dp_id = partner_repo.save(dp)

        primary_fb = DesignFeedback(
            id=uuid4(),
            design_partner_id=dp_id,
            created_by=user_uuid,
            updated_by=user_uuid,
            customer_name="Customer",
            customer_email="test@example.com",
            customer_company="Co",
            category=FeedbackCategory.FEATURE_REQUEST,
            title="Single feedback",
            description="Only one feedback item",
            impact_score=50,
            priority_score=50,
            status=FeedbackStatus.SUBMITTED,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        primary_id = feedback_repo.save(primary_fb)

        input_data = ClusterFeedbackInput(
            primary_feedback_id=primary_id,
            related_feedback_ids=[],
            cluster_reason="Single item",
            theme="Single feedback",
        )

        output = use_case.execute(input_data)

        # Verify cluster created with count=1
        cluster = cluster_repo.find_by_id(output.cluster_id)
        assert cluster.total_feedback_count == 1
