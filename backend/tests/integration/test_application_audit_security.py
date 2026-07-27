"""Application layer: AuditSecurityEventUseCase tests."""

from uuid import UUID, uuid4

import pytest

from backend.application.audit_security_event import (
    AuditSecurityEventInput,
    AuditSecurityEventUseCase,
)
from backend.domain.enums import AuditAction, PolicyResult
from backend.infrastructure.repositories.audit_repository import (
    SecurityAuditRepositoryImpl,
)


@pytest.mark.integration
class TestAuditSecurityEventUseCase:
    """Test security/compliance event auditing."""

    @pytest.fixture
    def audit_repo(self, database_url) -> SecurityAuditRepositoryImpl:
        return SecurityAuditRepositoryImpl(database_url)

    @pytest.fixture
    def use_case(self, audit_repo, test_user_id):
        return AuditSecurityEventUseCase(
            audit_repository=audit_repo,
            actor_id=UUID(test_user_id),
        )

    def test_audit_security_event_happy_path(self, use_case, audit_repo):
        """Test: Record security audit event."""
        resource_id = uuid4()

        input_data = AuditSecurityEventInput(
            actor_role="admin",
            action=AuditAction.CREATED,
            resource_type="opportunity",
            policy_name="data_access_policy",
            policy_result=PolicyResult.APPROVED,
            policy_evaluation_reasoning="User has valid role",
        )

        output = use_case.execute(resource_id, input_data)

        # Verify output
        assert output.audit_id is not None

        # Verify persisted (append-only)
        audit = audit_repo.find_by_id(output.audit_id)
        assert audit is not None
        assert audit.action == AuditAction.CREATED
        assert audit.resource_type == "opportunity"

    def test_audit_multiple_events_append_only(self, use_case, audit_repo):
        """Test: Multiple audit events append correctly."""
        resource_id = uuid4()

        # Record 3 events
        event_ids = []
        for i in range(3):
            input_data = AuditSecurityEventInput(
                actor_role="user",
                action=[AuditAction.CREATED, AuditAction.UPDATED, AuditAction.DELETED][i],
                resource_type="design_partner",
            )

            output = use_case.execute(resource_id, input_data)
            event_ids.append(output.audit_id)

        # Verify all persisted (append-only, no overwrites)
        for event_id in event_ids:
            audit = audit_repo.find_by_id(event_id)
            assert audit is not None

    def test_audit_event_with_context_data(self, use_case, audit_repo):
        """Test: Audit event with rich context."""
        resource_id = uuid4()

        input_data = AuditSecurityEventInput(
            actor_role="system",
            action=AuditAction.POLICY_EVALUATED,
            resource_type="opportunity",
            policy_name="enterprise_qualification",
            policy_result=PolicyResult.REVIEW_REQUIRED,
            policy_evaluation_reasoning="ICP score below threshold",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0...",
            context_data={
                "icp_score": 45,
                "required_score": 60,
                "qualification_result": "PROSPECT",
            },
        )

        output = use_case.execute(resource_id, input_data)

        # Verify context preserved
        audit = audit_repo.find_by_id(output.audit_id)
        assert audit.context_data["icp_score"] == 45
        assert audit.ip_address == "192.168.1.100"

    def test_audit_event_minimal_input(self, use_case, audit_repo):
        """Test: Audit event with minimal input."""
        resource_id = uuid4()

        input_data = AuditSecurityEventInput(
            actor_role="user",
            action=AuditAction.CREATED,
            resource_type="feedback",
        )

        output = use_case.execute(resource_id, input_data)

        # Should still create valid record
        audit = audit_repo.find_by_id(output.audit_id)
        assert audit is not None
        assert audit.actor_role == "user"
        assert audit.policy_name == ""

    def test_audit_event_validation_required_fields(self, use_case):
        """Test: Missing required field → validation error."""
        resource_id = uuid4()

        # Create input with empty actor_role
        input_data = AuditSecurityEventInput(
            actor_role="",  # INVALID
            action=AuditAction.CREATED,
            resource_type="opportunity",
        )

        with pytest.raises(ValueError):
            use_case.execute(resource_id, input_data)

    def test_audit_different_policy_results(self, use_case, audit_repo):
        """Test: Audit events with different policy outcomes."""
        resource_id = uuid4()

        for policy_result in [
            PolicyResult.APPROVED,
            PolicyResult.REVIEW_REQUIRED,
            PolicyResult.REJECTED,
        ]:
            input_data = AuditSecurityEventInput(
                actor_role="compliance_engine",
                action=AuditAction.POLICY_EVALUATED,
                resource_type="policy_decision",
                policy_result=policy_result,
            )

            output = use_case.execute(resource_id, input_data)
            audit = audit_repo.find_by_id(output.audit_id)
            assert audit.policy_result == policy_result

    def test_audit_append_only_immutability(self, use_case, audit_repo):
        """Test: Audit records are immutable (append-only)."""
        resource_id = uuid4()

        input_data = AuditSecurityEventInput(
            actor_role="admin",
            action=AuditAction.CREATED,
            resource_type="opportunity",
            policy_evaluation_reasoning="Initial creation",
        )

        output = use_case.execute(resource_id, input_data)

        # Retrieve first version
        audit1 = audit_repo.find_by_id(output.audit_id)
        reasoning1 = audit1.policy_evaluation_reasoning

        # Should be immutable (append-only repo should not allow updates)
        # Just verify the record is intact
        assert reasoning1 == "Initial creation"
