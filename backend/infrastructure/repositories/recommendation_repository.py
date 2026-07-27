"""Product Recommendation repository (PostgreSQL)."""

import json
import psycopg2
from typing import Optional, List
from uuid import UUID

from backend.domain import ProductRecommendation, ReleaseTarget
from backend.application.repositories import ProductRecommendationRepository


class ProductRecommendationRepositoryImpl(ProductRecommendationRepository):
    """PostgreSQL implementation of ProductRecommendationRepository."""

    def __init__(self, db_url: str = None):
        """Initialize with database URL."""
        if db_url is None:
            import os

            db_url = os.getenv(
                "DATABASE_URL",
                "postgresql://test_user:test_password@localhost:5432/partneropsa_test",
            )
        self.db_url = db_url

    def _connect(self):
        """Get database connection."""
        return psycopg2.connect(self.db_url)

    def save(self, recommendation: ProductRecommendation) -> UUID:
        """Save or update recommendation."""
        conn = self._connect()
        cursor = conn.cursor()

        try:
            sql = """
                INSERT INTO product_recommendations (
                    id, feedback_cluster_id, created_by, updated_by, version,
                    title, aggregate_impact_score, aggregate_priority_score,
                    requesting_customer_count, total_feedback_items,
                    business_justification, market_opportunity,
                    revenue_impact_potential, competitive_positioning,
                    recommendation, recommendation_reasoning,
                    suggested_release, release_reasoning,
                    estimated_effort, affected_personas, dependencies, risks,
                    confidence
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (id) DO UPDATE SET
                    updated_by=EXCLUDED.updated_by,
                    version=EXCLUDED.version + 1,
                    title=EXCLUDED.title,
                    aggregate_impact_score=EXCLUDED.aggregate_impact_score,
                    aggregate_priority_score=EXCLUDED.aggregate_priority_score,
                    requesting_customer_count=EXCLUDED.requesting_customer_count,
                    total_feedback_items=EXCLUDED.total_feedback_items,
                    business_justification=EXCLUDED.business_justification,
                    market_opportunity=EXCLUDED.market_opportunity,
                    revenue_impact_potential=EXCLUDED.revenue_impact_potential,
                    competitive_positioning=EXCLUDED.competitive_positioning,
                    recommendation=EXCLUDED.recommendation,
                    recommendation_reasoning=EXCLUDED.recommendation_reasoning,
                    suggested_release=EXCLUDED.suggested_release,
                    release_reasoning=EXCLUDED.release_reasoning,
                    estimated_effort=EXCLUDED.estimated_effort,
                    affected_personas=EXCLUDED.affected_personas,
                    dependencies=EXCLUDED.dependencies,
                    risks=EXCLUDED.risks,
                    confidence=EXCLUDED.confidence
            """
            cursor.execute(
                sql,
                (
                    str(recommendation.id),
                    str(recommendation.feedback_cluster_id),
                    str(recommendation.created_by),
                    str(recommendation.updated_by),
                    recommendation.version,
                    recommendation.title,
                    recommendation.aggregate_impact_score,
                    recommendation.aggregate_priority_score,
                    recommendation.requesting_customer_count,
                    recommendation.total_feedback_items,
                    recommendation.business_justification,
                    recommendation.market_opportunity,
                    recommendation.revenue_impact_potential,
                    recommendation.competitive_positioning,
                    recommendation.recommendation.lower(),  # Normalize to lowercase for CHECK constraint
                    recommendation.recommendation_reasoning,
                    recommendation.suggested_release.value,
                    recommendation.release_reasoning,
                    recommendation.estimated_effort,
                    recommendation.affected_personas,
                    recommendation.dependencies,
                    recommendation.risks,
                    float(recommendation.confidence),
                ),
            )
            conn.commit()
            return recommendation.id
        except psycopg2.Error as e:
            conn.rollback()
            raise RuntimeError(f"Database constraint violation: {str(e).split(chr(10))[0]}") from e
        finally:
            cursor.close()
            conn.close()

    def find_by_id(self, recommendation_id: UUID) -> Optional[ProductRecommendation]:
        """Find recommendation by ID."""
        conn = self._connect()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT * FROM product_recommendations WHERE id = %s",
                (str(recommendation_id),),
            )
            row = cursor.fetchone()
            return self._row_to_recommendation(row) if row else None
        finally:
            cursor.close()
            conn.close()

    def find_by_cluster_id(self, cluster_id: UUID) -> Optional[ProductRecommendation]:
        """Find recommendation by cluster ID."""
        conn = self._connect()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT * FROM product_recommendations WHERE feedback_cluster_id = %s LIMIT 1",
                (str(cluster_id),),
            )
            row = cursor.fetchone()
            return self._row_to_recommendation(row) if row else None
        finally:
            cursor.close()
            conn.close()

    def find_undecided(self, limit: int = 50) -> List[ProductRecommendation]:
        """Find undecided recommendations."""
        conn = self._connect()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT * FROM product_recommendations WHERE recommendation = 'BUILD' LIMIT %s",
                (limit,),
            )
            rows = cursor.fetchall()
            return [self._row_to_recommendation(row) for row in rows]
        finally:
            cursor.close()
            conn.close()

    def list_all(self, limit: int = 100) -> List[ProductRecommendation]:
        """List all recommendations."""
        conn = self._connect()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM product_recommendations LIMIT %s", (limit,))
            rows = cursor.fetchall()
            return [self._row_to_recommendation(row) for row in rows]
        finally:
            cursor.close()
            conn.close()

    def _row_to_recommendation(self, row) -> ProductRecommendation:
        """Convert database row to ProductRecommendation domain object."""
        # Handle arrays in different formats: Python list, JSON string, or PostgreSQL literal
        def parse_array(value):
            if value is None or value == '':
                return []
            if isinstance(value, list):
                return value
            elif isinstance(value, str):
                if value.startswith('{'):
                    # PostgreSQL array literal: {val1,val2}
                    inner = value.strip('{}')
                    if not inner:
                        return []
                    return [x.strip().strip('"') for x in inner.split(',') if x.strip()]
                else:
                    # Try JSON
                    try:
                        return json.loads(value)
                    except (json.JSONDecodeError, ValueError):
                        return []
            else:
                return []

        affected_personas = parse_array(row[22])
        dependencies = parse_array(row[23])
        risks = parse_array(row[24])

        return ProductRecommendation(
            id=UUID(row[0]),
            feedback_cluster_id=UUID(row[1]),
            created_by=UUID(row[2]),
            updated_by=UUID(row[3]),
            version=row[4],
            title=row[5],
            aggregate_impact_score=row[10],
            aggregate_priority_score=row[11],
            requesting_customer_count=row[8],
            total_feedback_items=row[9],
            business_justification=row[12],
            market_opportunity=row[13],
            revenue_impact_potential=row[14],
            competitive_positioning=row[15],
            recommendation=row[16].upper() if isinstance(row[16], str) else row[16],  # Normalize back to uppercase
            recommendation_reasoning=row[17],
            suggested_release=ReleaseTarget(row[19]),
            release_reasoning=row[20],
            estimated_effort=row[21],
            affected_personas=affected_personas,
            dependencies=dependencies,
            risks=risks,
            business_score=0,  # Not stored in database, calculated on demand
            confidence=float(row[18]),
            created_at=row[29],
            updated_at=row[30],
        )
