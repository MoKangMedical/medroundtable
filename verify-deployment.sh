#!/bin/bash
# MedRoundTable Deployment Verification Script
# Usage: ./verify-deployment.sh

echo "🔍 MedRoundTable Deployment Verification"
echo "========================================"
echo ""

BACKEND_URL="https://medroundtable.zeabur.app"
FRONTEND_URL="https://medroundtable-v2.vercel.app"
ERRORS=0

check_endpoint() {
    local url=$1
    local name=$2
    local expected_code=${3:-200}
    
    echo -n "Checking $name... "
    
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
    
    if [ "$RESPONSE" = "$expected_code" ]; then
        echo -e "\033[0;32m✅ OK ($RESPONSE)\033[0m"
        return 0
    else
        echo -e "\033[0;31m❌ FAILED ($RESPONSE)\033[0m"
        return 1
    fi
}

echo "📋 Checking Backend Endpoints"
echo "------------------------------"

check_endpoint "$BACKEND_URL/health" "Health Check" || ((ERRORS++))
check_endpoint "$BACKEND_URL/a2a/discovery" "A2A Discovery" || ((ERRORS++))
check_endpoint "$BACKEND_URL/api/auth/login" "Auth Endpoint (may redirect)" 302 || ((ERRORS++))

echo ""
echo "📋 Checking Frontend"
echo "--------------------"

check_endpoint "$FRONTEND_URL" "Frontend" || ((ERRORS++))

echo ""
echo "📋 Environment Variables Check"
echo "-------------------------------"

# Check if we can connect to backend and get env info
ENV_CHECK=$(curl -s "$BACKEND_URL/api/config" 2>/dev/null | grep -c "configured" || echo "0")

if [ "$ENV_CHECK" != "0" ]; then
    echo -e "\033[0;32m✅ Environment configured\033[0m"
else
    echo -e "\033[0;33m⚠️  Cannot verify environment (expected if not authenticated)\033[0m"
fi

echo ""
echo "📋 CORS Configuration"
echo "---------------------"

CORS_CHECK=$(curl -s -I "$BACKEND_URL/health" 2>/dev/null | grep -i "access-control-allow-origin" || echo "")

if [ -n "$CORS_CHECK" ]; then
    echo -e "\033[0;32m✅ CORS headers present\033[0m"
    echo "   $CORS_CHECK"
else
    echo -e "\033[0;33m⚠️  CORS headers not visible (may be fine)\033[0m"
fi

echo ""
echo "========================================"

if [ $ERRORS -eq 0 ]; then
    echo -e "\033[0;32m🎉 All checks passed! Deployment looks good.\033[0m"
    echo ""
    echo "🔗 Important URLs:"
    echo "   Frontend: $FRONTEND_URL"
    echo "   Backend:  $BACKEND_URL"
    echo "   A2A:      $BACKEND_URL/a2a/discovery"
    exit 0
else
    echo -e "\033[0;31m❌ $ERRORS check(s) failed. Please review.\033[0m"
    echo ""
    echo "Troubleshooting:"
    echo "1. Check Zeabur deployment logs"
    echo "2. Verify environment variables are set"
    echo "3. Ensure database is initialized"
    exit 1
fi
