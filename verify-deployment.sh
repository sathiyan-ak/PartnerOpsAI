#!/bin/bash
# PartnerOpsAI Deployment Verification Script

set -e

BASE_URL="${1:-http://localhost:8000}"

echo "═══════════════════════════════════════════════════════"
echo "PartnerOpsAI Deployment Verification"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "Target URL: $BASE_URL"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASSED=0
FAILED=0

# Test function
test_endpoint() {
    local method=$1
    local endpoint=$2
    local expected_code=$3
    local description=$4

    echo -n "Testing $description... "

    response=$(curl -s -w "\n%{http_code}" -X "$method" "$BASE_URL$endpoint" 2>/dev/null || echo "error")
    http_code=$(echo "$response" | tail -1)

    if [ "$http_code" = "$expected_code" ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $http_code)"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}✗ FAIL${NC} (Expected $expected_code, got $http_code)"
        FAILED=$((FAILED + 1))
    fi
}

# Test function with JSON validation
test_json_endpoint() {
    local method=$1
    local endpoint=$2
    local description=$3
    local key=$4

    echo -n "Testing $description... "

    response=$(curl -s -X "$method" "$BASE_URL$endpoint" 2>/dev/null || echo "{}")

    if echo "$response" | grep -q "$key"; then
        echo -e "${GREEN}✓ PASS${NC}"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}✗ FAIL${NC} (Missing '$key' in response)"
        FAILED=$((FAILED + 1))
    fi
}

echo "1. Basic Connectivity"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
test_endpoint "GET" "/health" "200" "GET /health"

echo ""
echo "2. API Documentation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
test_endpoint "GET" "/docs" "200" "GET /docs (Swagger UI)"
test_endpoint "GET" "/openapi.json" "200" "GET /openapi.json (OpenAPI spec)"

echo ""
echo "3. Service Information"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
test_json_endpoint "GET" "/api/status" "GET /api/status" "service"
test_json_endpoint "GET" "/" "GET / (landing page)" "PartnerOpsAI"

echo ""
echo "4. Qualification Endpoint"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
test_endpoint "POST" "/api/qualify" "200" "POST /api/qualify (valid request)"

echo ""
echo "5. Demo Data Management"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
test_endpoint "POST" "/api/seed-demo-data" "200" "POST /api/seed-demo-data"

echo ""
echo "6. Data Retrieval"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -n "Checking for demo opportunities... "
opportunities=$(curl -s "$BASE_URL/api/opportunities/00000000-0000-0000-0000-000000000002" 2>/dev/null | grep -c "opportunity_id" || echo "0")
if [ "$opportunities" -gt "0" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${YELLOW}⚠ WARN${NC} (No demo data yet — run /api/seed-demo-data first)"
fi

echo ""
echo "═══════════════════════════════════════════════════════"
echo "Results: ${GREEN}$PASSED passed${NC}, ${RED}$FAILED failed${NC}"
echo "═══════════════════════════════════════════════════════"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Load demo data:"
    echo "     curl -X POST $BASE_URL/api/seed-demo-data"
    echo ""
    echo "  2. Try the API:"
    echo "     curl $BASE_URL/docs"
    echo ""
    echo "  3. Share the URL:"
    echo "     $BASE_URL"
    exit 0
else
    echo -e "\n${RED}✗ Some checks failed.${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  - Is the server running? (check Docker/startup logs)"
    echo "  - Is the database connected? (check DATABASE_URL)"
    echo "  - Is the correct URL? (check BASE_URL: $BASE_URL)"
    exit 1
fi
