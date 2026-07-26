"""Pytest configuration and fixtures for integration testing."""

import os
import subprocess
from uuid import uuid4
import pytest
from typing import Generator

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


@pytest.fixture(scope="session")
def database_url() -> str:
    """Get test database URL from environment."""
    url = os.getenv("DATABASE_URL", "postgresql://test_user:test_password@localhost:5432/partneropsa_test")
    return url


@pytest.fixture(scope="session")
def postgres_connection(database_url: str):
    """Connect to PostgreSQL test database."""
    try:
        conn = psycopg2.connect(database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        yield conn
        conn.close()
    except psycopg2.OperationalError as e:
        pytest.skip(f"PostgreSQL not available: {e}")


@pytest.fixture(scope="session", autouse=True)
def setup_database(postgres_connection):
    """Initialize database schema from migrations."""
    cursor = postgres_connection.cursor()

    # Check if tables exist
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables WHERE table_name = 'opportunities'
        )
    """)
    tables_exist = cursor.fetchone()[0]

    if not tables_exist:
        # Run migration
        migration_path = "backend/infrastructure/migrations/001_init_schema.sql"
        if os.path.exists(migration_path):
            with open(migration_path, "r") as f:
                sql = f.read()
                try:
                    cursor.execute(sql)
                    cursor.close()
                    print("✓ Database schema initialized")
                except psycopg2.Error as e:
                    print(f"✗ Migration failed: {e}")
                    cursor.close()
                    raise
        else:
            print(f"✗ Migration file not found: {migration_path}")
    else:
        print("✓ Database tables already exist")

    cursor.close()
    yield


@pytest.fixture
def test_user_id() -> str:
    """Generate a test user UUID."""
    return str(uuid4())


@pytest.fixture
def test_opportunity_data(test_user_id: str) -> dict:
    """Fixture: minimal opportunity data for testing."""
    return {
        "id": str(uuid4()),
        "created_by": test_user_id,
        "updated_by": test_user_id,
        "version": 0,
        "company_name": f"Test Company {uuid4()}",
        "company_size_employees": 50,
        "industry": "Technology",
        "location": "San Francisco",
        "status": "prospect",
        "icp_score": 50,
    }


@pytest.fixture
def test_design_partner_data(test_user_id: str, test_opportunity_data: dict) -> dict:
    """Fixture: minimal design partner data for testing."""
    return {
        "id": str(uuid4()),
        "opportunity_id": test_opportunity_data["id"],
        "created_by": test_user_id,
        "updated_by": test_user_id,
        "version": 0,
        "company_name": test_opportunity_data["company_name"],
        "product_owner_name": "Jane Doe",
        "product_owner_email": "jane@test.local",
        "converted_at": "2025-01-01T00:00:00Z",
        "converted_by": test_user_id,
        "onboarding_status": "onboarding",
    }


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "integration: integration tests (require database)")
    config.addinivalue_line("markers", "unit: unit tests")
    config.addinivalue_line("markers", "repository: repository tests")
    config.addinivalue_line("markers", "rls: RLS policy tests")


@pytest.fixture(autouse=True)
def reset_db_between_tests(postgres_connection):
    """Clean up test data after each test."""
    yield
    # In production, you'd truncate tables here
    # For now, we just yield
