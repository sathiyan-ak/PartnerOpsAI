"""Design Partner repository implementation (PostgreSQL)."""

from uuid import UUID

import psycopg2

from backend.application.repositories import DesignPartnerRepository
from backend.domain import DesignPartner, DesignPartnerStatus


class DesignPartnerRepositoryImpl(DesignPartnerRepository):
    """PostgreSQL implementation of DesignPartnerRepository."""

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

    def save(self, design_partner: DesignPartner) -> UUID:
        """Save or update design partner. Returns ID."""
        conn = self._connect()
        cursor = conn.cursor()

        try:
            # Always upsert
            sql = """
                INSERT INTO design_partners (
                    id, opportunity_id, created_by, updated_by, version,
                    converted_at, converted_by, company_name, product_owner_name,
                    product_owner_email, technical_contact_name,
                    technical_contact_email, onboarding_status,
                    partnership_notes, success_criteria, created_at, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    opportunity_id=EXCLUDED.opportunity_id,
                    updated_by=EXCLUDED.updated_by,
                    version=design_partners.version + 1,
                    converted_at=EXCLUDED.converted_at,
                    converted_by=EXCLUDED.converted_by,
                    company_name=EXCLUDED.company_name,
                    product_owner_name=EXCLUDED.product_owner_name,
                    product_owner_email=EXCLUDED.product_owner_email,
                    technical_contact_name=EXCLUDED.technical_contact_name,
                    technical_contact_email=EXCLUDED.technical_contact_email,
                    onboarding_status=EXCLUDED.onboarding_status,
                    partnership_notes=EXCLUDED.partnership_notes,
                    success_criteria=EXCLUDED.success_criteria,
                    updated_at=EXCLUDED.updated_at
            """
            cursor.execute(
                sql,
                (
                    str(design_partner.id),
                    str(design_partner.opportunity_id),
                    str(design_partner.created_by),
                    str(design_partner.updated_by),
                    design_partner.version,
                    design_partner.converted_at,
                    (
                        str(design_partner.converted_by)
                        if design_partner.converted_by
                        else None
                    ),
                    design_partner.company_name,
                    design_partner.product_owner_name,
                    design_partner.product_owner_email,
                    design_partner.technical_contact_name,
                    design_partner.technical_contact_email,
                    design_partner.onboarding_status.value,
                    design_partner.partnership_notes,
                    design_partner.success_criteria,
                    design_partner.created_at,
                    design_partner.updated_at,
                ),
            )
            conn.commit()
            return design_partner.id
        except psycopg2.Error as e:
            conn.rollback()
            raise RuntimeError(
                f"Database constraint violation: {str(e).split(chr(10))[0]}"
            ) from e
        finally:
            cursor.close()
            conn.close()

    def find_by_id(self, design_partner_id: UUID) -> DesignPartner | None:
        """Find design partner by ID."""
        conn = self._connect()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT * FROM design_partners WHERE id = %s",
                (str(design_partner_id),),
            )
            row = cursor.fetchone()
            return self._row_to_design_partner(row) if row else None
        finally:
            cursor.close()
            conn.close()

    def find_by_opportunity_id(self, opportunity_id: UUID) -> DesignPartner | None:
        """Find design partner by opportunity ID."""
        conn = self._connect()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT * FROM design_partners WHERE opportunity_id = %s LIMIT 1",
                (str(opportunity_id),),
            )
            row = cursor.fetchone()
            return self._row_to_design_partner(row) if row else None
        finally:
            cursor.close()
            conn.close()

    def list_all(self, limit: int = 100, offset: int = 0) -> list[DesignPartner]:
        """List all design partners."""
        conn = self._connect()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT * FROM design_partners LIMIT %s OFFSET %s",
                (limit, offset),
            )
            rows = cursor.fetchall()
            return [self._row_to_design_partner(row) for row in rows]
        finally:
            cursor.close()
            conn.close()

    def _row_to_design_partner(self, row) -> DesignPartner:
        """Convert database row to DesignPartner domain object."""
        # Column order from schema: id(0), opportunity_id(1), created_by(2), updated_by(3), version(4),
        # converted_at(5), converted_by(6), company_name(7), product_owner_name(8), product_owner_email(9),
        # technical_contact_name(10), technical_contact_email(11), onboarding_status(12), ...,
        # partnership_notes(27), success_criteria(28), created_at(29), updated_at(30)
        return DesignPartner(
            id=UUID(row[0]),
            opportunity_id=UUID(row[1]),
            created_by=UUID(row[2]),
            updated_by=UUID(row[3]),
            version=row[4],
            converted_at=row[5],
            converted_by=UUID(row[6]) if row[6] else None,
            company_name=row[7],
            product_owner_name=row[8],
            product_owner_email=row[9],
            technical_contact_name=row[10],
            technical_contact_email=row[11],
            onboarding_status=DesignPartnerStatus(row[12]),
            partnership_notes=row[27],
            success_criteria=row[28],
            created_at=row[29],
            updated_at=row[30],
        )
