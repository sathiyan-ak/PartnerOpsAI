"""Database connection and client for Supabase."""

import os
from typing import Optional

try:
    from supabase import Client, create_client
except ImportError:
    # Supabase optional for local testing
    Client = None
    create_client = None


class DatabaseClient:
    """Singleton Supabase client."""

    _instance: Optional["DatabaseClient"] = None
    _client: Client | None = None

    def __new__(cls) -> "DatabaseClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize database connection."""
        if self._client is None:
            self._client = self._create_client()

    @staticmethod
    def _create_client() -> Client | None:
        """Create Supabase client from environment variables."""
        if create_client is None:
            return None

        url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Use service role for backend

        if not url or not key:
            return None

        return create_client(url, key)

    @property
    def client(self) -> Client:
        """Get Supabase client."""
        if self._client is None:
            self._client = self._create_client()
        return self._client

    def get_table(self, table_name: str):
        """Get table reference."""
        return self.client.table(table_name)

    def execute_query(self, query: str):
        """Execute raw SQL query."""
        return self.client.postgrest.request(
            "GET", "/rpc/execute_query", json={"query": query}
        )


# Singleton instance
db = DatabaseClient()
