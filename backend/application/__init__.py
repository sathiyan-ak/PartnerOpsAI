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

from .repositories import (
    OpportunityRepository,
    DesignPartnerRepository,
    DesignFeedbackRepository,
    FeedbackClusterRepository,
    ProductRecommendationRepository,
    PolicyDecisionRepository,
    SecurityAuditRepository,
)

from .qualify_opportunity import (
    QualifyOpportunityUseCase,
    QualifyOpportunityInput,
    QualifyOpportunityOutput,
)
from .convert_design_partner import (
    ConvertDesignPartnerUseCase,
    ConvertDesignPartnerInput,
    ConvertDesignPartnerOutput,
)
from .submit_feedback import (
    SubmitFeedbackUseCase,
    SubmitFeedbackInput,
    SubmitFeedbackOutput,
)
from .cluster_feedback import (
    ClusterFeedbackUseCase,
    ClusterFeedbackInput,
    ClusterFeedbackOutput,
)
from .generate_recommendation import (
    GenerateRecommendationUseCase,
    GenerateRecommendationInput,
    GenerateRecommendationOutput,
)
from .evaluate_policy import (
    EvaluatePolicyUseCase,
    EvaluatePolicyInput,
    EvaluatePolicyOutput,
)
from .audit_security_event import (
    AuditSecurityEventUseCase,
    AuditSecurityEventInput,
    AuditSecurityEventOutput,
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
