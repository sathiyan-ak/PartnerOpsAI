"""Audit Security Event use case."""

from dataclasses import dataclass
from uuid import UUID
from typing import Optional, Dict, Any
from ..domain.audit import SecurityAuditRecord
from ..domain.enums import AuditAction, PolicyResult
from .repositories import SecurityAuditRepository


@dataclass
class AuditSecurityEventInput:
    actor_role: str
    action: AuditAction
    resource_type: str
    policy_name: Optional[str] = None
    policy_result: Optional[PolicyResult] = None
    policy_evaluation_reasoning: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    context_data: Optional[Dict[str, Any]] = None


@dataclass
class AuditSecurityEventOutput:
    audit_id: UUID


class AuditSecurityEventUseCase:
    """Record security/compliance audit event."""

    def __init__(
        self,
        audit_repository: SecurityAuditRepository,
        actor_id: UUID,
    ):
        self.audit_repo = audit_repository
        self.actor_id = actor_id

    def execute(self, resource_id: UUID, input_data: AuditSecurityEventInput) -> AuditSecurityEventOutput:
        """Execute audit event recording."""

        # Create audit record
        record = SecurityAuditRecord(
            actor_id=self.actor_id,
            actor_role=input_data.actor_role,
            action=input_data.action,
            resource_type=input_data.resource_type,
            resource_id=resource_id,
            policy_name=input_data.policy_name or "",
            policy_result=input_data.policy_result or PolicyResult.APPROVED,
            policy_evaluation_reasoning=input_data.policy_evaluation_reasoning or "",
            ip_address=input_data.ip_address,
            user_agent=input_data.user_agent,
            context_data=input_data.context_data or {},
        )

        # Validate
        errors = record.validate()
        if errors:
            raise ValueError(f"Audit record validation failed: {errors}")

        # Persist (append-only)
        audit_id = self.audit_repo.append(record)

        return AuditSecurityEventOutput(audit_id=audit_id)
