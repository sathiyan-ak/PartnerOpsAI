"""Feedback repository implementations (PostgreSQL)."""

import json
from uuid import UUID

import psycopg2

from backend.application.repositories import (
    DesignFeedbackRepository,
    FeedbackClusterRepository,
)
from backend.domain import DesignFeedback, FeedbackCluster


class DesignFeedbackRepositoryImpl(DesignFeedbackRepository):
    """PostgreSQL implementation of DesignFeedbackRepository."""

    def __init__(self, db_url: str | None = None):
        """Initialize with database URL."""
        if db_url is None:
            import os

            db_url = os.getenv(
                "DATABASE_URL",
                "postgresql://test_user:test_password@localhost:5432/partneropsa_test",
            )
        self.db_url = db_url

    def _connect(self):
        """Get database connection."""
        return psycopg2.connect(self.db_url)

    def save(self, feedback: DesignFeedback) -> UUID:
        """Save or update feedback."""
        conn = self._connect()
        cursor = conn.cursor()

        try:
            sql = """
                INSERT INTO design_feedback (
                    id, design_partner_id, created_by, updated_by, version,
                    customer_name, customer_email, customer_company,
                    category, category_confidence, title, description,
                    impact_score, priority_score, confidence,
                    similar_feedback_ids, similarity_explanation,
                    suggested_release, release_reasoning,
                    product_decision_summary, decision_evidence, affected_personas,
                    status, created_at, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    updated_by=EXCLUDED.updated_by,
                    version=design_feedback.version + 1,
                    customer_name=EXCLUDED.customer_name,
                    customer_email=EXCLUDED.customer_email,
                    customer_company=EXCLUDED.customer_company,
                    category=EXCLUDED.category,
                    title=EXCLUDED.title,
                    description=EXCLUDED.description,
                    impact_score=EXCLUDED.impact_score,
                    priority_score=EXCLUDED.priority_score,
                    status=EXCLUDED.status,
                    updated_at=EXCLUDED.updated_at
            """
            cursor.execute(
                sql,
                (
                    str(feedback.id),
                    str(feedback.design_partner_id),
                    str(feedback.created_by),
                    str(feedback.updated_by),
                    feedback.version,
                    feedback.customer_name,
                    feedback.customer_email,
                    feedback.customer_company,
                    feedback.category.value,
                    float(feedback.category_confidence),
                    feedback.title,
                    feedback.description,
                    feedback.impact_score,
                    feedback.priority_score,
                    float(feedback.confidence),
                    [str(fid) for fid in feedback.similar_feedback_ids],
                    feedback.similarity_explanation,
                    feedback.suggested_release,
                    feedback.release_reasoning,
                    feedback.product_decision_summary,
                    feedback.decision_evidence,
                    feedback.affected_personas,
                    feedback.status.value,
                    feedback.created_at,
                    feedback.updated_at,
                ),
            )
            conn.commit()
            return feedback.id
        except psycopg2.Error as e:
            conn.rollback()
            raise RuntimeError(f"Database constraint violation: {str(e).split(chr(10))[0]}") from e
        finally:
            cursor.close()
            conn.close()

    def find_by_id(self, feedback_id: UUID) -> DesignFeedback | None:
        """Find feedback by ID."""
        conn = self._connect()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT * FROM design_feedback WHERE id = %s",
                (str(feedback_id),),
            )
            row = cursor.fetchone()
            return self._row_to_feedback(row) if row else None
        finally:
            cursor.close()
            conn.close()

    def find_by_design_partner_id(
        self, design_partner_id: UUID, limit: int = 100
    ) -> list[DesignFeedback]:
        """Find feedback by design partner ID."""
        conn = self._connect()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT * FROM design_feedback WHERE design_partner_id = %s LIMIT %s",
                (str(design_partner_id), limit),
            )
            rows = cursor.fetchall()
            return [self._row_to_feedback(row) for row in rows]
        finally:
            cursor.close()
            conn.close()

    def list_all(self, limit: int = 100) -> list[DesignFeedback]:
        """List all feedback items."""
        conn = self._connect()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM design_feedback LIMIT %s", (limit,))
            rows = cursor.fetchall()
            return [self._row_to_feedback(row) for row in rows]
        finally:
            cursor.close()
            conn.close()

    def _row_to_feedback(self, row) -> DesignFeedback:
        """Convert database row to DesignFeedback domain object."""
        from backend.domain.enums import FeedbackCategory, FeedbackStatus

        # Schema order: id(0), design_partner_id(1), created_by(2), updated_by(3), version(4),
        # customer_name(5), customer_email(6), customer_company(7),
        # category(8), category_confidence(9), title(10), description(11),
        # impact_score(12), priority_score(13), confidence(14),
        # similar_feedback_ids(15), similarity_explanation(16),
        # suggested_release(17), release_reasoning(18),
        # product_decision_summary(19), decision_evidence(20), affected_personas(21),
        # status(22), created_at(23), updated_at(24)

        # Handle similar_feedback_ids array
        similar_ids = (
            row[15] if isinstance(row[15], list) else (json.loads(row[15]) if row[15] else [])
        )
        similar_ids = [UUID(sid) if isinstance(sid, str) else sid for sid in similar_ids]

        # Handle affected_personas array
        affected = (
            row[21] if isinstance(row[21], list) else (json.loads(row[21]) if row[21] else [])
        )

        return DesignFeedback(
            id=UUID(row[0]),
            design_partner_id=UUID(row[1]),
            created_by=UUID(row[2]),
            updated_by=UUID(row[3]),
            version=row[4],
            customer_name=row[5],
            customer_email=row[6],
            customer_company=row[7],
            category=FeedbackCategory(row[8]),
            category_confidence=float(row[9]),
            title=row[10],
            description=row[11],
            impact_score=row[12],
            priority_score=row[13],
            confidence=float(row[14]),
            similar_feedback_ids=similar_ids,
            similarity_explanation=row[16],
            suggested_release=row[17],
            release_reasoning=row[18],
            product_decision_summary=row[19],
            decision_evidence=row[20],
            affected_personas=affected,
            status=FeedbackStatus(row[22]),
            created_at=row[23],
            updated_at=row[24],
        )


