"""PartnerOpsAI Domain Layer

Pure business models for:
- Opportunity: Enterprise qualification + AI readiness
- DesignPartner: Converted opportunity (design partner engagement)
- DesignFeedback: Customer product feedback
- FeedbackCluster: Grouped similar feedback
- ProductRecommendation: AI-informed recommendation
- PolicyDecision: Governance/compliance item
- SecurityAuditRecord: Immutable audit trail
"""

from .enums import (
    OpportunityStatus,
    ICPAlignment,
    MaturityLevel,
    DesignPartnerStatus,
    PartnerHealth,
    FeedbackCategory,
    FeedbackStatus,
    ReleaseTarget,
    AuditAction,
    PolicyResult,
)

from .opportunity import Opportunity
from .design_partner import DesignPartner
from .feedback import DesignFeedback, FeedbackCluster
from .recommendation import ProductRecommendation
from .audit import SecurityAuditRecord, PolicyDecision

__all__ = [
    # Enums
    "OpportunityStatus",
    "ICPAlignment",
    "MaturityLevel",
    "DesignPartnerStatus",
    "PartnerHealth",
    "FeedbackCategory",
    "FeedbackStatus",
    "ReleaseTarget",
    "AuditAction",
    "PolicyResult",
    # Models
    "Opportunity",
    "DesignPartner",
    "DesignFeedback",
    "FeedbackCluster",
    "ProductRecommendation",
    "SecurityAuditRecord",
    "PolicyDecision",
]
