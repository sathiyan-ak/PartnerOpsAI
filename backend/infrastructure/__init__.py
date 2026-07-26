"""Infrastructure Layer (Persistence)

Concrete implementations of repositories using Supabase PostgreSQL.
No business logic here—just data access abstraction.

Provides:
- DatabaseClient: Supabase connection singleton
- DomainMapper: Converts domain ↔ database
- Repository implementations (OpportunityRepositoryImpl, etc.)
- SQL schema with RLS and indexes
"""

from .database import db, DatabaseClient
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
    "db",
    "DatabaseClient",
    "DomainMapper",
    "OpportunityRepositoryImpl",
    "DesignPartnerRepositoryImpl",
    "DesignFeedbackRepositoryImpl",
    "FeedbackClusterRepositoryImpl",
    "ProductRecommendationRepositoryImpl",
    "PolicyDecisionRepositoryImpl",
    "SecurityAuditRepositoryImpl",
]