class FeedbackClusterRepositoryImpl(FeedbackClusterRepository):
    """PostgreSQL implementation of FeedbackClusterRepository."""

    def __init__(self, db_url: str | None = None):
        """Initialize with database URL."""
        if db_url is None:
            import os

            db_url = os.getenv(
                "DATABASE_URL",
                "postgresql://test_user:test_password@localhost:5432/partneropsa_test",
            )
        self.db_url = db_url

    def _connect(self):
        """Get database connection."""
        return psycopg2.connect(self.db_url)

    def save(self, cluster: FeedbackCluster) -> UUID:
        """Save or update cluster."""
        conn = self._connect()
        cursor = conn.cursor()

        try:
            sql = """
                INSERT INTO feedback_clusters (
                    id, created_by, updated_by, version,
                    primary_feedback_id, related_feedback_ids,
                    cluster_reason, theme,
                    total_feedback_count, average_impact_score, average_priority_score
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    updated_by=EXCLUDED.updated_by,
                    version=EXCLUDED.version + 1,
                    primary_feedback_id=EXCLUDED.primary_feedback_id,
                    related_feedback_ids=EXCLUDED.related_feedback_ids,
                    cluster_reason=EXCLUDED.cluster_reason,
                    theme=EXCLUDED.theme,
                    total_feedback_count=EXCLUDED.total_feedback_count,
                    average_impact_score=EXCLUDED.average_impact_score,
                    average_priority_score=EXCLUDED.average_priority_score
            """
            # Format UUID array as PostgreSQL array literal: {uuid1,uuid2}
            uuid_array_str = "{" + ",".join(str(fid) for fid in cluster.related_feedback_ids) + "}"
            cursor.execute(
                sql,
                (
                    str(cluster.id),
                    str(cluster.created_by),
                    str(cluster.updated_by),
                    cluster.version,
                    str(cluster.primary_feedback_id),
                    uuid_array_str,
                    cluster.cluster_reason,
                    cluster.theme,
                    cluster.total_feedback_count,
                    float(cluster.average_impact_score),
                    float(cluster.average_priority_score),
                ),
            )
            conn.commit()
            return cluster.id
        except psycopg2.Error as e:
            conn.rollback()
            raise RuntimeError(f"Database constraint violation: {str(e).split(chr(10))[0]}") from e
        finally:
            cursor.close()
            conn.close()

    def find_by_id(self, cluster_id: UUID) -> FeedbackCluster | None:
        """Find cluster by ID."""
        conn = self._connect()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT * FROM feedback_clusters WHERE id = %s",
                (str(cluster_id),),
            )
            row = cursor.fetchone()
            return self._row_to_cluster(row) if row else None
        finally:
            cursor.close()
            conn.close()

    def find_by_primary_feedback_id(self, feedback_id: UUID) -> FeedbackCluster | None:
        """Find cluster by primary feedback ID."""
        conn = self._connect()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT * FROM feedback_clusters WHERE primary_feedback_id = %s LIMIT 1",
                (str(feedback_id),),
            )
            row = cursor.fetchone()
            return self._row_to_cluster(row) if row else None
        finally:
            cursor.close()
            conn.close()

    def list_all(self, limit: int = 100) -> list[FeedbackCluster]:
        """List all clusters."""
        conn = self._connect()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM feedback_clusters LIMIT %s", (limit,))
            rows = cursor.fetchall()
            return [self._row_to_cluster(row) for row in rows]
        finally:
            cursor.close()
            conn.close()

    def _row_to_cluster(self, row) -> FeedbackCluster:
        """Convert database row to FeedbackCluster domain object."""
        # Handle array in different formats: Python list, JSON string, or PostgreSQL literal
        raw_ids = row[5]
        if isinstance(raw_ids, list):
            related_ids = raw_ids
        elif isinstance(raw_ids, str):
            if raw_ids.startswith("{"):
                # PostgreSQL array literal: {uuid1,uuid2}
                related_ids = [x.strip() for x in raw_ids.strip("{}").split(",") if x.strip()]
            else:
                # Try JSON
                related_ids = json.loads(raw_ids) if raw_ids else []
        else:
            related_ids = []
        related_ids = [UUID(fid) if isinstance(fid, str) else fid for fid in related_ids]

        return FeedbackCluster(
            id=UUID(row[0]),
            created_by=UUID(row[1]),
            updated_by=UUID(row[2]),
            version=row[3],
            primary_feedback_id=UUID(row[4]),
            related_feedback_ids=related_ids,
            cluster_reason=row[6],
            theme=row[7],
            total_feedback_count=row[8],
            average_impact_score=row[9],
            average_priority_score=row[10],
            created_at=row[11],
            updated_at=row[12],
        )
