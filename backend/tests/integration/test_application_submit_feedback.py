"""Application layer: SubmitFeedbackUseCase tests."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from backend.application.submit_feedback import (
    SubmitFeedbackInput,
    SubmitFeedbackUseCase,
)
from backend.domain import (
    DesignPartner,
    DesignPartnerStatus,
    FeedbackCategory,
    FeedbackStatus,
)
from backend.infrastructure.repositories.audit_repository import (
    SecurityAuditRepositoryImpl,
)
from backend.infrastructure.repositories.design_partner_repository import (
    DesignPartnerRepositoryImpl,
)
from backend.infrastructure.repositories.feedback_repository import (
    DesignFeedbackRepositoryImpl,
)


@pytest.mark.integration
class TestSubmitFeedbackUseCase:
    """Test feedback submission from design partner."""

    @pytest.fixture
    def partner_repo(self, database_url) -> DesignPartnerRepositoryImpl:
        return DesignPartnerRepositoryImpl(database_url)

    @pytest.fixture
    def feedback_repo(self, database_url) -> DesignFeedbackRepositoryImpl:
        return DesignFeedbackRepositoryImpl(database_url)

    @pytest.fixture
    def audit_repo(self, database_url) -> SecurityAuditRepositoryImpl:
        return SecurityAuditRepositoryImpl(database_url)

    @pytest.fixture
    def use_case(self, feedback_repo, audit_repo, test_user_id):
        return SubmitFeedbackUseCase(
            feedback_repository=feedback_repo,
            audit_repository=audit_repo,
            actor_id=UUID(test_user_id),
        )

    def test_submit_feedback_happy_path(
        self, use_case, partner_repo, feedback_repo, test_user_id, test_opportunity_id
    ):
        """Test: Submit valid feedback → persisted."""
        user_uuid = UUID(test_user_id)

        # 1. Create design partner
        dp = DesignPartner(
            id=uuid4(),
            opportunity_id=test_opportunity_id,
            created_by=user_uuid,
            updated_by=user_uuid,
            converted_by=user_uuid,
            company_name="Feedback Customer",
            converted_at=datetime.now(UTC),
            onboarding_status=DesignPartnerStatus.ONBOARDING,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        dp_id = partner_repo.save(dp)

        # 2. Submit feedback
        input_data = SubmitFeedbackInput(
            customer_name="John Doe",
            customer_email="john@customer.com",
            customer_company="Feedback Co",
            category=FeedbackCategory.FEATURE_REQUEST,
            title="Real-time collaboration support needed",
            description="Multiple users should edit simultaneously",
            impact_score=85,
            priority_score=90,
        )

        output = use_case.execute(dp_id, input_data)

        # 3. Verify output
        assert output.feedback_id is not None
        assert output.status == FeedbackStatus.SUBMITTED.value

        # 4. Verify persisted
        fb = feedback_repo.find_by_id(output.feedback_id)
        assert fb is not None
        assert fb.title == "Real-time collaboration support needed"
        assert fb.impact_score == 85
        assert fb.priority_score == 90

    def test_submit_feedback_validation_error_missing_title(
        self, use_case, partner_repo, test_user_id, test_opportunity_id
    ):
        """Test: Empty title → validation error."""
        user_uuid = UUID(test_user_id)

        dp = DesignPartner(
            id=uuid4(),
            opportunity_id=test_opportunity_id,
            created_by=user_uuid,
            updated_by=user_uuid,
            converted_by=user_uuid,
            company_name="Test Co",
            converted_at=datetime.now(UTC),
            onboarding_status=DesignPartnerStatus.ONBOARDING,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        dp_id = partner_repo.save(dp)

        input_data = SubmitFeedbackInput(
            customer_name="Test",
            customer_email="test@example.com",
            customer_company="Test Co",
            category=FeedbackCategory.FEATURE_REQUEST,
            title="",  # INVALID
            description="Description",
            impact_score=50,
            priority_score=50,
        )

        with pytest.raises(ValueError) as exc_info:
            use_case.execute(dp_id, input_data)

        assert "validation failed" in str(exc_info.value).lower()

    def test_submit_feedback_invalid_scores(
        self, use_case, partner_repo, test_user_id, test_opportunity_id
    ):
        """Test: Score > 100 → validation error."""
        user_uuid = UUID(test_user_id)

        dp = DesignPartner(
            id=uuid4(),
            opportunity_id=test_opportunity_id,
            created_by=user_uuid,
            updated_by=user_uuid,
            converted_by=user_uuid,
            company_name="Test Co",
            converted_at=datetime.now(UTC),
            onboarding_status=DesignPartnerStatus.ONBOARDING,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        dp_id = partner_repo.save(dp)

        input_data = SubmitFeedbackInput(
            customer_name="Test",
            customer_email="test@example.com",
            customer_company="Test Co",
            category=FeedbackCategory.FEATURE_REQUEST,
            title="Valid Title",
            description="Description",
            impact_score=150,  # INVALID
            priority_score=50,
        )

        with pytest.raises(ValueError):
            use_case.execute(dp_id, input_data)

    def test_submit_multiple_feedback_same_partner(
        self, use_case, partner_repo, feedback_repo, test_user_id, test_opportunity_id
    ):
        """Test: Multiple feedback items from one partner."""
        user_uuid = UUID(test_user_id)

        dp = DesignPartner(
            id=uuid4(),
            opportunity_id=test_opportunity_id,
            created_by=user_uuid,
            updated_by=user_uuid,
            converted_by=user_uuid,
            company_name="Active Customer",
            onboarding_status=DesignPartnerStatus.ONBOARDING,
            converted_at=datetime.now(UTC),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        dp_id = partner_repo.save(dp)

        # Submit 2 feedback items
        for i in range(2):
            input_data = SubmitFeedbackInput(
                customer_name=f"Customer {i}",
                customer_email=f"customer{i}@company.com",
                customer_company="Active Customer",
                category=FeedbackCategory.FEATURE_REQUEST,
                title=f"Feature request {i}",
                description=f"Description {i}",
                impact_score=50 + (i * 10),
                priority_score=50 + (i * 10),
            )

            output = use_case.execute(dp_id, input_data)
            assert output.feedback_id is not None

        # Verify both persisted
        all_feedback = feedback_repo.find_by_design_partner_id(dp_id)
        assert len(all_feedback) == 2
