"""Cluster Similar Feedback use case."""

from dataclasses import dataclass
from uuid import UUID

from ..domain import FeedbackCluster
from ..domain.audit import SecurityAuditRecord
from ..domain.enums import AuditAction
from .repositories import (
    DesignFeedbackRepository,
    FeedbackClusterRepository,
    SecurityAuditRepository,
)


@dataclass
class ClusterFeedbackInput:
    primary_feedback_id: UUID
    related_feedback_ids: list[UUID]
    cluster_reason: str
    theme: str = ""


@dataclass
class ClusterFeedbackOutput:
    cluster_id: UUID
    primary_feedback_id: UUID
    related_count: int


class ClusterFeedbackUseCase:
    """Group similar feedback into clusters for analysis."""

    def __init__(
        self,
        feedback_repository: DesignFeedbackRepository,
        cluster_repository: FeedbackClusterRepository,
        audit_repository: SecurityAuditRepository,
        actor_id: UUID,
    ):
        self.feedback_repo = feedback_repository
        self.cluster_repo = cluster_repository
        self.audit_repo = audit_repository
        self.actor_id = actor_id

    def execute(self, input_data: ClusterFeedbackInput) -> ClusterFeedbackOutput:
        """Execute clustering."""

        # Verify primary feedback exists
        primary = self.feedback_repo.find_by_id(input_data.primary_feedback_id)
        if not primary:
            raise ValueError(f"Primary feedback {input_data.primary_feedback_id} not found")

        # Create cluster
        cluster = FeedbackCluster(
            created_by=self.actor_id,
            updated_by=self.actor_id,
            primary_feedback_id=input_data.primary_feedback_id,
            related_feedback_ids=input_data.related_feedback_ids,
            cluster_reason=input_data.cluster_reason,
            theme=input_data.theme or primary.title,
        )

        # Calculate aggregates
        related_scores = [
            feedback.impact_score
            for fid in input_data.related_feedback_ids
            if (feedback := self.feedback_repo.find_by_id(fid))
        ]
        all_scores = [primary.impact_score] + related_scores
        cluster.total_feedback_count = len(all_scores)
        cluster.average_impact_score = sum(all_scores) / len(all_scores) if all_scores else 0

        # Persist
        cluster_id = self.cluster_repo.save(cluster)

        # Audit
        audit = SecurityAuditRecord(
            actor_id=self.actor_id,
            actor_role="feedback_engine",
            action=AuditAction.CREATED,
            resource_type="feedback_cluster",
            resource_id=cluster_id,
            context_data={"feedback_count": len(all_scores)},
        )
        self.audit_repo.append(audit)

        return ClusterFeedbackOutput(
            cluster_id=cluster_id,
            primary_feedback_id=input_data.primary_feedback_id,
            related_count=len(input_data.related_feedback_ids),
        )
