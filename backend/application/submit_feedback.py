"""Submit Design Feedback use case."""

from dataclasses import dataclass
from uuid import UUID

from ..domain import DesignFeedback, FeedbackCategory, FeedbackStatus
from ..domain.audit import SecurityAuditRecord
from ..domain.enums import AuditAction
from .repositories import DesignFeedbackRepository, SecurityAuditRepository


@dataclass
class SubmitFeedbackInput:
    customer_name: str
    customer_email: str
    customer_company: str
    category: FeedbackCategory
    title: str
    description: str
    impact_score: int
    priority_score: int


@dataclass
class SubmitFeedbackOutput:
    feedback_id: UUID
    status: str


class SubmitFeedbackUseCase:
    """Submit customer feedback on product roadmap."""

    def __init__(
        self,
        feedback_repository: DesignFeedbackRepository,
        audit_repository: SecurityAuditRepository,
        actor_id: UUID,
    ):
        self.feedback_repo = feedback_repository
        self.audit_repo = audit_repository
        self.actor_id = actor_id

    def execute(
        self, design_partner_id: UUID, input_data: SubmitFeedbackInput
    ) -> SubmitFeedbackOutput:
        """Execute feedback submission."""

        # Create feedback
        fb = DesignFeedback(
            design_partner_id=design_partner_id,
            created_by=self.actor_id,
            updated_by=self.actor_id,
            customer_name=input_data.customer_name,
            customer_email=input_data.customer_email,
            customer_company=input_data.customer_company,
            category=input_data.category,
            title=input_data.title,
            description=input_data.description,
            impact_score=input_data.impact_score,
            priority_score=input_data.priority_score,
            status=FeedbackStatus.SUBMITTED,
        )

        # Validate
        errors = fb.validate()
        if errors:
            raise ValueError(f"Feedback validation failed: {errors}")

        # Persist
        feedback_id = self.feedback_repo.save(fb)

        # Audit
        audit = SecurityAuditRecord(
            actor_id=self.actor_id,
            actor_role="customer",
            action=AuditAction.CREATED,
            resource_type="feedback",
            resource_id=feedback_id,
        )
        self.audit_repo.append(audit)

        return SubmitFeedbackOutput(feedback_id=feedback_id, status=fb.status.value)
