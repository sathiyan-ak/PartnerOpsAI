"""Security Audit repository (append-only)."""

from typing import Optional, List
from uuid import UUID
from backend.domain import SecurityAuditRecord
from backend.application.repositories import SecurityAuditRepository
from ..database import db
from ..mapper import DomainMapper


class SecurityAuditRepositoryImpl(SecurityAuditRepository):
    def append(self, record: SecurityAuditRecord) -> UUID:
        """Append-only: insert only, never update."""
        data = DomainMapper.audit_to_db(record)
        response = db.get_table("security_audit_records").insert(data).execute()
        if not response.data:
            raise RuntimeError(f"Failed to append audit record {record.id}")
        return UUID(response.data[0]["id"])

    def find_by_id(self, record_id: UUID) -> Optional[SecurityAuditRecord]:
        response = db.get_table("security_audit_records").select("*").eq("id", str(record_id)).execute()
        return DomainMapper.db_to_audit(response.data[0]) if response.data else None

    def find_by_resource_id(self, resource_id: UUID, limit: int = 100) -> List[SecurityAuditRecord]:
        response = (
            db.get_table("security_audit_records")
            .select("*")
            .eq("resource_id", str(resource_id))
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return [DomainMapper.db_to_audit(row) for row in response.data]

    def find_by_actor_id(self, actor_id: UUID, limit: int = 100) -> List[SecurityAuditRecord]:
        response = (
            db.get_table("security_audit_records")
            .select("*")
            .eq("actor_id", str(actor_id))
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return [DomainMapper.db_to_audit(row) for row in response.data]

    def list_all(self, limit: int = 100) -> List[SecurityAuditRecord]:
        response = db.get_table("security_audit_records").select("*").order("created_at", desc=True).limit(limit).execute()
        return [DomainMapper.db_to_audit(row) for row in response.data]
