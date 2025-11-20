#!/bin/bash
# Add dashboard integration to main.py
# Run this on the server: sudo bash add_dashboard_to_main.sh

set -e

echo "=== Add Dashboard Integration to main.py ==="
echo ""

MAIN_PY="/opt/polly-backend/backend/main.py"

echo "Step 1: Checking if dashboard is already integrated..."
if grep -q "from dashboard.routes import router" "$MAIN_PY"; then
    echo "! Dashboard integration already exists in main.py"
    echo ""
    echo "Current dashboard references:"
    grep -n "dashboard" "$MAIN_PY"
    echo ""
    read -p "Remove existing integration and re-add? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborting. Please manually check main.py"
        exit 1
    fi

    echo "Removing existing dashboard integration..."
    sed -i '/from dashboard.routes import/d' "$MAIN_PY"
    sed -i '/from dashboard.telemetry_middleware import/d' "$MAIN_PY"
    sed -i '/from fastapi.staticfiles import StaticFiles/d' "$MAIN_PY"
    sed -i '/app.add_middleware(TelemetryMiddleware)/d' "$MAIN_PY"
    sed -i '/app.include_router(dashboard_router)/d' "$MAIN_PY"
    sed -i '/app.mount("\/dashboard\/static"/d' "$MAIN_PY"
    sed -i '/# Dashboard integration/d' "$MAIN_PY"
    echo "✓ Removed old integration"
fi

echo ""
echo "Step 2: Finding the correct location to insert dashboard code..."

# Find the line number of "if __name__"
IF_NAME_LINE=$(grep -n 'if __name__ == "__main__":' "$MAIN_PY" | cut -d: -f1)

if [ -z "$IF_NAME_LINE" ]; then
    echo "✗ ERROR: Could not find 'if __name__ == \"__main__\":' in main.py"
    exit 1
fi

echo "✓ Found 'if __name__' at line $IF_NAME_LINE"

echo ""
echo "Step 3: Adding dashboard integration code..."

# Use Python to properly insert the code
/opt/polly-backend/venv/bin/python3 << EOF
import sys

main_py_path = "$MAIN_PY"

# Read the file
with open(main_py_path, 'r') as f:
    lines = f.readlines()

# Find the if __name__ line
if_name_line = None
for i, line in enumerate(lines):
    if 'if __name__ == "__main__":' in line:
        if_name_line = i
        break

if if_name_line is None:
    print("ERROR: Could not find if __name__ block")
    sys.exit(1)

# Dashboard integration code
dashboard_code = '''
# Dashboard integration
from dashboard.routes import router as dashboard_router
from dashboard.telemetry_middleware import TelemetryMiddleware
from fastapi.staticfiles import StaticFiles

# Add telemetry middleware
app.add_middleware(TelemetryMiddleware)

# Mount dashboard routes
app.include_router(dashboard_router)

# Mount static files for dashboard
app.mount("/dashboard/static", StaticFiles(directory="dashboard/static"), name="dashboard_static")

'''

# Insert before if __name__
new_lines = lines[:if_name_line] + [dashboard_code] + lines[if_name_line:]

# Write back
with open(main_py_path, 'w') as f:
    f.writelines(new_lines)

print(f"✓ Dashboard integration added at line {if_name_line}")
EOF

if [ $? -ne 0 ]; then
    echo "✗ Failed to add dashboard integration"
    exit 1
fi

echo ""
echo "Step 4: Verifying the changes..."
echo ""
echo "--- Dashboard integration in main.py ---"
grep -n -A2 -B2 "Dashboard integration" "$MAIN_PY"

echo ""
echo "Step 5: Testing Python import..."
cd /opt/polly-backend/backend
/opt/polly-backend/venv/bin/python3 << 'PYTHON_TEST'
import sys
sys.path.insert(0, '/opt/polly-backend/backend')

try:
    import main
    print("✓ main.py imports successfully")
except Exception as e:
    print(f"✗ Failed to import main.py: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Check if app has dashboard routes
try:
    routes = [route.path for route in main.app.routes]
    dashboard_routes = [r for r in routes if 'dashboard' in r.lower()]

    if dashboard_routes:
        print(f"✓ Found {len(dashboard_routes)} dashboard routes:")
        for route in dashboard_routes:
            print(f"  - {route}")
    else:
        print("✗ No dashboard routes found!")
        sys.exit(1)
except Exception as e:
    print(f"! Could not check routes: {e}")

print("\n✓✓✓ Dashboard integration successful! ✓✓✓")
PYTHON_TEST

if [ $? -eq 0 ]; then
    echo ""
    echo "Step 6: Restarting backend service..."
    systemctl restart polly-backend
    sleep 3

    if systemctl is-active --quiet polly-backend; then
        echo "✓ Backend is running!"

        echo ""
        echo "Step 7: Testing endpoints..."
        sleep 2

        # Test API
        echo -n "Testing /v1/models... "
        if curl -s http://localhost:8000/v1/models | grep -q "data"; then
            echo "✓"
        else
            echo "✗"
        fi

        # Test dashboard redirect
        echo -n "Testing /dashboard... "
        DASHBOARD_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/dashboard)
        if [ "$DASHBOARD_RESPONSE" = "307" ] || [ "$DASHBOARD_RESPONSE" = "200" ]; then
            echo "✓ (HTTP $DASHBOARD_RESPONSE)"
        else
            echo "✗ (HTTP $DASHBOARD_RESPONSE)"
        fi

        # Test dashboard login page
        echo -n "Testing /dashboard/login... "
        if curl -s http://localhost:8000/dashboard/login | grep -q "login\|password"; then
            echo "✓"
        else
            echo "✗"
        fi

        echo ""
        echo "=== Dashboard Integration Complete! ==="
        echo ""
        echo "Dashboard URL: http://api.interzonesec.com/dashboard"
        echo "Credentials:"
        echo "  Username: admin"
        echo "  Password: admin123"
        echo ""
        echo "If you get 'Not Found', check the logs:"
        echo "  sudo journalctl -u polly-backend -n 50"

    else
        echo "✗ Backend failed to start. Checking logs..."
        journalctl -u polly-backend -n 50 --no-pager
        exit 1
    fi
else
    echo ""
    echo "✗ Import test failed. Not restarting service."
    exit 1
fi
