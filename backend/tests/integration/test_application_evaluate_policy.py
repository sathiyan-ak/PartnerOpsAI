"""Application layer: EvaluatePolicyUseCase tests."""

from uuid import UUID, uuid4

import pytest

from backend.application.evaluate_policy import (
    EvaluatePolicyInput,
    EvaluatePolicyUseCase,
)
from backend.infrastructure.repositories.audit_repository import (
    SecurityAuditRepositoryImpl,
)
from backend.infrastructure.repositories.policy_repository import (
    PolicyDecisionRepositoryImpl,
)


@pytest.mark.integration
class TestEvaluatePolicyUseCase:
    """Test policy evaluation."""

    @pytest.fixture
    def policy_repo(self, database_url) -> PolicyDecisionRepositoryImpl:
        return PolicyDecisionRepositoryImpl(database_url)

    @pytest.fixture
    def audit_repo(self, database_url) -> SecurityAuditRepositoryImpl:
        return SecurityAuditRepositoryImpl(database_url)

    @pytest.fixture
    def use_case(self, policy_repo, audit_repo, test_user_id):
        return EvaluatePolicyUseCase(
            policy_repository=policy_repo,
            audit_repository=audit_repo,
            actor_id=UUID(test_user_id),
        )

    def test_evaluate_policy_happy_path(
        self, use_case, policy_repo, test_user_id, test_opportunity_id
    ):
        """Test: Evaluate compliance policy."""
        opportunity_id = test_opportunity_id

        input_data = EvaluatePolicyInput(
            title="GDPR Compliance",
            description="Evaluate GDPR compliance requirements",
            category="Compliance",
            impact_score=95,
            urgency_score=90,
            effort_score=60,
        )

        output = use_case.execute(opportunity_id, input_data)

        # Verify output
        assert output.policy_id is not None
        assert output.priority_score is not None
        assert output.priority_score > 0

        # Verify persisted
        policy = policy_repo.find_by_id(output.policy_id)
        assert policy is not None
        assert policy.title == "GDPR Compliance"
        assert policy.category == "Compliance"

    def test_evaluate_high_priority_policy(
        self, use_case, policy_repo, test_opportunity_id
    ):
        """Test: High impact policy gets high priority."""
        opportunity_id = test_opportunity_id

        input_data = EvaluatePolicyInput(
            title="Critical Security",
            description="Critical security issue",
            category="Security",
            impact_score=100,
            urgency_score=100,
            effort_score=30,
        )

        output = use_case.execute(opportunity_id, input_data)

        # Should have high priority
        policy = policy_repo.find_by_id(output.policy_id)
        assert policy.priority_score >= 80

    def test_evaluate_low_priority_policy(
        self, use_case, policy_repo, test_opportunity_id
    ):
        """Test: Low impact policy gets low priority."""
        opportunity_id = test_opportunity_id

        input_data = EvaluatePolicyInput(
            title="Minor Documentation",
            description="Minor documentation update",
            category="Documentation",
            impact_score=20,
            urgency_score=10,
            effort_score=5,
        )

        output = use_case.execute(opportunity_id, input_data)

        # Should have low priority
        policy = policy_repo.find_by_id(output.policy_id)
        assert policy.priority_score <= 40

    def test_evaluate_policy_validation_error_invalid_score(self, use_case):
        """Test: Invalid score > 100 → validation error."""
        opportunity_id = uuid4()

        input_data = EvaluatePolicyInput(
            title="Policy",
            description="Test",
            category="Category",
            impact_score=150,  # INVALID
            urgency_score=50,
            effort_score=50,
        )

        with pytest.raises(ValueError):
            use_case.execute(opportunity_id, input_data)

    def test_evaluate_policy_deterministic_scoring(
        self, use_case, policy_repo, test_opportunity_id
    ):
        """Test: Same inputs produce same priority score."""
        opportunity_id = test_opportunity_id

        input_data = EvaluatePolicyInput(
            title="Consistent Policy",
            description="Test",
            category="Category",
            impact_score=75,
            urgency_score=80,
            effort_score=50,
        )

        # Execute twice
        output1 = use_case.execute(opportunity_id, input_data)

        # Same opportunity, same scores (deterministic)
        output2 = use_case.execute(opportunity_id, input_data)

        policy1 = policy_repo.find_by_id(output1.policy_id)
        policy2 = policy_repo.find_by_id(output2.policy_id)

        # Same inputs → same priority
        assert policy1.priority_score == policy2.priority_score

    def test_evaluate_multiple_policies_same_opportunity(
        self, use_case, policy_repo, test_opportunity_id
    ):
        """Test: Multiple policies for one opportunity."""
        opportunity_id = test_opportunity_id

        for i in range(3):
            input_data = EvaluatePolicyInput(
                title=f"Policy {i}",
                description=f"Test policy {i}",
                category=["Compliance", "Security", "Data Protection"][i],
                impact_score=50 + (i * 20),
                urgency_score=50 + (i * 15),
                effort_score=40,
            )

            use_case.execute(opportunity_id, input_data)

        # Verify all persisted
        all_policies = policy_repo.find_by_opportunity_id(opportunity_id)
        assert len(all_policies) == 3
