"""Design partner domain model (bridge from Opportunity)."""

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from .enums import DesignPartnerStatus, PartnerHealth


@dataclass
class DesignPartner:
    """
    A qualified opportunity converted into an active design partner.

    Represents a customer actively providing feedback on our roadmap
    and helping us shape product direction.

    Converted from Opportunity when qualification_score >= 60 and
    other conditions met.
    """

    id: UUID = field(default_factory=uuid4)
    opportunity_id: UUID = field(default_factory=uuid4)
    created_by: UUID = field(default_factory=uuid4)
    updated_by: UUID = field(default_factory=uuid4)
    version: int = 0

    # Conversion info
    converted_at: datetime = field(default_factory=datetime.utcnow)
    converted_by: UUID = field(default_factory=uuid4)

    # Design partner info
    company_name: str = ""
    product_owner_name: str = ""
    product_owner_email: str = ""
    technical_contact_name: str = ""
    technical_contact_email: str = ""

    # Onboarding & implementation
    onboarding_status: DesignPartnerStatus = DesignPartnerStatus.ONBOARDING
    onboarding_started_at: datetime | None = None
    onboarding_completed_at: datetime | None = None

    implementation_status: DesignPartnerStatus = DesignPartnerStatus.ONBOARDING
    implementation_started_at: datetime | None = None
    implementation_completed_at: datetime | None = None

    # Health & engagement
    health: PartnerHealth = PartnerHealth.GOOD
    health_notes: str = ""
    last_engagement_at: datetime | None = None

    # Feedback engagement
    total_feedback_count: int = 0
    feedback_count_this_quarter: int = 0
    last_feedback_date: datetime | None = None

    # Product involvement
    features_influenced: list[str] = field(
        default_factory=list
    )  # Features this partner influenced
    roadmap_review_frequency: str = "monthly"  # monthly, quarterly, ad_hoc
    product_review_dates: list[datetime] = field(default_factory=list)

    # Context & notes
    partnership_notes: str = ""
    success_criteria: str = ""  # What defines success for this partnership?

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def validate(self) -> list[str]:
        """Validate design partner data."""
        errors = []
        if not self.company_name.strip():
            errors.append("company_name: required")
        if not self.product_owner_email.strip():
            errors.append("product_owner_email: required")
        if self.total_feedback_count < 0:
            errors.append("total_feedback_count: must be >= 0")
        if self.feedback_count_this_quarter < 0:
            errors.append("feedback_count_this_quarter: must be >= 0")
        return errors

    def update_engagement(self, feedback_count: int = 0) -> None:
        """Update engagement metrics."""
        if feedback_count > 0:
            self.total_feedback_count += feedback_count
            self.feedback_count_this_quarter += feedback_count
            self.last_engagement_at = datetime.utcnow()
            self.last_feedback_date = datetime.utcnow()
            self.updated_at = datetime.utcnow()

    def mark_onboarding_complete(self) -> None:
        """Mark onboarding phase as complete."""
        self.onboarding_status = DesignPartnerStatus.ACTIVE
        self.onboarding_completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def mark_implementation_complete(self) -> None:
        """Mark implementation phase as complete."""
        self.implementation_status = DesignPartnerStatus.SHIPPED
        self.implementation_completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        data = asdict(self)
        data["id"] = str(self.id)
        data["opportunity_id"] = str(self.opportunity_id)
        data["created_by"] = str(self.created_by)
        data["updated_by"] = str(self.updated_by)
        data["converted_by"] = str(self.converted_by)
        data["onboarding_status"] = self.onboarding_status.value
        data["implementation_status"] = self.implementation_status.value
        data["health"] = self.health.value
        data["converted_at"] = self.converted_at.isoformat()
        if data["onboarding_started_at"]:
            data["onboarding_started_at"] = data["onboarding_started_at"].isoformat()
        if data["onboarding_completed_at"]:
            data["onboarding_completed_at"] = data[
                "onboarding_completed_at"
            ].isoformat()
        if data["implementation_started_at"]:
            data["implementation_started_at"] = data[
                "implementation_started_at"
            ].isoformat()
        if data["implementation_completed_at"]:
            data["implementation_completed_at"] = data[
                "implementation_completed_at"
            ].isoformat()
        if data["last_engagement_at"]:
            data["last_engagement_at"] = data["last_engagement_at"].isoformat()
        if data["last_feedback_date"]:
            data["last_feedback_date"] = data["last_feedback_date"].isoformat()
        data["product_review_dates"] = [
            d.isoformat() for d in self.product_review_dates
        ]
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DesignPartner":
        """Deserialize from dictionary."""
        data = data.copy()
        data["id"] = UUID(data["id"]) if isinstance(data["id"], str) else data["id"]
        data["opportunity_id"] = (
            UUID(data["opportunity_id"])
            if isinstance(data["opportunity_id"], str)
            else data["opportunity_id"]
        )
        data["created_by"] = (
            UUID(data["created_by"])
            if isinstance(data["created_by"], str)
            else data["created_by"]
        )
        data["updated_by"] = (
            UUID(data["updated_by"])
            if isinstance(data["updated_by"], str)
            else data["updated_by"]
        )
        data["converted_by"] = (
            UUID(data["converted_by"])
            if isinstance(data["converted_by"], str)
            else data["converted_by"]
        )
        data["onboarding_status"] = (
            DesignPartnerStatus(data["onboarding_status"])
            if isinstance(data["onboarding_status"], str)
            else data["onboarding_status"]
        )
        data["implementation_status"] = (
            DesignPartnerStatus(data["implementation_status"])
            if isinstance(data["implementation_status"], str)
            else data["implementation_status"]
        )
        data["health"] = (
            PartnerHealth(data["health"])
            if isinstance(data["health"], str)
            else data["health"]
        )

        # Parse datetime fields
        for field_name in [
            "converted_at",
            "onboarding_started_at",
            "onboarding_completed_at",
            "implementation_started_at",
            "implementation_completed_at",
            "last_engagement_at",
            "last_feedback_date",
            "created_at",
            "updated_at",
        ]:
            if data.get(field_name) and isinstance(data[field_name], str):
                data[field_name] = datetime.fromisoformat(data[field_name])

        if data.get("product_review_dates"):
            data["product_review_dates"] = [
                datetime.fromisoformat(d) if isinstance(d, str) else d
                for d in data["product_review_dates"]
            ]

        return cls(**data)
