"""Security Audit repository (append-only)."""

import json
import psycopg2
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from backend.domain import SecurityAuditRecord
from backend.domain.enums import AuditAction, PolicyResult
from backend.application.repositories import SecurityAuditRepository


class SecurityAuditRepositoryImpl(SecurityAuditRepository):
    """PostgreSQL append-only audit repository."""

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

    def append(self, record: SecurityAuditRecord) -> UUID:
        """Append-only: insert only, never update."""
        conn = self._connect()
        cursor = conn.cursor()

        try:
            sql = """
                INSERT INTO security_audit_records (
                    id, version, actor_id, actor_role, action, resource_type, resource_id,
                    policy_name, policy_version, policy_result, policy_evaluation_reasoning,
                    request_id, request_hash, record_hash, previous_hash,
                    ip_address, user_agent, context_data, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            values = (
                str(record.id),
                record.version,
                str(record.actor_id),
                record.actor_role,
                record.action.value,
                record.resource_type,
                str(record.resource_id),
                record.policy_name,
                record.policy_version,
                record.policy_result.value if record.policy_result else None,
                record.policy_evaluation_reasoning,
                record.request_id,
                record.request_hash,
                record.record_hash,
                record.previous_hash,
                record.ip_address,
                record.user_agent,
                json.dumps(record.context_data) if record.context_data else "{}",
                datetime.utcnow(),
            )

            cursor.execute(sql, values)
            conn.commit()
            return record.id

        except psycopg2.Error as e:
            conn.rollback()
            raise RuntimeError(f"Failed to append audit record: {e}")
        finally:
            cursor.close()
            conn.close()

    def find_by_id(self, record_id: UUID) -> Optional[SecurityAuditRecord]:
        """Find audit record by ID."""
        conn = self._connect()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT * FROM security_audit_records WHERE id = %s", (str(record_id),)
            )
            row = cursor.fetchone()

            if not row:
                return None

            return self._row_to_audit(row, cursor.description)

        finally:
            cursor.close()
            conn.close()

    def find_by_resource_id(
        self, resource_id: UUID, limit: int = 100
    ) -> List[SecurityAuditRecord]:
        """Find audit records by resource ID."""
        conn = self._connect()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT * FROM security_audit_records WHERE resource_id = %s ORDER BY created_at DESC LIMIT %s",
                (str(resource_id), limit),
            )
            rows = cursor.fetchall()

            return [self._row_to_audit(row, cursor.description) for row in rows]

        finally:
            cursor.close()
            conn.close()

    def find_by_actor_id(
        self, actor_id: UUID, limit: int = 100
    ) -> List[SecurityAuditRecord]:
        """Find audit records by actor ID."""
        conn = self._connect()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT * FROM security_audit_records WHERE actor_id = %s ORDER BY created_at DESC LIMIT %s",
                (str(actor_id), limit),
            )
            rows = cursor.fetchall()

            return [self._row_to_audit(row, cursor.description) for row in rows]

        finally:
            cursor.close()
            conn.close()

    def list_all(self, limit: int = 100) -> List[SecurityAuditRecord]:
        """List all audit records."""
        conn = self._connect()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT * FROM security_audit_records ORDER BY created_at DESC LIMIT %s",
                (limit,),
            )
            rows = cursor.fetchall()

            return [self._row_to_audit(row, cursor.description) for row in rows]

        finally:
            cursor.close()
            conn.close()

    def _row_to_audit(self, row, description):
        """Convert database row to SecurityAuditRecord."""
        columns = {d[0]: i for i, d in enumerate(description)}

        return SecurityAuditRecord(
            id=UUID(row[columns["id"]]),
            version=row[columns["version"]],
            actor_id=UUID(row[columns["actor_id"]]),
            actor_role=row[columns["actor_role"]],
            action=AuditAction(row[columns["action"]]),
            resource_type=row[columns["resource_type"]],
            resource_id=UUID(row[columns["resource_id"]]),
            policy_name=row[columns["policy_name"]],
            policy_version=row[columns["policy_version"]],
            policy_result=PolicyResult(row[columns["policy_result"]])
            if row[columns["policy_result"]]
            else None,
            policy_evaluation_reasoning=row[columns["policy_evaluation_reasoning"]],
            request_id=row[columns["request_id"]],
            request_hash=row[columns["request_hash"]],
            record_hash=row[columns["record_hash"]],
            previous_hash=row[columns["previous_hash"]],
            ip_address=row[columns["ip_address"]],
            user_agent=row[columns["user_agent"]],
            context_data=json.loads(row[columns["context_data"]])
            if row[columns["context_data"]]
            else {},
            created_at=row[columns["created_at"]],
        )
