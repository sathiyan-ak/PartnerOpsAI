#!/bin/bash
# PartnerOpsAI Production Startup Script

set -e

# Configuration
DATABASE_URL="${DATABASE_URL:-postgresql://test_user:test_password@localhost:5432/partneropsa_test}"
SERVER_HOST="${SERVER_HOST:-0.0.0.0}"
SERVER_PORT="${SERVER_PORT:-8000}"
ENVIRONMENT="${ENVIRONMENT:-development}"

echo "═══════════════════════════════════════════════════════"
echo "PartnerOpsAI Startup"
echo "═══════════════════════════════════════════════════════"
echo "Environment: $ENVIRONMENT"
echo "Database: $DATABASE_URL"
echo "Server: $SERVER_HOST:$SERVER_PORT"
echo ""

# Wait for database to be ready (if in Docker Compose)
echo "Waiting for database..."
max_attempts=30
attempt=1
while [ $attempt -le $max_attempts ]; do
    if python -c "import psycopg2; psycopg2.connect('$DATABASE_URL')" 2>/dev/null; then
        echo "✓ Database is ready"
        break
    fi
    echo "  Attempt $attempt/$max_attempts..."
    sleep 1
    attempt=$((attempt + 1))
done

if [ $attempt -gt $max_attempts ]; then
    echo "✗ Database failed to start"
    exit 1
fi

# Apply migrations
echo ""
echo "Applying database migrations..."
python -c "
import os
import psycopg2

db_url = os.getenv('DATABASE_URL')
conn = psycopg2.connect(db_url)
cursor = conn.cursor()

# Read migration file
with open('backend/infrastructure/migrations/001_init_schema.sql', 'r') as f:
    schema = f.read()

# Execute schema
cursor.execute(schema)
conn.commit()
cursor.close()
conn.close()

print('✓ Database schema initialized')
"

# Initialize demo user
echo ""
echo "Initializing demo user..."
python -c "
import os
import psycopg2
from uuid import UUID

db_url = os.getenv('DATABASE_URL')
actor_id = '00000000-0000-0000-0000-000000000001'

conn = psycopg2.connect(db_url)
cursor = conn.cursor()

cursor.execute(
    'INSERT INTO users (id, email) VALUES (%s, %s) ON CONFLICT (id) DO NOTHING',
    (actor_id, 'demo@partneropsa.com')
)
conn.commit()
cursor.close()
conn.close()

print('✓ Demo user initialized')
"

# Start FastAPI server
echo ""
echo "═══════════════════════════════════════════════════════"
echo "Starting FastAPI server..."
echo "═══════════════════════════════════════════════════════"
echo ""
echo "Endpoints:"
echo "  API:     http://$SERVER_HOST:$SERVER_PORT/docs"
echo "  Status:  http://$SERVER_HOST:$SERVER_PORT/health"
echo "  Swagger: http://$SERVER_HOST:$SERVER_PORT/docs"
echo ""

# Use PORT env var if set (Railway, Fly.io, Cloud Run)
if [ -z "$PORT" ]; then
    PORT="$SERVER_PORT"
fi

exec python -m uvicorn backend.main:app \
    --host "$SERVER_HOST" \
    --port "$PORT" \
    --log-level info
