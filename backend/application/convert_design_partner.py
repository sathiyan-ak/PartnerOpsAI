"""Convert Qualified Opportunity to Design Partner use case."""

from dataclasses import dataclass
from uuid import UUID
from typing import Optional
from ..domain import Opportunity, DesignPartner, DesignPartnerStatus, OpportunityStatus
from .repositories import (
    OpportunityRepository,
    DesignPartnerRepository,
    SecurityAuditRepository,
)
from ..domain.audit import SecurityAuditRecord
from ..domain.enums import AuditAction


@dataclass
class ConvertDesignPartnerInput:
    """Input: opportunity to convert."""

    opportunity_id: UUID
    product_owner_name: str
    product_owner_email: str
    technical_contact_name: str
    technical_contact_email: str
    partnership_notes: str = ""
    success_criteria: str = ""


@dataclass
class ConvertDesignPartnerOutput:
    """Output: new design partner."""

    design_partner_id: UUID
    opportunity_id: UUID
    company_name: str


class ConvertDesignPartnerUseCase:
    """
    Convert a qualified opportunity into an active design partner.

    Precondition: Opportunity must be QUALIFIED status.
    """

    def __init__(
        self,
        opportunity_repository: OpportunityRepository,
        design_partner_repository: DesignPartnerRepository,
        audit_repository: SecurityAuditRepository,
        actor_id: UUID,
    ):
        self.opportunity_repo = opportunity_repository
        self.design_partner_repo = design_partner_repository
        self.audit_repo = audit_repository
        self.actor_id = actor_id

    def execute(
        self, input_data: ConvertDesignPartnerInput
    ) -> ConvertDesignPartnerOutput:
        """Execute conversion."""

        # 1. Load opportunity
        opp = self.opportunity_repo.find_by_id(input_data.opportunity_id)
        if not opp:
            raise ValueError(f"Opportunity {input_data.opportunity_id} not found")

        # 2. Verify it's qualified
        if opp.status != OpportunityStatus.QUALIFIED:
            raise ValueError(
                f"Opportunity status must be QUALIFIED, got {opp.status.value}"
            )

        # 3. Create design partner
        dp = DesignPartner(
            opportunity_id=opp.id,
            created_by=self.actor_id,
            updated_by=self.actor_id,
            converted_by=self.actor_id,
            company_name=opp.company_name,
            product_owner_name=input_data.product_owner_name,
            product_owner_email=input_data.product_owner_email,
            technical_contact_name=input_data.technical_contact_name,
            technical_contact_email=input_data.technical_contact_email,
            onboarding_status=DesignPartnerStatus.ONBOARDING,
            partnership_notes=input_data.partnership_notes,
            success_criteria=input_data.success_criteria,
        )

        # 4. Validate
        errors = dp.validate()
        if errors:
            raise ValueError(f"Design partner validation failed: {errors}")

        # 5. Update opportunity status
        opp.status = OpportunityStatus.CONVERTED
        opp.updated_by = self.actor_id

        # 6. Persist both
        opp_id = self.opportunity_repo.save(opp)
        dp_id = self.design_partner_repo.save(dp)

        # 7. Audit
        audit = SecurityAuditRecord(
            actor_id=self.actor_id,
            actor_role="partnership_manager",
            action=AuditAction.CREATED,
            resource_type="design_partner",
            resource_id=dp_id,
            context_data={"opportunity_id": str(opp_id)},
        )
        self.audit_repo.append(audit)

        return ConvertDesignPartnerOutput(
            design_partner_id=dp_id,
            opportunity_id=opp_id,
            company_name=opp.company_name,
        )
