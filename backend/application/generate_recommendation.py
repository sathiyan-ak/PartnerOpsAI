"""Generate Product Recommendation use case."""

from dataclasses import dataclass
from uuid import UUID

from ..domain import ProductRecommendation, ReleaseTarget
from ..domain.audit import SecurityAuditRecord
from ..domain.enums import AuditAction, PolicyResult
from .repositories import (
    FeedbackClusterRepository,
    ProductRecommendationRepository,
    SecurityAuditRepository,
)


@dataclass
class GenerateRecommendationInput:
    cluster_id: UUID
    aggregate_impact_score: int
    aggregate_priority_score: int
    requesting_customer_count: int
    total_feedback_items: int
    business_justification: str
    market_opportunity: str
    revenue_impact_potential: str
    competitive_positioning: str
    recommendation: str  # BUILD | DEFER | REJECT | RESEARCH
    recommendation_reasoning: str
    suggested_release: ReleaseTarget
    release_reasoning: str
    estimated_effort: str  # small | medium | large | xlarge
    affected_personas: list[str]
    dependencies: list[str]
    risks: list[str]


@dataclass
class GenerateRecommendationOutput:
    recommendation_id: UUID
    business_score: int
    confidence: float
    recommendation: str


class GenerateRecommendationUseCase:
    """Generate AI-informed product recommendation from feedback cluster."""

    def __init__(
        self,
        cluster_repository: FeedbackClusterRepository,
        recommendation_repository: ProductRecommendationRepository,
        audit_repository: SecurityAuditRepository,
        actor_id: UUID,
    ):
        self.cluster_repo = cluster_repository
        self.recommendation_repo = recommendation_repository
        self.audit_repo = audit_repository
        self.actor_id = actor_id

    def execute(self, input_data: GenerateRecommendationInput) -> GenerateRecommendationOutput:
        """Execute recommendation generation."""

        # Load cluster
        cluster = self.cluster_repo.find_by_id(input_data.cluster_id)
        if not cluster:
            raise ValueError(f"Cluster {input_data.cluster_id} not found")

        # Create recommendation
        rec = ProductRecommendation(
            created_by=self.actor_id,
            updated_by=self.actor_id,
            feedback_cluster_id=input_data.cluster_id,
            title=cluster.theme,
            aggregate_impact_score=input_data.aggregate_impact_score,
            aggregate_priority_score=input_data.aggregate_priority_score,
            requesting_customer_count=input_data.requesting_customer_count,
            total_feedback_items=input_data.total_feedback_items,
            business_justification=input_data.business_justification,
            market_opportunity=input_data.market_opportunity,
            revenue_impact_potential=input_data.revenue_impact_potential,
            competitive_positioning=input_data.competitive_positioning,
            recommendation=input_data.recommendation,
            recommendation_reasoning=input_data.recommendation_reasoning,
            suggested_release=input_data.suggested_release,
            release_reasoning=input_data.release_reasoning,
            estimated_effort=input_data.estimated_effort,
            affected_personas=input_data.affected_personas,
            dependencies=input_data.dependencies,
            risks=input_data.risks,
        )

        # Validate
        errors = rec.validate()
        if errors:
            raise ValueError(f"Recommendation validation failed: {errors}")

        # Calculate deterministic scores (NOT LLM)
        rec.business_score = rec.calculate_business_score()
        rec.confidence = rec.calculate_confidence()

        # Persist
        rec_id = self.recommendation_repo.save(rec)

        # Audit
        audit = SecurityAuditRecord(
            actor_id=self.actor_id,
            actor_role="recommendation_engine",
            action=AuditAction.CREATED,
            resource_type="recommendation",
            resource_id=rec_id,
            policy_result=PolicyResult.APPROVED,
            context_data={
                "business_score": rec.business_score,
                "confidence": float(rec.confidence),
                "recommendation": input_data.recommendation,
            },
        )
        self.audit_repo.append(audit)

        return GenerateRecommendationOutput(
            recommendation_id=rec_id,
            business_score=rec.business_score,
            confidence=rec.confidence,
            recommendation=input_data.recommendation,
        )
