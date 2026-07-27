"""Pytest configuration and fixtures for integration testing."""

import os
import subprocess
from datetime import datetime, timezone
from uuid import uuid4
import pytest
from typing import Generator

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import json


@pytest.fixture(scope="session")
def database_url() -> str:
    """Get test database URL from environment."""
    url = os.getenv(
        "DATABASE_URL",
        "postgresql://test_user:test_password@localhost:5432/partneropsa_test",
    )
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
def test_user_id(postgres_connection) -> str:
    """Create and return a test user UUID. DEPENDENCY: First fixture to run."""
    user_id = str(uuid4())
    cursor = postgres_connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (id, email) VALUES (%s, %s) ON CONFLICT (id) DO NOTHING",
            (user_id, f"{user_id}@test.local"),
        )
        postgres_connection.commit()
    except Exception as e:
        postgres_connection.rollback()
        raise e
    finally:
        cursor.close()
    return user_id


@pytest.fixture
def test_opportunity_id(postgres_connection, test_user_id: str) -> str:
    """Create and persist opportunity. DEPENDENCY: Requires test_user_id."""
    opp_id = str(uuid4())
    cursor = postgres_connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO opportunities (
                id, created_by, updated_by, version, company_name,
                company_size_employees, industry, location, status,
                icp_alignment, icp_score, ai_maturity, security_maturity,
                design_partner_potential, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            opp_id, test_user_id, test_user_id, 0,
            f"Test Company {uuid4()}",
            50, "Technology", "San Francisco", "prospect",
            "weak", 50, "none", "none",
            0, datetime.now(timezone.utc), datetime.now(timezone.utc)
        ))
        postgres_connection.commit()
    except Exception as e:
        postgres_connection.rollback()
        raise e
    finally:
        cursor.close()
    return opp_id


@pytest.fixture
def test_design_partner_id(postgres_connection, test_user_id: str, test_opportunity_id: str) -> str:
    """Create and persist design partner. DEPENDENCY: Requires test_user_id + test_opportunity_id."""
    dp_id = str(uuid4())
    cursor = postgres_connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO design_partners (
                id, opportunity_id, created_by, updated_by, version,
                company_name, product_owner_name, product_owner_email,
                converted_at, converted_by, onboarding_status, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            dp_id, test_opportunity_id, test_user_id, test_user_id, 0,
            f"Test Partner {uuid4()}", "Jane Doe", "jane@test.local",
            datetime.now(timezone.utc), test_user_id, "onboarding",
            datetime.now(timezone.utc), datetime.now(timezone.utc)
        ))
        postgres_connection.commit()
    except Exception as e:
        postgres_connection.rollback()
        raise e
    finally:
        cursor.close()
    return dp_id


@pytest.fixture
def test_opportunity_data(test_user_id: str) -> dict:
    """Fixture: minimal opportunity data dict for manual inserts."""
    now = datetime.now(timezone.utc)
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
        "icp_alignment": "weak",
        "icp_score": 50,
        "ai_maturity": "none",
        "security_maturity": "none",
        "design_partner_potential": 0,
        "created_at": now,
        "updated_at": now,
    }


@pytest.fixture
def test_design_partner_data(test_user_id: str, test_opportunity_id: str) -> dict:
    """Fixture: minimal design partner data dict for manual inserts."""
    now = datetime.now(timezone.utc)
    return {
        "id": str(uuid4()),
        "opportunity_id": test_opportunity_id,
        "created_by": test_user_id,
        "updated_by": test_user_id,
        "version": 0,
        "company_name": f"Test Partner {uuid4()}",
        "product_owner_name": "Jane Doe",
        "product_owner_email": "jane@test.local",
        "converted_at": now,
        "converted_by": test_user_id,
        "onboarding_status": "onboarding",
        "created_at": now,
        "updated_at": now,
    }


@pytest.fixture
def test_feedback_data(test_user_id: str, test_design_partner_id: str) -> dict:
    """Fixture: feedback data. DEPENDENCY: Requires test_design_partner_id."""
    now = datetime.now(timezone.utc)
    return {
        "id": str(uuid4()),
        "design_partner_id": test_design_partner_id,
        "created_by": test_user_id,
        "updated_by": test_user_id,
        "version": 0,
        "customer_name": "John Smith",
        "customer_email": "john@customer.local",
        "customer_company": "ACME Corp",
        "category": "feature_request",
        "category_confidence": 0.95,
        "title": "Test Feedback",
        "description": "This is test feedback",
        "impact_score": 8,
        "priority_score": 7,
        "confidence": 0.85,
        "similar_feedback_ids": [],
        "status": "open",
        "created_at": now,
        "updated_at": now,
    }


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "integration: integration tests (require database)"
    )
    config.addinivalue_line("markers", "unit: unit tests")
    config.addinivalue_line("markers", "repository: repository tests")
    config.addinivalue_line("markers", "rls: RLS policy tests")


@pytest.fixture(autouse=True)
def reset_db_between_tests(postgres_connection):
    """Clean up test data after each test."""
    yield
    cursor = postgres_connection.cursor()
    try:
        # TRUNCATE CASCADE to delete in dependency order and reset sequences
        cursor.execute("TRUNCATE TABLE security_audit_records CASCADE")
        cursor.execute("TRUNCATE TABLE policy_decisions CASCADE")
        cursor.execute("TRUNCATE TABLE product_recommendations CASCADE")
        cursor.execute("TRUNCATE TABLE feedback_clusters CASCADE")
        cursor.execute("TRUNCATE TABLE design_feedback CASCADE")
        cursor.execute("TRUNCATE TABLE design_partners CASCADE")
        cursor.execute("TRUNCATE TABLE opportunities CASCADE")
        # Users should persist for the test_user_id fixture
        postgres_connection.commit()
    except Exception as e:
        postgres_connection.rollback()
        raise
    finally:
        cursor.close()
