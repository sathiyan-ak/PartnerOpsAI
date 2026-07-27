"""Customer feedback and clustering models."""

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from .enums import FeedbackCategory, FeedbackStatus, ReleaseTarget


@dataclass
class DesignFeedback:
    """
    Customer feedback on product roadmap.

    Submitted by design partners (or prospects). Represents feature requests,
    bugs, enhancements, integrations that inform product decisions.
    """

    id: UUID = field(default_factory=uuid4)
    design_partner_id: UUID = field(default_factory=uuid4)
    created_by: UUID = field(default_factory=uuid4)
    updated_by: UUID = field(default_factory=uuid4)
    version: int = 0

    # Submitter info
    customer_name: str = ""
    customer_email: str = ""
    customer_company: str = ""

    # Feedback content
    category: FeedbackCategory = FeedbackCategory.OTHER
    category_confidence: float = 0.0  # 0.0-1.0 (LLM confidence)
    title: str = ""
    description: str = ""

    # Scoring (deterministic, not AI)
    impact_score: int = 0  # 0-100: how many customers want this?
    priority_score: int = 0  # 0-100: urgency + strategic value
    confidence: float = 0.0  # 0.0-1.0: how certain are we about the score?

    # AI-generated insights (with reasoning)
    similar_feedback_ids: list[UUID] = field(default_factory=list)
    similarity_explanation: str = ""  # Why are these similar?

    suggested_release: ReleaseTarget = ReleaseTarget.BACKLOG
    release_reasoning: str = ""  # Why this release timing?

    product_decision_summary: str = ""  # LLM-generated summary
    decision_evidence: str = ""  # Supporting facts

    affected_personas: list[str] = field(default_factory=list)  # Who benefits?

    # Status
    status: FeedbackStatus = FeedbackStatus.SUBMITTED

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def validate(self) -> list[str]:
        """Validate feedback data."""
        errors = []
        if not self.customer_name.strip():
            errors.append("customer_name: required")
        if not self.title.strip():
            errors.append("title: required")
        if not self.description.strip():
            errors.append("description: required")
        if not 0 <= self.impact_score <= 100:
            errors.append("impact_score: must be 0-100")
        if not 0 <= self.priority_score <= 100:
            errors.append("priority_score: must be 0-100")
        if not 0.0 <= self.confidence <= 1.0:
            errors.append("confidence: must be 0.0-1.0")
        if not 0.0 <= self.category_confidence <= 1.0:
            errors.append("category_confidence: must be 0.0-1.0")
        return errors

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        data = asdict(self)
        data["id"] = str(self.id)
        data["design_partner_id"] = str(self.design_partner_id)
        data["created_by"] = str(self.created_by)
        data["updated_by"] = str(self.updated_by)
        data["category"] = self.category.value
        data["suggested_release"] = self.suggested_release.value
        data["status"] = self.status.value
        data["similar_feedback_ids"] = [str(fid) for fid in self.similar_feedback_ids]
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DesignFeedback":
        """Deserialize from dictionary."""
        data = data.copy()
        data["id"] = UUID(data["id"]) if isinstance(data["id"], str) else data["id"]
        data["design_partner_id"] = (
            UUID(data["design_partner_id"])
            if isinstance(data["design_partner_id"], str)
            else data["design_partner_id"]
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
        data["category"] = (
            FeedbackCategory(data["category"])
            if isinstance(data["category"], str)
            else data["category"]
        )
        data["suggested_release"] = (
            ReleaseTarget(data["suggested_release"])
            if isinstance(data["suggested_release"], str)
            else data["suggested_release"]
        )
        data["status"] = (
            FeedbackStatus(data["status"])
            if isinstance(data["status"], str)
            else data["status"]
        )
        data["similar_feedback_ids"] = [
            UUID(fid) if isinstance(fid, str) else fid
            for fid in data.get("similar_feedback_ids", [])
        ]
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


@dataclass
class FeedbackCluster:
    """
    Groups similar feedback together for analysis and deduplication.

    Multiple feedback items with same theme get clustered into one
    aggregate view for product decision-making.
    """

    id: UUID = field(default_factory=uuid4)
    created_by: UUID = field(default_factory=uuid4)
    updated_by: UUID = field(default_factory=uuid4)
    version: int = 0

    primary_feedback_id: UUID = field(default_factory=uuid4)
    related_feedback_ids: list[UUID] = field(default_factory=list)

    cluster_reason: str = ""  # Why grouped? e.g., "same keyword", "same workflow"
    theme: str = ""  # High-level theme: "Dark Mode", "API Performance", etc.

    # Aggregates from related feedback
    total_feedback_count: int = 0
    average_impact_score: float = 0.0
    average_priority_score: float = 0.0
    unique_customers: int = 0

    merged_at: datetime | None = None

    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def add_related(self, feedback_id: UUID) -> None:
        """Add a related feedback to cluster."""
        if feedback_id not in self.related_feedback_ids:
            self.related_feedback_ids.append(feedback_id)

    def calculate_aggregate_impact(self, feedback_scores: list[int]) -> int:
        """Deterministic: Calculate aggregate impact from related feedback."""
        if not feedback_scores:
            return 0
        return int(sum(feedback_scores) / len(feedback_scores))

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        data = asdict(self)
        data["id"] = str(self.id)
        data["created_by"] = str(self.created_by)
        data["updated_by"] = str(self.updated_by)
        data["primary_feedback_id"] = str(self.primary_feedback_id)
        data["related_feedback_ids"] = [str(fid) for fid in self.related_feedback_ids]
        if data["merged_at"]:
            data["merged_at"] = data["merged_at"].isoformat()
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        return data
