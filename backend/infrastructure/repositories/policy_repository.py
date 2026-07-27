"""Policy Decision repository (PostgreSQL)."""

from uuid import UUID

import psycopg2

from backend.application.repositories import PolicyDecisionRepository
from backend.domain import PolicyDecision


class PolicyDecisionRepositoryImpl(PolicyDecisionRepository):
    """PostgreSQL implementation of PolicyDecisionRepository."""

    def __init__(self, db_url: str = None):
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

    def save(self, policy: PolicyDecision) -> UUID:
        """Save or update policy."""
        conn = self._connect()
        cursor = conn.cursor()

        try:
            sql = """
                INSERT INTO policy_decisions (
                    id, opportunity_id, created_by, updated_by, version,
                    title, description, category,
                    impact_score, urgency_score, effort_score, priority_score,
                    confidence, reasoning, recommendation, status, assigned_to_id, due_date
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    updated_by=EXCLUDED.updated_by,
                    version=EXCLUDED.version + 1,
                    title=EXCLUDED.title,
                    description=EXCLUDED.description,
                    category=EXCLUDED.category,
                    impact_score=EXCLUDED.impact_score,
                    urgency_score=EXCLUDED.urgency_score,
                    effort_score=EXCLUDED.effort_score,
                    priority_score=EXCLUDED.priority_score,
                    confidence=EXCLUDED.confidence,
                    reasoning=EXCLUDED.reasoning,
                    recommendation=EXCLUDED.recommendation,
                    status=EXCLUDED.status,
                    assigned_to_id=EXCLUDED.assigned_to_id,
                    due_date=EXCLUDED.due_date
            """
            cursor.execute(
                sql,
                (
                    str(policy.id),
                    str(policy.opportunity_id),
                    str(policy.created_by),
                    str(policy.updated_by),
                    policy.version,
                    policy.title,
                    policy.description,
                    policy.category,
                    policy.impact_score,
                    policy.urgency_score,
                    policy.effort_score,
                    policy.priority_score,
                    float(policy.confidence),
                    policy.reasoning,
                    policy.recommendation,
                    policy.status,
                    str(policy.assigned_to_id) if policy.assigned_to_id else None,
                    policy.due_date.isoformat() if policy.due_date else None,
                ),
            )
            conn.commit()
            return policy.id
        except psycopg2.Error as e:
            conn.rollback()
            raise RuntimeError(
                f"Database constraint violation: {str(e).split(chr(10))[0]}"
            ) from e
        finally:
            cursor.close()
            conn.close()

    def find_by_id(self, policy_id: UUID) -> PolicyDecision | None:
        """Find policy by ID."""
        conn = self._connect()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT * FROM policy_decisions WHERE id = %s",
                (str(policy_id),),
            )
            row = cursor.fetchone()
            return self._row_to_policy(row) if row else None
        finally:
            cursor.close()
            conn.close()

    def find_by_opportunity_id(
        self, opportunity_id: UUID, limit: int = 100
    ) -> list[PolicyDecision]:
        """Find policies by opportunity ID."""
        conn = self._connect()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT * FROM policy_decisions WHERE opportunity_id = %s LIMIT %s",
                (str(opportunity_id), limit),
            )
            rows = cursor.fetchall()
            return [self._row_to_policy(row) for row in rows]
        finally:
            cursor.close()
            conn.close()

    def find_open(self, limit: int = 100) -> list[PolicyDecision]:
        """Find open policies."""
        conn = self._connect()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT * FROM policy_decisions WHERE status = 'open' LIMIT %s",
                (limit,),
            )
            rows = cursor.fetchall()
            return [self._row_to_policy(row) for row in rows]
        finally:
            cursor.close()
            conn.close()

    def list_all(self, limit: int = 100) -> list[PolicyDecision]:
        """List all policies."""
        conn = self._connect()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM policy_decisions LIMIT %s", (limit,))
            rows = cursor.fetchall()
            return [self._row_to_policy(row) for row in rows]
        finally:
            cursor.close()
            conn.close()

    def _row_to_policy(self, row) -> PolicyDecision:
        """Convert database row to PolicyDecision domain object."""
        from datetime import datetime

        policy = PolicyDecision(
            id=UUID(row[0]),
            opportunity_id=UUID(row[1]),
            created_by=UUID(row[2]),
            updated_by=UUID(row[3]),
            version=row[4],
            title=row[5],
            description=row[6],
            category=row[7],
            impact_score=row[8],
            urgency_score=row[9],
            effort_score=row[10],
            priority_score=row[11],
            confidence=row[12],
            reasoning=row[13],
            recommendation=row[14],
            status=row[15],
            assigned_to_id=UUID(row[16]) if row[16] else None,
            due_date=datetime.fromisoformat(row[17]) if row[17] else None,
            created_at=row[18],
            updated_at=row[19],
        )
        return policy
