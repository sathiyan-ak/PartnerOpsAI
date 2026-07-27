"""Infrastructure Layer (Persistence)

Concrete implementations of repositories using PostgreSQL.
No business logic here—just data access abstraction.

Provides:
- DomainMapper: Converts domain ↔ database
- Repository implementations (OpportunityRepositoryImpl, etc.)
- SQL schema with indexes
"""

from .mapper import DomainMapper
from .repositories import (
    DesignFeedbackRepositoryImpl,
    DesignPartnerRepositoryImpl,
    FeedbackClusterRepositoryImpl,
    OpportunityRepositoryImpl,
    PolicyDecisionRepositoryImpl,
    ProductRecommendationRepositoryImpl,
    SecurityAuditRepositoryImpl,
)

__all__ = [
    "DesignFeedbackRepositoryImpl",
    "DesignPartnerRepositoryImpl",
    "DomainMapper",
    "FeedbackClusterRepositoryImpl",
    "OpportunityRepositoryImpl",
    "PolicyDecisionRepositoryImpl",
    "ProductRecommendationRepositoryImpl",
    "SecurityAuditRepositoryImpl",
]
