"""Repository interfaces for application layer.

These define contracts for persistence without concrete implementation.
Actual database/ORM code goes in infrastructure layer (Phase 3).
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from backend.domain import (
    Opportunity,
    DesignPartner,
    DesignFeedback,
    FeedbackCluster,
    ProductRecommendation,
    PolicyDecision,
    SecurityAuditRecord,
)


class OpportunityRepository(ABC):
    """Repository for Opportunity aggregate."""

    @abstractmethod
    def save(self, opportunity: Opportunity) -> UUID:
        """Save opportunity. Returns ID."""
        pass

    @abstractmethod
    def find_by_id(self, opportunity_id: UUID) -> Optional[Opportunity]:
        """Find opportunity by ID."""
        pass

    @abstractmethod
    def find_by_company_name(self, company_name: str) -> Optional[Opportunity]:
        """Find opportunity by company name."""
        pass

    @abstractmethod
    def list_all(self, limit: int = 100) -> List[Opportunity]:
        """List all opportunities."""
        pass


class DesignPartnerRepository(ABC):
    """Repository for DesignPartner aggregate."""

    @abstractmethod
    def save(self, design_partner: DesignPartner) -> UUID:
        """Save design partner. Returns ID."""
        pass

    @abstractmethod
    def find_by_id(self, design_partner_id: UUID) -> Optional[DesignPartner]:
        """Find design partner by ID."""
        pass

    @abstractmethod
    def find_by_opportunity_id(self, opportunity_id: UUID) -> Optional[DesignPartner]:
        """Find design partner by linked opportunity."""
        pass

    @abstractmethod
    def list_all(self, limit: int = 100) -> List[DesignPartner]:
        """List all design partners."""
        pass


class DesignFeedbackRepository(ABC):
    """Repository for DesignFeedback aggregate."""

    @abstractmethod
    def save(self, feedback: DesignFeedback) -> UUID:
        """Save feedback. Returns ID."""
        pass

    @abstractmethod
    def find_by_id(self, feedback_id: UUID) -> Optional[DesignFeedback]:
        """Find feedback by ID."""
        pass

    @abstractmethod
    def find_by_design_partner_id(
        self, design_partner_id: UUID, limit: int = 100
    ) -> List[DesignFeedback]:
        """Find all feedback from a design partner."""
        pass

    @abstractmethod
    def list_all(self, limit: int = 100) -> List[DesignFeedback]:
        """List all feedback."""
        pass


class FeedbackClusterRepository(ABC):
    """Repository for FeedbackCluster aggregate."""

    @abstractmethod
    def save(self, cluster: FeedbackCluster) -> UUID:
        """Save cluster. Returns ID."""
        pass

    @abstractmethod
    def find_by_id(self, cluster_id: UUID) -> Optional[FeedbackCluster]:
        """Find cluster by ID."""
        pass

    @abstractmethod
    def find_by_primary_feedback_id(
        self, feedback_id: UUID
    ) -> Optional[FeedbackCluster]:
        """Find cluster by primary feedback ID."""
        pass

    @abstractmethod
    def list_all(self, limit: int = 100) -> List[FeedbackCluster]:
        """List all clusters."""
        pass


class ProductRecommendationRepository(ABC):
    """Repository for ProductRecommendation aggregate."""

    @abstractmethod
    def save(self, recommendation: ProductRecommendation) -> UUID:
        """Save recommendation. Returns ID."""
        pass

    @abstractmethod
    def find_by_id(self, recommendation_id: UUID) -> Optional[ProductRecommendation]:
        """Find recommendation by ID."""
        pass

    @abstractmethod
    def find_by_cluster_id(self, cluster_id: UUID) -> Optional[ProductRecommendation]:
        """Find recommendation by cluster ID."""
        pass

    @abstractmethod
    def find_undecided(self, limit: int = 50) -> List[ProductRecommendation]:
        """Find recommendations not yet decided."""
        pass

    @abstractmethod
    def list_all(self, limit: int = 100) -> List[ProductRecommendation]:
        """List all recommendations."""
        pass


class PolicyDecisionRepository(ABC):
    """Repository for PolicyDecision aggregate."""

    @abstractmethod
    def save(self, policy: PolicyDecision) -> UUID:
        """Save policy decision. Returns ID."""
        pass

    @abstractmethod
    def find_by_id(self, policy_id: UUID) -> Optional[PolicyDecision]:
        """Find policy decision by ID."""
        pass

    @abstractmethod
    def find_by_opportunity_id(
        self, opportunity_id: UUID, limit: int = 100
    ) -> List[PolicyDecision]:
        """Find all policies for an opportunity."""
        pass

    @abstractmethod
    def find_open(self, limit: int = 100) -> List[PolicyDecision]:
        """Find all open policy decisions."""
        pass

    @abstractmethod
    def list_all(self, limit: int = 100) -> List[PolicyDecision]:
        """List all policy decisions."""
        pass


class SecurityAuditRepository(ABC):
    """Repository for SecurityAuditRecord (append-only)."""

    @abstractmethod
    def append(self, record: SecurityAuditRecord) -> UUID:
        """Append audit record (write-only, immutable). Returns ID."""
        pass

    @abstractmethod
    def find_by_id(self, record_id: UUID) -> Optional[SecurityAuditRecord]:
        """Find audit record by ID."""
        pass

    @abstractmethod
    def find_by_resource_id(
        self, resource_id: UUID, limit: int = 100
    ) -> List[SecurityAuditRecord]:
        """Find all audit records for a resource."""
        pass

    @abstractmethod
    def find_by_actor_id(
        self, actor_id: UUID, limit: int = 100
    ) -> List[SecurityAuditRecord]:
        """Find all audit records by an actor."""
        pass

    @abstractmethod
    def list_all(self, limit: int = 100) -> List[SecurityAuditRecord]:
        """List all audit records (most recent first)."""
        pass
