"""Concrete repository implementations for Supabase."""

from .opportunity_repository import OpportunityRepositoryImpl
from .design_partner_repository import DesignPartnerRepositoryImpl
from .feedback_repository import (
    DesignFeedbackRepositoryImpl,
    FeedbackClusterRepositoryImpl,
)
from .recommendation_repository import ProductRecommendationRepositoryImpl
from .policy_repository import PolicyDecisionRepositoryImpl
from .audit_repository import SecurityAuditRepositoryImpl

__all__ = [
    "OpportunityRepositoryImpl",
    "DesignPartnerRepositoryImpl",
    "DesignFeedbackRepositoryImpl",
    "FeedbackClusterRepositoryImpl",
    "ProductRecommendationRepositoryImpl",
    "PolicyDecisionRepositoryImpl",
    "SecurityAuditRepositoryImpl",
]
