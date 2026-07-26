"""
PartnerOpsAI Domain Models

Pure business models for:
- Opportunities (prospects from Phase 4)
- Design Feedback (customer feedback from Phase 6)
- Feedback Clusters (duplicate grouping)
- Product Recommendations (priority + release suggestions)
- Policy Decisions (governance from Phase 5)
- Security Audit Records (audit trail)

Framework-independent. Testable. Serializable.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4


class OpportunityStatus(str, Enum):
    """Lifecycle status for opportunities (prospects)."""
    PROSPECTING = "prospecting"
    QUALIFIED = "qualified"
    NEGOTIATING = "negotiating"
    WON = "won"
    LOST = "lost"
    DEFERRED = "deferred"


class RiskLevel(str, Enum):
    """Risk assessment levels."""
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"


class FeedbackCategory(str, Enum):
    """Types of customer feedback."""
    FEATURE_REQUEST = "feature_request"
    BUG = "bug"
    ENHANCEMENT = "enhancement"
    INTEGRATION = "integration"
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
    """Lifecycle status for policy/governance decisions."""
    OPEN = "open"
    IN_REVIEW = "in_review"
    RESOLVED = "resolved"
    DEFERRED = "deferred"


@dataclass
class Opportunity:
    """
    Enterprise prospect opportunity.

    Represents a potential customer deal with associated context.
    Used in Phase 4: Enterprise Prospect Intelligence.
    """
    id: UUID = field(default_factory=uuid4)
    owner_id: UUID = field(default_factory=uuid4)
    company_name: str = ""
    deal_size_usd: int = 0  # in dollars
    status: OpportunityStatus = OpportunityStatus.PROSPECTING

    # Risk factors
    legal_risk_score: int = 0  # 0-100
    funding_risk_score: int = 0  # 0-100
    momentum_score: int = 0  # 0-100
    overall_risk_level: RiskLevel = RiskLevel.GREEN

    # Stakeholders
    buyer_name: str = ""
    buyer_email: str = ""
    legal_contact_name: str = ""
    legal_contact_email: str = ""
    executive_sponsor_name: str = ""

    # Context
    funding_sources: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    notes: str = ""

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def validate(self) -> List[str]:
        """
        Validate opportunity data.
        Returns list of errors (empty if valid).
        """
        errors = []
        if not self.company_name.strip():
            errors.append("company_name: required")
        if self.deal_size_usd < 0:
            errors.append("deal_size_usd: must be >= 0")
        if not 0 <= self.legal_risk_score <= 100:
            errors.append("legal_risk_score: must be 0-100")
        if not 0 <= self.funding_risk_score <= 100:
            errors.append("funding_risk_score: must be 0-100")
        if not 0 <= self.momentum_score <= 100:
            errors.append("momentum_score: must be 0-100")
        return errors

    def calculate_overall_risk(self) -> RiskLevel:
        """
        Deterministic: Calculate overall risk level from component scores.

        Rules:
        - If any score >= 70: RED
        - If any score >= 50: YELLOW
        - Otherwise: GREEN
        """
        max_score = max(self.legal_risk_score, self.funding_risk_score, self.momentum_score)
        if max_score >= 70:
            return RiskLevel.RED
        elif max_score >= 50:
            return RiskLevel.YELLOW
        else:
            return RiskLevel.GREEN

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        data = asdict(self)
        data['id'] = str(self.id)
        data['owner_id'] = str(self.owner_id)
        data['status'] = self.status.value
        data['overall_risk_level'] = self.overall_risk_level.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Opportunity':
        """Deserialize from dictionary."""
        data = data.copy()
        data['id'] = UUID(data['id']) if isinstance(data['id'], str) else data['id']
        data['owner_id'] = UUID(data['owner_id']) if isinstance(data['owner_id'], str) else data['owner_id']
        data['status'] = OpportunityStatus(data['status']) if isinstance(data['status'], str) else data['status']
        data['overall_risk_level'] = RiskLevel(data['overall_risk_level']) if isinstance(data['overall_risk_level'], str) else data['overall_risk_level']
        data['created_at'] = datetime.fromisoformat(data['created_at']) if isinstance(data['created_at'], str) else data['created_at']
        data['updated_at'] = datetime.fromisoformat(data['updated_at']) if isinstance(data['updated_at'], str) else data['updated_at']
        return cls(**data)


@dataclass
class DesignFeedback:
    """
    Customer feedback on product roadmap.

    Represents feedback submitted by a design partner.
    Used in Phase 6: Design Partner Portal.
    """
    id: UUID = field(default_factory=uuid4)
    opportunity_id: UUID = field(default_factory=uuid4)
    owner_id: UUID = field(default_factory=uuid4)

    # Submitter info
    customer_name: str = ""
    customer_company: str = ""

    # Feedback content
    category: FeedbackCategory = FeedbackCategory.OTHER
    category_confidence: float = 0.0  # 0.0-1.0
    description: str = ""

    # Scoring (deterministic, not AI)
    impact_score: int = 0  # 0-100
    priority_score: int = 0  # 0-100
    confidence: float = 0.0  # 0.0-1.0 (how certain are we about this score?)

    # AI-generated insights (with reasoning)
    similar_feedback_ids: List[UUID] = field(default_factory=list)
    similarity_explanation: str = ""

    suggested_release: ReleaseTarget = ReleaseTarget.BACKLOG
    release_reasoning: str = ""

    product_decision_summary: str = ""
    decision_evidence: str = ""

    # Status
    status: FeedbackStatus = FeedbackStatus.SUBMITTED

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def validate(self) -> List[str]:
        """Validate feedback data."""
        errors = []
        if not self.customer_name.strip():
            errors.append("customer_name: required")
        if not self.description.strip():
            errors.append("description: required")
        if not 0 <= self.impact_score <= 100:
            errors.append("impact_score: must be 0-100")
        if not 0 <= self.priority_score <= 100:
            errors.append("priority_score: must be 0-100")
        if not 0.0 <= self.confidence <= 1.0:
            errors.append("confidence: must be 0.0-1.0")
        if not 0.0 <= self.category_confidence <= 1.0:
            errors.append("category_confidence: must be 0.0-1.0")
        return errors

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        data = asdict(self)
        data['id'] = str(self.id)
        data['opportunity_id'] = str(self.opportunity_id)
        data['owner_id'] = str(self.owner_id)
        data['category'] = self.category.value
        data['suggested_release'] = self.suggested_release.value
        data['status'] = self.status.value
        data['similar_feedback_ids'] = [str(fid) for fid in self.similar_feedback_ids]
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DesignFeedback':
        """Deserialize from dictionary."""
        data = data.copy()
        data['id'] = UUID(data['id']) if isinstance(data['id'], str) else data['id']
        data['opportunity_id'] = UUID(data['opportunity_id']) if isinstance(data['opportunity_id'], str) else data['opportunity_id']
        data['owner_id'] = UUID(data['owner_id']) if isinstance(data['owner_id'], str) else data['owner_id']
        data['category'] = FeedbackCategory(data['category']) if isinstance(data['category'], str) else data['category']
        data['suggested_release'] = ReleaseTarget(data['suggested_release']) if isinstance(data['suggested_release'], str) else data['suggested_release']
        data['status'] = FeedbackStatus(data['status']) if isinstance(data['status'], str) else data['status']
        data['similar_feedback_ids'] = [UUID(fid) if isinstance(fid, str) else fid for fid in data.get('similar_feedback_ids', [])]
        data['created_at'] = datetime.fromisoformat(data['created_at']) if isinstance(data['created_at'], str) else data['created_at']
        data['updated_at'] = datetime.fromisoformat(data['updated_at']) if isinstance(data['updated_at'], str) else data['updated_at']
        return cls(**data)


@dataclass
class PolicyDecision:
    """
    Governance or compliance decision item.

    Represents a policy/legal/compliance issue that needs action.
    Used in Phase 5: AI Governance Pipeline.
    """
    id: UUID = field(default_factory=uuid4)
    opportunity_id: UUID = field(default_factory=uuid4)
    owner_id: UUID = field(default_factory=uuid4)

    title: str = ""
    description: str = ""
    category: str = "governance"  # e.g., "legal", "compliance", "security", "risk"

    # Scoring (deterministic)
    impact_score: int = 0  # 0-100: how badly blocks the deal
    urgency_score: int = 0  # 0-100: how soon must be resolved
    effort_score: int = 0  # 0-100: how much work to resolve
    priority_score: int = 0  # calculated: (impact*0.5 + urgency*0.4) + (1-effort/100)*0.1
    confidence: float = 0.0  # 0.0-1.0

    # Reasoning
    reasoning: str = ""
    recommendation: str = ""

    # Status
    status: PolicyDecisionStatus = PolicyDecisionStatus.OPEN
    assigned_to_id: Optional[UUID] = None
    due_date: Optional[datetime] = None

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def validate(self) -> List[str]:
        """Validate policy decision data."""
        errors = []
        if not self.title.strip():
            errors.append("title: required")
        if not 0 <= self.impact_score <= 100:
            errors.append("impact_score: must be 0-100")
        if not 0 <= self.urgency_score <= 100:
            errors.append("urgency_score: must be 0-100")
        if not 0 <= self.effort_score <= 100:
            errors.append("effort_score: must be 0-100")
        if not 0.0 <= self.confidence <= 1.0:
            errors.append("confidence: must be 0.0-1.0")
        return errors

    def calculate_priority(self) -> int:
        """
        Deterministic: Calculate priority from component scores.

        Formula: (impact * 0.5) + (urgency * 0.4) + (1 - effort/100) * 0.1
        Result: 0-100 scale
        """
        effort_factor = 1.0 - (self.effort_score / 100.0)
        priority = (self.impact_score * 0.5) + (self.urgency_score * 0.4) + (effort_factor * 0.1 * 100)
        return int(min(100, max(0, priority)))

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        data = asdict(self)
        data['id'] = str(self.id)
        data['opportunity_id'] = str(self.opportunity_id)
        data['owner_id'] = str(self.owner_id)
        data['status'] = self.status.value
        if data['assigned_to_id']:
            data['assigned_to_id'] = str(data['assigned_to_id'])
        if data['due_date']:
            data['due_date'] = data['due_date'].isoformat()
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PolicyDecision':
        """Deserialize from dictionary."""
        data = data.copy()
        data['id'] = UUID(data['id']) if isinstance(data['id'], str) else data['id']
        data['opportunity_id'] = UUID(data['opportunity_id']) if isinstance(data['opportunity_id'], str) else data['opportunity_id']
        data['owner_id'] = UUID(data['owner_id']) if isinstance(data['owner_id'], str) else data['owner_id']
        if data.get('assigned_to_id'):
            data['assigned_to_id'] = UUID(data['assigned_to_id']) if isinstance(data['assigned_to_id'], str) else data['assigned_to_id']
        data['status'] = PolicyDecisionStatus(data['status']) if isinstance(data['status'], str) else data['status']
        if data.get('due_date') and isinstance(data['due_date'], str):
            data['due_date'] = datetime.fromisoformat(data['due_date'])
        data['created_at'] = datetime.fromisoformat(data['created_at']) if isinstance(data['created_at'], str) else data['created_at']
        data['updated_at'] = datetime.fromisoformat(data['updated_at']) if isinstance(data['updated_at'], str) else data['updated_at']
        return cls(**data)


@dataclass
class ActivityLogEntry:
    """
    Audit trail record for all meaningful state changes.

    Immutable (append-only). Used by all phases.
    """
    id: UUID = field(default_factory=uuid4)
    user_id: UUID = field(default_factory=uuid4)

    action: str = ""  # e.g., "created", "updated", "deleted", "approved"
    table_name: str = ""  # e.g., "opportunities", "feedback", "policies"
    record_id: UUID = field(default_factory=uuid4)

    old_value: Optional[Dict[str, Any]] = None
    new_value: Optional[Dict[str, Any]] = None

    created_at: datetime = field(default_factory=datetime.utcnow)

    def validate(self) -> List[str]:
        """Validate activity log entry."""
        errors = []
        if not self.action.strip():
            errors.append("action: required")
        if not self.table_name.strip():
            errors.append("table_name: required")
        return errors

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        data = asdict(self)
        data['id'] = str(self.id)
        data['user_id'] = str(self.user_id)
        data['record_id'] = str(self.record_id)
        data['created_at'] = self.created_at.isoformat()
        return data


@dataclass
class FeedbackCluster:
    """
    Groups similar feedback items together for analysis.

    Represents duplicate or highly related feedback.
    Used in Phase 6 for deduplication.
    """
    id: UUID = field(default_factory=uuid4)

    primary_feedback_id: UUID = field(default_factory=uuid4)
    related_feedback_ids: List[UUID] = field(default_factory=list)

    cluster_reason: str = ""  # Why are these grouped? e.g., "same keyword", "similar use case"
    merged_at: Optional[datetime] = None

    def add_related(self, feedback_id: UUID) -> None:
        """Add a related feedback to the cluster."""
        if feedback_id not in self.related_feedback_ids:
            self.related_feedback_ids.append(feedback_id)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        data = asdict(self)
        data['id'] = str(self.id)
        data['primary_feedback_id'] = str(self.primary_feedback_id)
        data['related_feedback_ids'] = [str(fid) for fid in self.related_feedback_ids]
        if data['merged_at']:
            data['merged_at'] = data['merged_at'].isoformat()
        return data
