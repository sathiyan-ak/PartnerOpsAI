"""Opportunity repository implementation (Supabase)."""

from typing import Optional, List
from uuid import UUID
from backend.domain import Opportunity
from backend.application.repositories import OpportunityRepository
from ..database import db
from ..mapper import DomainMapper


class OpportunityRepositoryImpl(OpportunityRepository):
    """Supabase implementation of OpportunityRepository."""

    def save(self, opportunity: Opportunity) -> UUID:
        """Save or update opportunity."""
        data = DomainMapper.opportunity_to_db(opportunity)

        # Increment version for updates
        if opportunity.version > 0:
            data["version"] = opportunity.version + 1

        response = db.get_table("opportunities").upsert(data).execute()

        if not response.data or len(response.data) == 0:
            raise RuntimeError(f"Failed to save opportunity {opportunity.id}")

        return UUID(response.data[0]["id"])

    def find_by_id(self, opportunity_id: UUID) -> Optional[Opportunity]:
        """Find opportunity by ID."""
        response = (
            db.get_table("opportunities")
            .select("*")
            .eq("id", str(opportunity_id))
            .execute()
        )

        if not response.data:
            return None

        return DomainMapper.db_to_opportunity(response.data[0])

    def find_by_company_name(self, company_name: str) -> Optional[Opportunity]:
        """Find opportunity by company name."""
        response = (
            db.get_table("opportunities")
            .select("*")
            .eq("company_name", company_name)
            .limit(1)
            .execute()
        )

        if not response.data:
            return None

        return DomainMapper.db_to_opportunity(response.data[0])

    def list_all(self, limit: int = 100) -> List[Opportunity]:
        """List all opportunities."""
        response = db.get_table("opportunities").select("*").limit(limit).execute()

        return [DomainMapper.db_to_opportunity(row) for row in response.data]
