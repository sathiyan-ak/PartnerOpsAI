"""Evaluate Governance Policy use case."""

from dataclasses import dataclass
from uuid import UUID
from ..domain import PolicyDecision
from .repositories import PolicyDecisionRepository, SecurityAuditRepository
from ..domain.audit import SecurityAuditRecord
from ..domain.enums import AuditAction


@dataclass
class EvaluatePolicyInput:
    title: str
    description: str
    category: str
    impact_score: int
    urgency_score: int
    effort_score: int


@dataclass
class EvaluatePolicyOutput:
    policy_id: UUID
    priority_score: int


class EvaluatePolicyUseCase:
    """Evaluate governance/compliance policy for an opportunity."""

    def __init__(
        self,
        policy_repository: PolicyDecisionRepository,
        audit_repository: SecurityAuditRepository,
        actor_id: UUID,
    ):
        self.policy_repo = policy_repository
        self.audit_repo = audit_repository
        self.actor_id = actor_id

    def execute(
        self, opportunity_id: UUID, input_data: EvaluatePolicyInput
    ) -> EvaluatePolicyOutput:
        """Execute policy evaluation."""

        # Create policy
        policy = PolicyDecision(
            created_by=self.actor_id,
            updated_by=self.actor_id,
            opportunity_id=opportunity_id,
            title=input_data.title,
            description=input_data.description,
            category=input_data.category,
            impact_score=input_data.impact_score,
            urgency_score=input_data.urgency_score,
            effort_score=input_data.effort_score,
        )

        # Validate
        errors = policy.validate()
        if errors:
            raise ValueError(f"Policy validation failed: {errors}")

        # Calculate priority (deterministic)
        priority = policy.calculate_priority()
        policy.priority_score = priority

        # Persist
        policy_id = self.policy_repo.save(policy)

        # Audit
        audit = SecurityAuditRecord(
            actor_id=self.actor_id,
            actor_role="compliance_engine",
            action=AuditAction.POLICY_EVALUATED,
            resource_type="policy_decision",
            resource_id=policy_id,
            context_data={"priority_score": priority},
        )
        self.audit_repo.append(audit)

        return EvaluatePolicyOutput(policy_id=policy_id, priority_score=priority)
