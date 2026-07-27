"""Repository interfaces for application layer.

These define contracts for persistence without concrete implementation.
Actual database/ORM code goes in infrastructure layer (Phase 3).
"""

from abc import ABC, abstractmethod
from uuid import UUID

from backend.domain import (
    DesignFeedback,
    DesignPartner,
    FeedbackCluster,
    Opportunity,
    PolicyDecision,
    ProductRecommendation,
    SecurityAuditRecord,
)


class OpportunityRepository(ABC):
    """Repository for Opportunity aggregate."""

    @abstractmethod
    def save(self, opportunity: Opportunity) -> UUID:
        """Save opportunity. Returns ID."""

    @abstractmethod
    def find_by_id(self, opportunity_id: UUID) -> Opportunity | None:
        """Find opportunity by ID."""

    @abstractmethod
    def find_by_company_name(self, company_name: str) -> Opportunity | None:
        """Find opportunity by company name."""

    @abstractmethod
    def list_all(self, limit: int = 100) -> list[Opportunity]:
        """List all opportunities."""


class DesignPartnerRepository(ABC):
    """Repository for DesignPartner aggregate."""

    @abstractmethod
    def save(self, design_partner: DesignPartner) -> UUID:
        """Save design partner. Returns ID."""

    @abstractmethod
    def find_by_id(self, design_partner_id: UUID) -> DesignPartner | None:
        """Find design partner by ID."""

    @abstractmethod
    def find_by_opportunity_id(self, opportunity_id: UUID) -> DesignPartner | None:
        """Find design partner by linked opportunity."""

    @abstractmethod
    def list_all(self, limit: int = 100) -> list[DesignPartner]:
        """List all design partners."""


class DesignFeedbackRepository(ABC):
    """Repository for DesignFeedback aggregate."""

    @abstractmethod
    def save(self, feedback: DesignFeedback) -> UUID:
        """Save feedback. Returns ID."""

    @abstractmethod
    def find_by_id(self, feedback_id: UUID) -> DesignFeedback | None:
        """Find feedback by ID."""

    @abstractmethod
    def find_by_design_partner_id(
        self, design_partner_id: UUID, limit: int = 100
    ) -> list[DesignFeedback]:
        """Find all feedback from a design partner."""

    @abstractmethod
    def list_all(self, limit: int = 100) -> list[DesignFeedback]:
        """List all feedback."""


class FeedbackClusterRepository(ABC):
    """Repository for FeedbackCluster aggregate."""

    @abstractmethod
    def save(self, cluster: FeedbackCluster) -> UUID:
        """Save cluster. Returns ID."""

    @abstractmethod
    def find_by_id(self, cluster_id: UUID) -> FeedbackCluster | None:
        """Find cluster by ID."""

    @abstractmethod
    def find_by_primary_feedback_id(
        self, feedback_id: UUID
    ) -> FeedbackCluster | None:
        """Find cluster by primary feedback ID."""

    @abstractmethod
    def list_all(self, limit: int = 100) -> list[FeedbackCluster]:
        """List all clusters."""


class ProductRecommendationRepository(ABC):
    """Repository for ProductRecommendation aggregate."""

    @abstractmethod
    def save(self, recommendation: ProductRecommendation) -> UUID:
        """Save recommendation. Returns ID."""

    @abstractmethod
    def find_by_id(self, recommendation_id: UUID) -> ProductRecommendation | None:
        """Find recommendation by ID."""

    @abstractmethod
    def find_by_cluster_id(self, cluster_id: UUID) -> ProductRecommendation | None:
        """Find recommendation by cluster ID."""

    @abstractmethod
    def find_undecided(self, limit: int = 50) -> list[ProductRecommendation]:
        """Find recommendations not yet decided."""

    @abstractmethod
    def list_all(self, limit: int = 100) -> list[ProductRecommendation]:
        """List all recommendations."""


class PolicyDecisionRepository(ABC):
    """Repository for PolicyDecision aggregate."""

    @abstractmethod
    def save(self, policy: PolicyDecision) -> UUID:
        """Save policy decision. Returns ID."""

    @abstractmethod
    def find_by_id(self, policy_id: UUID) -> PolicyDecision | None:
        """Find policy decision by ID."""

    @abstractmethod
    def find_by_opportunity_id(
        self, opportunity_id: UUID, limit: int = 100
    ) -> list[PolicyDecision]:
        """Find all policies for an opportunity."""

    @abstractmethod
    def find_open(self, limit: int = 100) -> list[PolicyDecision]:
        """Find all open policy decisions."""

    @abstractmethod
    def list_all(self, limit: int = 100) -> list[PolicyDecision]:
        """List all policy decisions."""


class SecurityAuditRepository(ABC):
    """Repository for SecurityAuditRecord (append-only)."""

    @abstractmethod
    def append(self, record: SecurityAuditRecord) -> UUID:
        """Append audit record (write-only, immutable). Returns ID."""

    @abstractmethod
    def find_by_id(self, record_id: UUID) -> SecurityAuditRecord | None:
        """Find audit record by ID."""

    @abstractmethod
    def find_by_resource_id(
        self, resource_id: UUID, limit: int = 100
    ) -> list[SecurityAuditRecord]:
        """Find all audit records for a resource."""

    @abstractmethod
    def find_by_actor_id(
        self, actor_id: UUID, limit: int = 100
    ) -> list[SecurityAuditRecord]:
        """Find all audit records by an actor."""

    @abstractmethod
    def list_all(self, limit: int = 100) -> list[SecurityAuditRecord]:
        """List all audit records (most recent first)."""
