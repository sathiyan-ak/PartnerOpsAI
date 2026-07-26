"""Mapper: Convert between domain models and database records."""

from typing import Dict, Any
from backend.domain import (
    Opportunity, DesignPartner, DesignFeedback, FeedbackCluster,
    ProductRecommendation, PolicyDecision, SecurityAuditRecord,
)


class DomainMapper:
    """Converts domain models ↔ database dictionaries."""

    @staticmethod
    def opportunity_to_db(opp: Opportunity) -> Dict[str, Any]:
        """Domain → Database."""
        return {
            "id": str(opp.id),
            "created_by": str(opp.created_by),
            "updated_by": str(opp.updated_by),
            "version": opp.version,
            "company_name": opp.company_name,
            "company_size_employees": opp.company_size_employees,
            "industry": opp.industry,
            "location": opp.location,
            "website": opp.website,
            "status": opp.status.value,
            "icp_alignment": opp.icp_alignment.value,
            "icp_score": opp.icp_score,
            "ai_maturity": opp.ai_maturity.value,
            "ai_maturity_evidence": opp.ai_maturity_evidence,
            "ai_investment_usd": opp.ai_investment_usd,
            "security_maturity": opp.security_maturity.value,
            "security_certifications": opp.security_certifications,
            "compliance_needs": opp.compliance_needs,
            "design_partner_potential": opp.design_partner_potential,
            "has_product_team": opp.has_product_team,
            "product_owner_email": opp.product_owner_email,
            "technical_contact_email": opp.technical_contact_email,
            "executive_sponsor_email": opp.executive_sponsor_email,
            "qualification_evidence": opp.qualification_evidence,
            "strategic_alignment": opp.strategic_alignment,
            "notes": opp.notes,
            "source": opp.source,
        }

    @staticmethod
    def db_to_opportunity(data: Dict[str, Any]) -> Opportunity:
        """Database → Domain."""
        return Opportunity.from_dict(data)

    @staticmethod
    def design_partner_to_db(dp: DesignPartner) -> Dict[str, Any]:
        """Domain → Database."""
        return {
            "id": str(dp.id),
            "opportunity_id": str(dp.opportunity_id),
            "created_by": str(dp.created_by),
            "updated_by": str(dp.updated_by),
            "version": dp.version,
            "converted_at": dp.converted_at.isoformat(),
            "converted_by": str(dp.converted_by),
            "company_name": dp.company_name,
            "product_owner_name": dp.product_owner_name,
            "product_owner_email": dp.product_owner_email,
            "technical_contact_name": dp.technical_contact_name,
            "technical_contact_email": dp.technical_contact_email,
            "onboarding_status": dp.onboarding_status.value,
            "implementation_status": dp.implementation_status.value,
            "health": dp.health.value,
            "health_notes": dp.health_notes,
            "total_feedback_count": dp.total_feedback_count,
            "feedback_count_this_quarter": dp.feedback_count_this_quarter,
            "partnership_notes": dp.partnership_notes,
            "success_criteria": dp.success_criteria,
        }

    @staticmethod
    def db_to_design_partner(data: Dict[str, Any]) -> DesignPartner:
        """Database → Domain."""
        return DesignPartner.from_dict(data)

    @staticmethod
    def design_feedback_to_db(fb: DesignFeedback) -> Dict[str, Any]:
        """Domain → Database."""
        return {
            "id": str(fb.id),
            "design_partner_id": str(fb.design_partner_id),
            "created_by": str(fb.created_by),
            "updated_by": str(fb.updated_by),
            "version": fb.version,
            "customer_name": fb.customer_name,
            "customer_email": fb.customer_email,
            "customer_company": fb.customer_company,
            "category": fb.category.value,
            "category_confidence": float(fb.category_confidence),
            "title": fb.title,
            "description": fb.description,
            "impact_score": fb.impact_score,
            "priority_score": fb.priority_score,
            "confidence": float(fb.confidence),
            "similar_feedback_ids": [str(fid) for fid in fb.similar_feedback_ids],
            "similarity_explanation": fb.similarity_explanation,
            "suggested_release": fb.suggested_release.value,
            "release_reasoning": fb.release_reasoning,
            "product_decision_summary": fb.product_decision_summary,
            "decision_evidence": fb.decision_evidence,
            "affected_personas": fb.affected_personas,
            "status": fb.status.value,
        }

    @staticmethod
    def db_to_design_feedback(data: Dict[str, Any]) -> DesignFeedback:
        """Database → Domain."""
        return DesignFeedback.from_dict(data)

    @staticmethod
    def recommendation_to_db(rec: ProductRecommendation) -> Dict[str, Any]:
        """Domain → Database."""
        return {
            "id": str(rec.id),
            "feedback_cluster_id": str(rec.feedback_cluster_id),
            "created_by": str(rec.created_by),
            "updated_by": str(rec.updated_by),
            "version": rec.version,
            "title": rec.title,
            "description": rec.description,
            "category": rec.category,
            "requesting_customer_count": rec.requesting_customer_count,
            "total_feedback_items": rec.total_feedback_items,
            "aggregate_impact_score": rec.aggregate_impact_score,
            "aggregate_priority_score": rec.aggregate_priority_score,
            "business_justification": rec.business_justification,
            "market_opportunity": rec.market_opportunity,
            "revenue_impact_potential": rec.revenue_impact_potential,
            "competitive_positioning": rec.competitive_positioning,
            "recommendation": rec.recommendation,
            "recommendation_reasoning": rec.recommendation_reasoning,
            "confidence": float(rec.confidence),
            "suggested_release": rec.suggested_release.value,
            "release_reasoning": rec.release_reasoning,
            "estimated_effort": rec.estimated_effort,
            "affected_personas": rec.affected_personas,
            "dependencies": rec.dependencies,
            "risks": rec.risks,
            "decision_made": rec.decision_made,
            "decision_made_by": str(rec.decision_made_by) if rec.decision_made_by else None,
            "decision_notes": rec.decision_notes,
        }

    @staticmethod
    def db_to_recommendation(data: Dict[str, Any]) -> ProductRecommendation:
        """Database → Domain."""
        return ProductRecommendation.from_dict(data)

    @staticmethod
    def audit_to_db(record: SecurityAuditRecord) -> Dict[str, Any]:
        """Domain → Database."""
        return {
            "id": str(record.id),
            "version": record.version,
            "actor_id": str(record.actor_id),
            "actor_role": record.actor_role,
            "action": record.action.value,
            "resource_type": record.resource_type,
            "resource_id": str(record.resource_id),
            "policy_name": record.policy_name,
            "policy_version": record.policy_version,
            "policy_result": record.policy_result.value,
            "policy_evaluation_reasoning": record.policy_evaluation_reasoning,
            "request_id": record.request_id,
            "request_hash": record.request_hash,
            "record_hash": record.record_hash,
            "previous_hash": record.previous_hash,
            "ip_address": record.ip_address,
            "user_agent": record.user_agent,
            "context_data": record.context_data,
        }

    @staticmethod
    def db_to_audit(data: Dict[str, Any]) -> SecurityAuditRecord:
        """Database → Domain."""
        return SecurityAuditRecord.from_dict(data)
