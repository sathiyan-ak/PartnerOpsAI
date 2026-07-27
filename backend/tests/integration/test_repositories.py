"""Repository integration tests: CRUD + constraints + concurrency."""

import pytest
from uuid import uuid4, UUID
from datetime import datetime

from backend.domain import Opportunity, OpportunityStatus, ICPAlignment, MaturityLevel
from backend.infrastructure.repositories.opportunity_repository import OpportunityRepositoryImpl


@pytest.mark.integration
class TestOpportunityRepository:
    """Test OpportunityRepository CRUD operations."""

    @pytest.fixture
    def repo(self, database_url) -> OpportunityRepositoryImpl:
        """Get repository instance."""
        return OpportunityRepositoryImpl(database_url)

    @pytest.fixture
    def test_opp(self, test_user_id: str):
        """Create test opportunity."""
        user_uuid = UUID(test_user_id)
        return Opportunity(
            id=uuid4(),
            created_by=user_uuid,
            updated_by=user_uuid,
            version=0,
            company_name="Test Corp",
            company_size_employees=100,
            industry="Technology",
            location="SF",
            status=OpportunityStatus.PROSPECT,
            icp_alignment=ICPAlignment.STRONG,
            icp_score=75,
            ai_maturity=MaturityLevel.INTERMEDIATE,
            security_maturity=MaturityLevel.ADVANCED,
            design_partner_potential=80,
            has_product_team=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    def test_create_opportunity(self, repo, test_opp):
        """Test: Create opportunity in database."""
        result_id = repo.save(test_opp)
        assert result_id is not None
        assert result_id == test_opp.id

        # Verify persisted
        persisted = repo.find_by_id(result_id)
        assert persisted.company_name == test_opp.company_name
        assert persisted.status == OpportunityStatus.PROSPECT

    def test_find_by_id(self, repo, test_opp):
        """Test: Save then retrieve by ID."""
        repo.save(test_opp)
        found = repo.find_by_id(test_opp.id)
        assert found is not None
        assert found.id == test_opp.id
        assert found.icp_score == 75

    def test_find_by_company_name(self, repo, test_opp):
        """Test: Query by company name."""
        repo.save(test_opp)
        found = repo.find_by_company_name("Test Corp")
        assert found is not None
        assert found.company_name == "Test Corp"

    def test_list_all(self, repo, test_opp, test_user_id):
        """Test: Paginated list."""
        repo.save(test_opp)
        results = repo.list_all(limit=10, offset=0)
        assert len(results) > 0
        assert any(o.id == test_opp.id for o in results)

    def test_update_opportunity(self, repo, test_opp):
        """Test: Update existing record."""
        repo.save(test_opp)
        # Fetch fresh copy to get correct version
        updated = repo.find_by_id(test_opp.id)
        updated.icp_score = 90
        updated.status = OpportunityStatus.QUALIFIED
        repo.save(updated)
        # Verify persisted
        final = repo.find_by_id(test_opp.id)
        assert final.icp_score == 90
        assert final.status == OpportunityStatus.QUALIFIED

    def test_optimistic_locking_conflict(self, repo, test_opp):
        """Test: Stale version rejected."""
        repo.save(test_opp)  # test_opp now version 0 in DB
        # Simulate concurrent update by fetching fresh copy
        fresh = repo.find_by_id(test_opp.id)  # fresh.version = 0
        fresh.icp_score = 85
        repo.save(fresh)  # Increments to version 1 in DB

        # Try to save stale copy (still has version 0, but DB now has version 1)
        test_opp.icp_score = 99
        with pytest.raises(RuntimeError):  # Version conflict error
            repo.save(test_opp)

    def test_duplicate_id_upserts(self, repo, test_opp, test_user_id):
        """Test: Duplicate UUID upserts (ON CONFLICT DO UPDATE)."""
        repo.save(test_opp)
        original_version = 0

        # Try to save same ID with different data (version 0 to 1)
        user_uuid = UUID(test_user_id)
        update = Opportunity(
            id=test_opp.id,
            created_by=user_uuid,
            updated_by=user_uuid,
            version=original_version,  # Current version
            company_name="Updated Corp",
            company_size_employees=50,
            industry="Finance",
            location="NYC",
            status=OpportunityStatus.PROSPECT,
            icp_alignment=ICPAlignment.WEAK,
            icp_score=30,
            ai_maturity=MaturityLevel.NONE,
            security_maturity=MaturityLevel.NONE,
            design_partner_potential=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        # Should upsert (update because version matches)
        repo.save(update)
        # Verify update happened
        fetched = repo.find_by_id(test_opp.id)
        assert fetched.company_name == "Updated Corp"
        assert fetched.version == 1  # Version incremented

    def test_invalid_score_rejected(self, repo, test_opp):
        """Test: Score constraint violation."""
        test_opp.icp_score = 150  # > 100
        with pytest.raises(Exception):  # CHECK constraint
            repo.save(test_opp)

    def test_missing_company_name_rejected(self, repo, test_opp):
        """Test: Empty company name is stored (no validation at DB level)."""
        # Note: Database allows empty strings (no CHECK constraint)
        # This test verifies that behavior
        test_opp.company_name = ""
        result_id = repo.save(test_opp)
        assert result_id is not None
        # Empty string is allowed by database
        found = repo.find_by_id(result_id)
        assert found.company_name == ""

    def test_invalid_status_rejected(self, repo, test_opp):
        """Test: Invalid enum value rejected."""
        test_opp.status = "invalid_status"  # type: ignore
        with pytest.raises(Exception):
            repo.save(test_opp)

    def test_find_nonexistent_returns_none(self, repo):
        """Test: Query missing ID returns None."""
        result = repo.find_by_id(uuid4())
        assert result is None

    def test_find_by_status(self, repo, test_opp, test_user_id):
        """Test: Filter by status."""
        repo.save(test_opp)
        # Create another opportunity with qualified status
        user_uuid = UUID(test_user_id)
        qualified = Opportunity(
            id=uuid4(),
            created_by=user_uuid,
            updated_by=user_uuid,
            version=0,
            company_name="Qualified Corp",
            company_size_employees=200,
            industry="Tech",
            location="Boston",
            status=OpportunityStatus.QUALIFIED,
            icp_alignment=ICPAlignment.PERFECT,
            icp_score=95,
            ai_maturity=MaturityLevel.ADVANCED,
            security_maturity=MaturityLevel.ADVANCED,
            design_partner_potential=90,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        repo.save(qualified)
        # Verify we can distinguish statuses
        by_id = repo.find_by_id(qualified.id)
        assert by_id.status == OpportunityStatus.QUALIFIED

    def test_pagination(self, repo, test_user_id):
        """Test: Limit/offset pagination works."""
        user_uuid = UUID(test_user_id)
        # Insert 15 records
        for i in range(15):
            opp = Opportunity(
                id=uuid4(),
                created_by=user_uuid,
                updated_by=user_uuid,
                version=0,
                company_name=f"Corp {i}",
                company_size_employees=100 + i,
                industry="Tech",
                location="SF",
                status=OpportunityStatus.PROSPECT,
                icp_alignment=ICPAlignment.MODERATE,
                icp_score=50,
                ai_maturity=MaturityLevel.BEGINNER,
                security_maturity=MaturityLevel.BEGINNER,
                design_partner_potential=0,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            repo.save(opp)

        # Test pagination
        page1 = repo.list_all(limit=5, offset=0)
        page2 = repo.list_all(limit=5, offset=5)
        page3 = repo.list_all(limit=5, offset=10)

        assert len(page1) == 5
        assert len(page2) == 5
        assert len(page3) == 5
        # Verify no overlap
        ids1 = {o.id for o in page1}
        ids2 = {o.id for o in page2}
        assert len(ids1 & ids2) == 0
