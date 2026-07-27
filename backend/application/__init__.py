"""Application Layer

Orchestrates domain models and repositories to implement use cases.
No HTTP, database, or UI code here—just business logic orchestration.

Use Cases:
- QualifyOpportunityUseCase: Assess enterprise qualification
- ConvertDesignPartnerUseCase: Convert qualified opportunity to partner
- SubmitFeedbackUseCase: Record customer feedback
- ClusterFeedbackUseCase: Group similar feedback
- GenerateRecommendationUseCase: Create product recommendation
- EvaluatePolicyUseCase: Assess governance/compliance need
- AuditSecurityEventUseCase: Record audit trail
"""

from .audit_security_event import (
    AuditSecurityEventInput,
    AuditSecurityEventOutput,
    AuditSecurityEventUseCase,
)
from .cluster_feedback import (
    ClusterFeedbackInput,
    ClusterFeedbackOutput,
    ClusterFeedbackUseCase,
)
from .convert_design_partner import (
    ConvertDesignPartnerInput,
    ConvertDesignPartnerOutput,
    ConvertDesignPartnerUseCase,
)
from .evaluate_policy import (
    EvaluatePolicyInput,
    EvaluatePolicyOutput,
    EvaluatePolicyUseCase,
)
from .generate_recommendation import (
    GenerateRecommendationInput,
    GenerateRecommendationOutput,
    GenerateRecommendationUseCase,
)
from .qualify_opportunity import (
    QualifyOpportunityInput,
    QualifyOpportunityOutput,
    QualifyOpportunityUseCase,
)
from .repositories import (
    DesignFeedbackRepository,
    DesignPartnerRepository,
    FeedbackClusterRepository,
    OpportunityRepository,
    PolicyDecisionRepository,
    ProductRecommendationRepository,
    SecurityAuditRepository,
)
from .submit_feedback import (
    SubmitFeedbackInput,
    SubmitFeedbackOutput,
    SubmitFeedbackUseCase,
)

__all__ = [
    # Repositories
    "OpportunityRepository",
    "DesignPartnerRepository",
    "DesignFeedbackRepository",
    "FeedbackClusterRepository",
    "ProductRecommendationRepository",
    "PolicyDecisionRepository",
    "SecurityAuditRepository",
    # Use Cases
    "QualifyOpportunityUseCase",
    "ConvertDesignPartnerUseCase",
    "SubmitFeedbackUseCase",
    "ClusterFeedbackUseCase",
    "GenerateRecommendationUseCase",
    "EvaluatePolicyUseCase",
    "AuditSecurityEventUseCase",
    # Input/Output DTOs
    "QualifyOpportunityInput",
    "QualifyOpportunityOutput",
    "ConvertDesignPartnerInput",
    "ConvertDesignPartnerOutput",
    "SubmitFeedbackInput",
    "SubmitFeedbackOutput",
    "ClusterFeedbackInput",
    "ClusterFeedbackOutput",
    "GenerateRecommendationInput",
    "GenerateRecommendationOutput",
    "EvaluatePolicyInput",
    "EvaluatePolicyOutput",
    "AuditSecurityEventInput",
    "AuditSecurityEventOutput",
]
