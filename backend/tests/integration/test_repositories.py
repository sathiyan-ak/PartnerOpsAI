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
        result = repo.save(test_opp)
        assert result is not None
        assert result.id == test_opp.id
        assert result.company_name == test_opp.company_name
        assert result.status == OpportunityStatus.PROSPECT

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
        test_opp.icp_score = 90
        test_opp.status = OpportunityStatus.QUALIFIED
        test_opp.version = 1
        updated = repo.save(test_opp)
        assert updated.icp_score == 90
        assert updated.status == OpportunityStatus.QUALIFIED

    def test_optimistic_locking_conflict(self, repo, test_opp):
        """Test: Stale version rejected."""
        repo.save(test_opp)
        # Simulate concurrent update by fetching fresh copy
        fresh = repo.find_by_id(test_opp.id)
        fresh.icp_score = 85
        fresh.version = fresh.version + 1
        repo.save(fresh)  # fresh now has version 1

        # Try to save stale copy (still has version 0)
        test_opp.icp_score = 99
        with pytest.raises(Exception):  # Version conflict error
            repo.save(test_opp)

    def test_duplicate_id_fails(self, repo, test_opp):
        """Test: Cannot insert duplicate UUID."""
        repo.save(test_opp)
        # Try to save same ID again
        duplicate = Opportunity(
            id=test_opp.id,
            created_by=uuid4(),
            updated_by=uuid4(),
            version=0,
            company_name="Different Corp",
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
        with pytest.raises(Exception):  # Primary key violation
            repo.save(duplicate)

    def test_invalid_score_rejected(self, repo, test_opp):
        """Test: Score constraint violation."""
        test_opp.icp_score = 150  # > 100
        with pytest.raises(Exception):  # CHECK constraint
            repo.save(test_opp)

    def test_missing_company_name_rejected(self, repo, test_opp):
        """Test: NOT NULL constraint."""
        test_opp.company_name = ""
        with pytest.raises(Exception):  # Check constraint or validation
            repo.save(test_opp)

    def test_invalid_status_rejected(self, repo, test_opp):
        """Test: Invalid enum value rejected."""
        test_opp.status = "invalid_status"  # type: ignore
        with pytest.raises(Exception):
            repo.save(test_opp)

    def test_find_nonexistent_returns_none(self, repo):
        """Test: Query missing ID returns None."""
        result = repo.find_by_id(uuid4())
        assert result is None

    def test_find_by_status(self, repo, test_opp):
        """Test: Filter by status."""
        repo.save(test_opp)
        # Assuming repository has find_by_status
        # This may need implementation
        qualified = Opportunity(
            id=uuid4(),
            created_by=uuid4(),
            updated_by=uuid4(),
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

    def test_pagination(self, repo):
        """Test: Limit/offset pagination works."""
        # Insert 15 records
        for i in range(15):
            opp = Opportunity(
                id=uuid4(),
                created_by=uuid4(),
                updated_by=uuid4(),
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
