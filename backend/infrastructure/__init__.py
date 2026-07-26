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
    OpportunityRepositoryImpl,
    DesignPartnerRepositoryImpl,
    DesignFeedbackRepositoryImpl,
    FeedbackClusterRepositoryImpl,
    ProductRecommendationRepositoryImpl,
    PolicyDecisionRepositoryImpl,
    SecurityAuditRepositoryImpl,
)

__all__ = [
    "DomainMapper",
    "OpportunityRepositoryImpl",
    "DesignPartnerRepositoryImpl",
    "DesignFeedbackRepositoryImpl",
    "FeedbackClusterRepositoryImpl",
    "ProductRecommendationRepositoryImpl",
    "PolicyDecisionRepositoryImpl",
    "SecurityAuditRepositoryImpl",
]
