"""Product Recommendation repository."""

from typing import Optional, List
from uuid import UUID
from backend.domain import ProductRecommendation
from backend.application.repositories import ProductRecommendationRepository
from ..database import db
from ..mapper import DomainMapper


class ProductRecommendationRepositoryImpl(ProductRecommendationRepository):
    def save(self, recommendation: ProductRecommendation) -> UUID:
        data = DomainMapper.recommendation_to_db(recommendation)
        if recommendation.version > 0:
            data["version"] = recommendation.version + 1
        response = db.get_table("product_recommendations").upsert(data).execute()
        if not response.data:
            raise RuntimeError(f"Failed to save recommendation {recommendation.id}")
        return UUID(response.data[0]["id"])

    def find_by_id(self, recommendation_id: UUID) -> Optional[ProductRecommendation]:
        response = db.get_table("product_recommendations").select("*").eq("id", str(recommendation_id)).execute()
        return DomainMapper.db_to_recommendation(response.data[0]) if response.data else None

    def find_by_cluster_id(self, cluster_id: UUID) -> Optional[ProductRecommendation]:
        response = (
            db.get_table("product_recommendations")
            .select("*")
            .eq("feedback_cluster_id", str(cluster_id))
            .limit(1)
            .execute()
        )
        return DomainMapper.db_to_recommendation(response.data[0]) if response.data else None

    def find_undecided(self, limit: int = 50) -> List[ProductRecommendation]:
        response = (
            db.get_table("product_recommendations")
            .select("*")
            .eq("decision_made", False)
            .limit(limit)
            .execute()
        )
        return [DomainMapper.db_to_recommendation(row) for row in response.data]

    def list_all(self, limit: int = 100) -> List[ProductRecommendation]:
        response = db.get_table("product_recommendations").select("*").limit(limit).execute()
        return [DomainMapper.db_to_recommendation(row) for row in response.data]
