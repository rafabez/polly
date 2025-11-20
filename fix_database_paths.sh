#!/bin/bash
# Fix database paths in dashboard code
# Run this on the server: sudo bash fix_database_paths.sh

set -e

echo "=== Fix Database Paths ==="
echo ""

BACKEND_DIR="/opt/polly-backend/backend"
DASHBOARD_DIR="$BACKEND_DIR/dashboard"

echo "Step 1: Checking database location..."
if [ -f "$BACKEND_DIR/requests.db" ]; then
    echo "✓ Database found at: $BACKEND_DIR/requests.db"
else
    echo "! Database not found, will be created on first request"
fi

echo ""
echo "Step 2: Checking current paths in dashboard files..."
echo ""
echo "--- auth.py database references ---"
grep -n "requests.db\|DATABASE" "$DASHBOARD_DIR/auth.py" 2>/dev/null || echo "No database references in auth.py"

echo ""
echo "--- routes.py database references ---"
grep -n "requests.db\|DATABASE" "$DASHBOARD_DIR/routes.py" 2>/dev/null || echo "No database references in routes.py"

echo ""
echo "--- telemetry_middleware.py database references ---"
grep -n "requests.db\|DATABASE" "$DASHBOARD_DIR/telemetry_middleware.py" 2>/dev/null || echo "No database references in telemetry_middleware.py"

echo ""
echo "Step 3: Fixing database paths..."

# Fix auth.py if it has database path
if grep -q "requests.db" "$DASHBOARD_DIR/auth.py" 2>/dev/null; then
    echo "Fixing auth.py..."
    sed -i 's|"requests.db"|"/opt/polly-backend/backend/requests.db"|g' "$DASHBOARD_DIR/auth.py"
    sed -i "s|'requests.db'|'/opt/polly-backend/backend/requests.db'|g" "$DASHBOARD_DIR/auth.py"
    echo "✓ auth.py fixed"
fi

# Fix routes.py
if grep -q "requests.db" "$DASHBOARD_DIR/routes.py" 2>/dev/null; then
    echo "Fixing routes.py..."
    sed -i 's|"requests.db"|"/opt/polly-backend/backend/requests.db"|g' "$DASHBOARD_DIR/routes.py"
    sed -i "s|'requests.db'|'/opt/polly-backend/backend/requests.db'|g" "$DASHBOARD_DIR/routes.py"
    echo "✓ routes.py fixed"
fi

# Fix telemetry_middleware.py
if grep -q "requests.db" "$DASHBOARD_DIR/telemetry_middleware.py" 2>/dev/null; then
    echo "Fixing telemetry_middleware.py..."
    sed -i 's|"requests.db"|"/opt/polly-backend/backend/requests.db"|g' "$DASHBOARD_DIR/telemetry_middleware.py"
    sed -i "s|'requests.db'|'/opt/polly-backend/backend/requests.db'|g" "$DASHBOARD_DIR/telemetry_middleware.py"
    echo "✓ telemetry_middleware.py fixed"
fi

echo ""
echo "Step 4: Verifying new paths..."
echo ""
echo "--- Updated paths ---"
grep -n "requests.db" "$DASHBOARD_DIR"/*.py 2>/dev/null || echo "Using relative paths or no database references"

echo ""
echo "Step 5: Testing Python import..."
cd "$BACKEND_DIR"
source /opt/polly-backend/venv/bin/activate

python3 << 'PYTHON_TEST'
import sys
sys.path.insert(0, '/opt/polly-backend/backend')

try:
    from dashboard.routes import router
    print("✓ Successfully imported dashboard.routes")
except Exception as e:
    print(f"✗ Failed to import dashboard.routes: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from dashboard.telemetry_middleware import TelemetryMiddleware
    print("✓ Successfully imported dashboard.telemetry_middleware")
except Exception as e:
    print(f"✗ Failed to import dashboard.telemetry_middleware: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✓ All imports successful!")
PYTHON_TEST

if [ $? -eq 0 ]; then
    echo ""
    echo "Step 6: Restarting backend service..."
    systemctl restart polly-backend
    sleep 3

    if systemctl is-active --quiet polly-backend; then
        echo "✓ Backend is running!"
        echo ""
        echo "=== Fix completed successfully! ==="
        echo ""
        echo "Test endpoints:"
        echo "  curl http://localhost:8000/v1/models"
        echo "  curl http://localhost:8000/dashboard"
    else
        echo "✗ Backend failed to start. Checking logs..."
        journalctl -u polly-backend -n 50 --no-pager
        exit 1
    fi
else
    echo ""
    echo "✗ Import test failed. Please check the errors above."
    exit 1
fi
