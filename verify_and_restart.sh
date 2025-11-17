#!/bin/bash
# Verify dashboard integration and restart
# Run: sudo bash verify_and_restart.sh

echo "=== Verify Dashboard Integration ==="
echo ""

MAIN_PY="/opt/polly-backend/backend/main.py"

echo "Step 1: Verifying dashboard code is BEFORE 'if __name__'..."
echo ""

# Get line numbers
IF_NAME_LINE=$(grep -n 'if __name__ == "__main__":' "$MAIN_PY" | cut -d: -f1)
DASHBOARD_LINE=$(grep -n 'from dashboard.routes import router' "$MAIN_PY" | cut -d: -f1)

echo "if __name__ is at line: $IF_NAME_LINE"
echo "dashboard import is at line: $DASHBOARD_LINE"
echo ""

if [ -z "$DASHBOARD_LINE" ]; then
    echo "✗ ERROR: Dashboard import not found!"
    exit 1
fi

if [ "$DASHBOARD_LINE" -lt "$IF_NAME_LINE" ]; then
    echo "✓ CORRECT! Dashboard code is BEFORE 'if __name__' block"
    echo "  This means it will execute when Gunicorn imports the module"
else
    echo "✗ ERROR: Dashboard code is AFTER 'if __name__' block!"
    echo "  It will never execute with Gunicorn!"
    exit 1
fi

echo ""
echo "Step 2: Showing dashboard integration code..."
echo ""
sed -n "${DASHBOARD_LINE},$((DASHBOARD_LINE+10))p" "$MAIN_PY"

echo ""
echo "Step 3: Checking all required imports are present..."
echo ""

REQUIRED_IMPORTS=(
    "from dashboard.routes import router"
    "from dashboard.telemetry_middleware import TelemetryMiddleware"
    "app.include_router"
    "app.add_middleware(TelemetryMiddleware)"
)

ALL_GOOD=true
for import_line in "${REQUIRED_IMPORTS[@]}"; do
    if grep -q "$import_line" "$MAIN_PY"; then
        echo "✓ Found: $import_line"
    else
        echo "✗ Missing: $import_line"
        ALL_GOOD=false
    fi
done

if [ "$ALL_GOOD" = false ]; then
    echo ""
    echo "✗ Some required code is missing!"
    exit 1
fi

echo ""
echo "✓ All dashboard integration code is present and in correct location!"
echo ""
echo "Step 4: Restarting backend service..."
systemctl restart polly-backend

sleep 3

if systemctl is-active --quiet polly-backend; then
    echo "✓ Backend is running!"
else
    echo "✗ Backend failed to start!"
    echo ""
    echo "Logs:"
    journalctl -u polly-backend -n 30 --no-pager
    exit 1
fi

echo ""
echo "Step 5: Testing endpoints..."
sleep 2

# Test API
echo -n "Testing /v1/models... "
API_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/v1/models)
if [ "$API_RESPONSE" = "200" ]; then
    echo "✓ (HTTP $API_RESPONSE)"
else
    echo "✗ (HTTP $API_RESPONSE)"
fi

# Test dashboard
echo -n "Testing /dashboard... "
DASHBOARD_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/dashboard)
if [ "$DASHBOARD_RESPONSE" = "200" ] || [ "$DASHBOARD_RESPONSE" = "307" ]; then
    echo "✓ (HTTP $DASHBOARD_RESPONSE)"
else
    echo "✗ (HTTP $DASHBOARD_RESPONSE)"
    echo ""
    echo "Response body:"
    curl -s http://localhost:8000/dashboard
    echo ""
fi

# Test dashboard login
echo -n "Testing /dashboard/login... "
LOGIN_RESPONSE=$(curl -s http://localhost:8000/dashboard/login)
if echo "$LOGIN_RESPONSE" | grep -q "login\|password\|username"; then
    echo "✓ (Found login page)"
else
    echo "✗ (No login page found)"
    echo ""
    echo "Response:"
    echo "$LOGIN_RESPONSE" | head -20
fi

echo ""
echo "=== Verification Complete ==="
echo ""
echo "If all tests passed, access:"
echo "  http://api.interzonesec.com/dashboard"
echo ""
echo "Credentials:"
echo "  Username: admin"
echo "  Password: admin123"
