"""Security audit and governance domain models."""

from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from .enums import AuditAction, PolicyResult


@dataclass
class SecurityAuditRecord:
    """
    Immutable audit trail record for security & compliance tracking.

    Records every action that could affect security or compliance:
    - Policy evaluations
    - Data access
    - Configuration changes
    - Decision overrides
    """

    id: UUID = field(default_factory=uuid4)
    version: int = 0

    # Actor
    actor_id: UUID = field(default_factory=uuid4)
    actor_role: str = ""  # e.g., "admin", "product", "legal"

    # Action
    action: AuditAction = AuditAction.CREATED
    resource_type: str = ""  # e.g., "opportunity", "feedback", "recommendation"
    resource_id: UUID = field(default_factory=uuid4)  # ID of the affected resource

    # Policy evaluation (if applicable)
    policy_name: str = ""
    policy_version: int = 0
    policy_result: PolicyResult = PolicyResult.APPROVED
    policy_evaluation_reasoning: str = ""

    # Artifacts for verification
    request_id: str = ""  # Unique request identifier
    request_hash: str = ""  # Hash of request for integrity
    record_hash: str = ""  # Hash of this record for chain verification
    previous_hash: str = ""  # Hash of previous record (chain)

    # Context
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    context_data: Dict[str, Any] = field(default_factory=dict)  # Additional context

    # Timestamp (immutable)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def validate(self) -> list[str]:
        """Validate audit record data."""
        errors = []
        if not self.action:
            errors.append("action: required")
        if not self.resource_type.strip():
            errors.append("resource_type: required")
        return errors

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        data = asdict(self)
        data["id"] = str(self.id)
        data["actor_id"] = str(self.actor_id)
        data["resource_id"] = str(self.resource_id)
        data["action"] = self.action.value
        data["policy_result"] = self.policy_result.value
        data["created_at"] = self.created_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SecurityAuditRecord":
        """Deserialize from dictionary."""
        data = data.copy()
        data["id"] = UUID(data["id"]) if isinstance(data["id"], str) else data["id"]
        data["actor_id"] = (
            UUID(data["actor_id"])
            if isinstance(data["actor_id"], str)
            else data["actor_id"]
        )
        data["resource_id"] = (
            UUID(data["resource_id"])
            if isinstance(data["resource_id"], str)
            else data["resource_id"]
        )
        data["action"] = (
            AuditAction(data["action"])
            if isinstance(data["action"], str)
            else data["action"]
        )
        data["policy_result"] = (
            PolicyResult(data["policy_result"])
            if isinstance(data["policy_result"], str)
            else data["policy_result"]
        )
        data["created_at"] = (
            datetime.fromisoformat(data["created_at"])
            if isinstance(data["created_at"], str)
            else data["created_at"]
        )
        return cls(**data)


@dataclass
class PolicyDecision:
    """
    Governance or compliance decision item.

    Represents a policy/legal/compliance issue that needs action.
    Tracked through lifecycle: OPEN → IN_REVIEW → RESOLVED.
    """

    id: UUID = field(default_factory=uuid4)
    opportunity_id: UUID = field(default_factory=uuid4)
    created_by: UUID = field(default_factory=uuid4)
    updated_by: UUID = field(default_factory=uuid4)
    version: int = 0

    # Content
    title: str = ""
    description: str = ""
    category: str = "governance"  # e.g., "legal", "compliance", "security", "risk"

    # Scoring (deterministic)
    impact_score: int = 0  # 0-100: how badly blocks the deal?
    urgency_score: int = 0  # 0-100: how soon must be resolved?
    effort_score: int = 0  # 0-100: how much work to resolve?
    priority_score: int = 0  # calculated
    confidence: float = 0.0  # 0.0-1.0

    # Reasoning
    reasoning: str = ""
    recommendation: str = ""

    # Status & ownership
    status: str = "open"  # open | in_review | resolved | deferred
    assigned_to_id: Optional[UUID] = None
    due_date: Optional[datetime] = None

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def validate(self) -> list[str]:
        """Validate policy decision data."""
        errors = []
        if not self.title.strip():
            errors.append("title: required")
        if not 0 <= self.impact_score <= 100:
            errors.append("impact_score: must be 0-100")
        if not 0 <= self.urgency_score <= 100:
            errors.append("urgency_score: must be 0-100")
        if not 0 <= self.effort_score <= 100:
            errors.append("effort_score: must be 0-100")
        if not 0.0 <= self.confidence <= 1.0:
            errors.append("confidence: must be 0.0-1.0")
        return errors

    def calculate_priority(self) -> int:
        """
        Deterministic: Calculate priority from component scores.

        Formula: (impact * 0.5) + (urgency * 0.4) + (1 - effort/100) * 0.1 * 100
        Result: 0-100 scale
        """
        effort_factor = 1.0 - (self.effort_score / 100.0)
        priority = (
            (self.impact_score * 0.5)
            + (self.urgency_score * 0.4)
            + (effort_factor * 0.1 * 100)
        )
        return int(min(100, max(0, priority)))

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        data = asdict(self)
        data["id"] = str(self.id)
        data["opportunity_id"] = str(self.opportunity_id)
        data["created_by"] = str(self.created_by)
        data["updated_by"] = str(self.updated_by)
        if data.get("assigned_to_id"):
            data["assigned_to_id"] = str(data["assigned_to_id"])
        if data.get("due_date"):
            data["due_date"] = data["due_date"].isoformat()
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PolicyDecision":
        """Deserialize from dictionary."""
        data = data.copy()
        data["id"] = UUID(data["id"]) if isinstance(data["id"], str) else data["id"]
        data["opportunity_id"] = (
            UUID(data["opportunity_id"])
            if isinstance(data["opportunity_id"], str)
            else data["opportunity_id"]
        )
        data["created_by"] = (
            UUID(data["created_by"])
            if isinstance(data["created_by"], str)
            else data["created_by"]
        )
        data["updated_by"] = (
            UUID(data["updated_by"])
            if isinstance(data["updated_by"], str)
            else data["updated_by"]
        )
        if data.get("assigned_to_id") and isinstance(data["assigned_to_id"], str):
            data["assigned_to_id"] = UUID(data["assigned_to_id"])
        if data.get("due_date") and isinstance(data["due_date"], str):
            data["due_date"] = datetime.fromisoformat(data["due_date"])
        data["created_at"] = (
            datetime.fromisoformat(data["created_at"])
            if isinstance(data["created_at"], str)
            else data["created_at"]
        )
        data["updated_at"] = (
            datetime.fromisoformat(data["updated_at"])
            if isinstance(data["updated_at"], str)
            else data["updated_at"]
        )
        return cls(**data)
