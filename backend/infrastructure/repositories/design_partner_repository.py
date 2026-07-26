"""Design Partner repository implementation."""

from typing import Optional, List
from uuid import UUID
from backend.domain import DesignPartner
from backend.application.repositories import DesignPartnerRepository
from ..database import db
from ..mapper import DomainMapper


class DesignPartnerRepositoryImpl(DesignPartnerRepository):
    """Supabase implementation of DesignPartnerRepository."""

    def save(self, design_partner: DesignPartner) -> UUID:
        data = DomainMapper.design_partner_to_db(design_partner)
        if design_partner.version > 0:
            data["version"] = design_partner.version + 1
        response = db.get_table("design_partners").upsert(data).execute()
        if not response.data:
            raise RuntimeError(f"Failed to save design partner {design_partner.id}")
        return UUID(response.data[0]["id"])

    def find_by_id(self, design_partner_id: UUID) -> Optional[DesignPartner]:
        response = (
            db.get_table("design_partners")
            .select("*")
            .eq("id", str(design_partner_id))
            .execute()
        )
        if not response.data:
            return None
        return DomainMapper.db_to_design_partner(response.data[0])

    def find_by_opportunity_id(self, opportunity_id: UUID) -> Optional[DesignPartner]:
        response = (
            db.get_table("design_partners")
            .select("*")
            .eq("opportunity_id", str(opportunity_id))
            .limit(1)
            .execute()
        )
        if not response.data:
            return None
        return DomainMapper.db_to_design_partner(response.data[0])

    def list_all(self, limit: int = 100) -> List[DesignPartner]:
        response = db.get_table("design_partners").select("*").limit(limit).execute()
        return [DomainMapper.db_to_design_partner(row) for row in response.data]
