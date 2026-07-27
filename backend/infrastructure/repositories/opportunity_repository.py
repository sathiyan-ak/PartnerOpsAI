"""Opportunity repository implementation (PostgreSQL)."""

from uuid import UUID

import psycopg2

from backend.application.repositories import OpportunityRepository
from backend.domain import ICPAlignment, MaturityLevel, Opportunity, OpportunityStatus


class OpportunityRepositoryImpl(OpportunityRepository):
    """PostgreSQL implementation of OpportunityRepository."""

    def __init__(self, db_url: str | None = None):
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

    def save(self, opportunity: Opportunity) -> UUID:
        """Save or update opportunity. Returns opportunity ID."""
        conn = self._connect()
        cursor = conn.cursor()

        try:
            # UPSERT: INSERT or UPDATE with optimistic locking
            sql = """
                INSERT INTO opportunities (
                    id, created_by, updated_by, version,
                    company_name, company_size_employees, industry, location,
                    status, icp_alignment, icp_score,
                    ai_maturity, security_maturity, design_partner_potential,
                    has_product_team, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    updated_by = EXCLUDED.updated_by,
                    version = opportunities.version + 1,
                    company_name = EXCLUDED.company_name,
                    company_size_employees = EXCLUDED.company_size_employees,
                    industry = EXCLUDED.industry,
                    location = EXCLUDED.location,
                    status = EXCLUDED.status,
                    icp_alignment = EXCLUDED.icp_alignment,
                    icp_score = EXCLUDED.icp_score,
                    ai_maturity = EXCLUDED.ai_maturity,
                    security_maturity = EXCLUDED.security_maturity,
                    design_partner_potential = EXCLUDED.design_partner_potential,
                    has_product_team = EXCLUDED.has_product_team,
                    updated_at = EXCLUDED.updated_at
                WHERE opportunities.version = %s
            """
            values = (
                str(opportunity.id),
                str(opportunity.created_by),
                str(opportunity.updated_by),
                opportunity.version,
                opportunity.company_name,
                opportunity.company_size_employees,
                opportunity.industry,
                opportunity.location,
                opportunity.status.value,
                opportunity.icp_alignment.value,
                opportunity.icp_score,
                opportunity.ai_maturity.value,
                opportunity.security_maturity.value,
                opportunity.design_partner_potential,
                opportunity.has_product_team,
                opportunity.created_at,
                opportunity.updated_at,
                opportunity.version,
            )

            cursor.execute(sql, values)

            # Check if update/insert actually happened
            if cursor.rowcount == 0:
                # No rows affected = version conflict
                raise RuntimeError(
                    f"Optimistic locking conflict: version {opportunity.version} is stale or record doesn't exist"
                )

            conn.commit()
            return opportunity.id

        except psycopg2.IntegrityError as e:
            conn.rollback()
            raise RuntimeError(f"Database constraint violation: {e}")
        except psycopg2.Error as e:
            conn.rollback()
            raise RuntimeError(f"Database error: {e}")
        finally:
            cursor.close()
            conn.close()

    def find_by_id(self, opportunity_id: UUID) -> Opportunity | None:
        """Find opportunity by ID."""
        conn = self._connect()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM opportunities WHERE id = %s", (str(opportunity_id),))
            row = cursor.fetchone()

            if not row:
                return None

            return self._row_to_opportunity(row, cursor.description)

        finally:
            cursor.close()
            conn.close()

    def find_by_company_name(self, company_name: str) -> Opportunity | None:
        """Find opportunity by company name."""
        conn = self._connect()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT * FROM opportunities WHERE company_name = %s LIMIT 1",
                (company_name,),
            )
            row = cursor.fetchone()

            if not row:
                return None

            return self._row_to_opportunity(row, cursor.description)

        finally:
            cursor.close()
            conn.close()

    def list_all(self, limit: int = 100, offset: int = 0) -> list[Opportunity]:
        """List all opportunities with pagination."""
        conn = self._connect()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT * FROM opportunities ORDER BY created_at DESC LIMIT %s OFFSET %s",
                (limit, offset),
            )
            rows = cursor.fetchall()

            return [self._row_to_opportunity(row, cursor.description) for row in rows]

        finally:
            cursor.close()
            conn.close()

    def _row_to_opportunity(self, row, description):
        """Convert database row to Opportunity domain object."""
        columns = {d[0]: i for i, d in enumerate(description)}

        return Opportunity(
            id=UUID(row[columns["id"]]),
            created_by=UUID(row[columns["created_by"]]),
            updated_by=UUID(row[columns["updated_by"]]),
            version=row[columns["version"]],
            company_name=row[columns["company_name"]],
            company_size_employees=row[columns["company_size_employees"]],
            industry=row[columns["industry"]],
            location=row[columns["location"]],
            status=OpportunityStatus(row[columns["status"]]),
            icp_alignment=ICPAlignment(row[columns["icp_alignment"]]),
            icp_score=row[columns["icp_score"]],
            ai_maturity=MaturityLevel(row[columns["ai_maturity"]]),
            security_maturity=MaturityLevel(row[columns["security_maturity"]]),
            design_partner_potential=row[columns["design_partner_potential"]],
            has_product_team=row[columns["has_product_team"]],
            created_at=row[columns["created_at"]],
            updated_at=row[columns["updated_at"]],
        )
