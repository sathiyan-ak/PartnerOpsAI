"""Feedback repository implementations."""

from typing import Optional, List
from uuid import UUID
from backend.domain import DesignFeedback, FeedbackCluster
from backend.application.repositories import (
    DesignFeedbackRepository,
    FeedbackClusterRepository,
)
from ..database import db
from ..mapper import DomainMapper


class DesignFeedbackRepositoryImpl(DesignFeedbackRepository):
    def save(self, feedback: DesignFeedback) -> UUID:
        data = DomainMapper.design_feedback_to_db(feedback)
        if feedback.version > 0:
            data["version"] = feedback.version + 1
        response = db.get_table("design_feedback").upsert(data).execute()
        if not response.data:
            raise RuntimeError(f"Failed to save feedback {feedback.id}")
        return UUID(response.data[0]["id"])

    def find_by_id(self, feedback_id: UUID) -> Optional[DesignFeedback]:
        response = (
            db.get_table("design_feedback")
            .select("*")
            .eq("id", str(feedback_id))
            .execute()
        )
        return (
            DomainMapper.db_to_design_feedback(response.data[0])
            if response.data
            else None
        )

    def find_by_design_partner_id(
        self, design_partner_id: UUID, limit: int = 100
    ) -> List[DesignFeedback]:
        response = (
            db.get_table("design_feedback")
            .select("*")
            .eq("design_partner_id", str(design_partner_id))
            .limit(limit)
            .execute()
        )
        return [DomainMapper.db_to_design_feedback(row) for row in response.data]

    def list_all(self, limit: int = 100) -> List[DesignFeedback]:
        response = db.get_table("design_feedback").select("*").limit(limit).execute()
        return [DomainMapper.db_to_design_feedback(row) for row in response.data]


class FeedbackClusterRepositoryImpl(FeedbackClusterRepository):
    def save(self, cluster: FeedbackCluster) -> UUID:
        data = {
            "id": str(cluster.id),
            "created_by": str(cluster.created_by),
            "updated_by": str(cluster.updated_by),
            "version": cluster.version,
            "primary_feedback_id": str(cluster.primary_feedback_id),
            "related_feedback_ids": [str(fid) for fid in cluster.related_feedback_ids],
            "cluster_reason": cluster.cluster_reason,
            "theme": cluster.theme,
            "total_feedback_count": cluster.total_feedback_count,
            "average_impact_score": float(cluster.average_impact_score),
            "average_priority_score": float(cluster.average_priority_score),
        }
        response = db.get_table("feedback_clusters").upsert(data).execute()
        if not response.data:
            raise RuntimeError(f"Failed to save cluster {cluster.id}")
        return UUID(response.data[0]["id"])

    def find_by_id(self, cluster_id: UUID) -> Optional[FeedbackCluster]:
        response = (
            db.get_table("feedback_clusters")
            .select("*")
            .eq("id", str(cluster_id))
            .execute()
        )
        if not response.data:
            return None
        row = response.data[0]
        cluster = FeedbackCluster(
            id=UUID(row["id"]),
            primary_feedback_id=UUID(row["primary_feedback_id"]),
            cluster_reason=row["cluster_reason"],
            theme=row["theme"],
        )
        cluster.related_feedback_ids = [
            UUID(fid) for fid in row.get("related_feedback_ids", [])
        ]
        return cluster

    def find_by_primary_feedback_id(
        self, feedback_id: UUID
    ) -> Optional[FeedbackCluster]:
        response = (
            db.get_table("feedback_clusters")
            .select("*")
            .eq("primary_feedback_id", str(feedback_id))
            .limit(1)
            .execute()
        )
        if not response.data:
            return None
        return self.find_by_id(UUID(response.data[0]["id"]))

    def list_all(self, limit: int = 100) -> List[FeedbackCluster]:
        response = db.get_table("feedback_clusters").select("*").limit(limit).execute()
        return [
            self.find_by_id(UUID(row["id"]))
            for row in response.data
            if self.find_by_id(UUID(row["id"]))
        ]
