"""Domain enums for PartnerOpsAI."""

from enum import Enum


class OpportunityStatus(str, Enum):
    """Lifecycle status for enterprise opportunities."""

    PROSPECT = "prospect"
    QUALIFIED = "qualified"
    CONVERTED = "converted"
    DESIGN_PARTNER = "design_partner"
    LOST = "lost"


class ICPAlignment(str, Enum):
    """Ideal Customer Profile alignment."""

    PERFECT = "perfect"
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"


class MaturityLevel(str, Enum):
    """AI/Security/Product maturity assessment."""

    ADVANCED = "advanced"
    INTERMEDIATE = "intermediate"
    BEGINNER = "beginner"
    NONE = "none"


class DesignPartnerStatus(str, Enum):
    """Onboarding/implementation status of design partner."""

    ONBOARDING = "onboarding"
    ACTIVE = "active"
    IN_IMPLEMENTATION = "in_implementation"
    SHIPPED = "shipped"
    INACTIVE = "inactive"


class PartnerHealth(str, Enum):
    """Health score of design partner relationship."""

    EXCELLENT = "excellent"
    GOOD = "good"
    AT_RISK = "at_risk"
    CRITICAL = "critical"


class FeedbackCategory(str, Enum):
    """Types of customer feedback."""

    FEATURE_REQUEST = "feature_request"
    BUG = "bug"
    ENHANCEMENT = "enhancement"
    INTEGRATION = "integration"
    WORKFLOW = "workflow"
    OTHER = "other"


class FeedbackStatus(str, Enum):
    """Lifecycle status for feedback items."""

    SUBMITTED = "submitted"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    IN_DEVELOPMENT = "in_development"
    SHIPPED = "shipped"
    DEFERRED = "deferred"


class ReleaseTarget(str, Enum):
    """Suggested release timing."""

    UPCOMING = "upcoming"
    NEXT_MINOR = "next_minor"
    NEXT_MAJOR = "next_major"
    BACKLOG = "backlog"


class PolicyDecisionStatus(str, Enum):
    """Lifecycle status for governance decisions."""

    OPEN = "open"
    IN_REVIEW = "in_review"
    RESOLVED = "resolved"
    DEFERRED = "deferred"


class AuditAction(str, Enum):
    """Type of action in security audit record."""

    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    POLICY_EVALUATED = "policy_evaluated"
    POLICY_OVERRIDE = "policy_override"


class PolicyResult(str, Enum):
    """Result of policy evaluation."""

    APPROVED = "approved"
    REJECTED = "rejected"
    REVIEW_REQUIRED = "review_required"
    OVERRIDE = "override"
