"""Policy Decision repository."""

from typing import Optional, List
from uuid import UUID
from backend.domain import PolicyDecision
from backend.application.repositories import PolicyDecisionRepository
from ..database import db
from ..mapper import DomainMapper


class PolicyDecisionRepositoryImpl(PolicyDecisionRepository):
    def save(self, policy: PolicyDecision) -> UUID:
        data = {
            "id": str(policy.id),
            "opportunity_id": str(policy.opportunity_id),
            "created_by": str(policy.created_by),
            "updated_by": str(policy.updated_by),
            "version": policy.version,
            "title": policy.title,
            "description": policy.description,
            "category": policy.category,
            "impact_score": policy.impact_score,
            "urgency_score": policy.urgency_score,
            "effort_score": policy.effort_score,
            "priority_score": policy.priority_score,
            "confidence": float(policy.confidence),
            "reasoning": policy.reasoning,
            "recommendation": policy.recommendation,
            "status": policy.status,
            "assigned_to_id": (
                str(policy.assigned_to_id) if policy.assigned_to_id else None
            ),
            "due_date": policy.due_date.isoformat() if policy.due_date else None,
        }
        if policy.version > 0:
            data["version"] = policy.version + 1
        response = db.get_table("policy_decisions").upsert(data).execute()
        if not response.data:
            raise RuntimeError(f"Failed to save policy {policy.id}")
        return UUID(response.data[0]["id"])

    def find_by_id(self, policy_id: UUID) -> Optional[PolicyDecision]:
        response = (
            db.get_table("policy_decisions")
            .select("*")
            .eq("id", str(policy_id))
            .execute()
        )
        return PolicyDecision.from_dict(response.data[0]) if response.data else None

    def find_by_opportunity_id(
        self, opportunity_id: UUID, limit: int = 100
    ) -> List[PolicyDecision]:
        response = (
            db.get_table("policy_decisions")
            .select("*")
            .eq("opportunity_id", str(opportunity_id))
            .limit(limit)
            .execute()
        )
        return [PolicyDecision.from_dict(row) for row in response.data]

    def find_open(self, limit: int = 100) -> List[PolicyDecision]:
        response = (
            db.get_table("policy_decisions")
            .select("*")
            .eq("status", "open")
            .limit(limit)
            .execute()
        )
        return [PolicyDecision.from_dict(row) for row in response.data]

    def list_all(self, limit: int = 100) -> List[PolicyDecision]:
        response = db.get_table("policy_decisions").select("*").limit(limit).execute()
        return [PolicyDecision.from_dict(row) for row in response.data]
