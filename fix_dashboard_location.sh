#!/bin/bash
# Fix dashboard location - move it into backend folder
# Run this on the server: sudo bash fix_dashboard_location.sh

set -e

echo "=== Fix Dashboard Location ==="
echo ""

# Check if we're root
if [ "$EUID" -ne 0 ]; then
    echo "ERROR: Please run as root (use sudo)"
    exit 1
fi

BACKEND_DIR="/opt/polly-backend/backend"
DASHBOARD_SRC="/opt/polly-backend/dashboard"
DASHBOARD_DST="/opt/polly-backend/backend/dashboard"

echo "Step 1: Checking current structure..."
if [ ! -d "$DASHBOARD_SRC" ]; then
    echo "ERROR: Dashboard source not found at $DASHBOARD_SRC"
    exit 1
fi

if [ -d "$DASHBOARD_DST" ]; then
    echo "! Dashboard already exists in backend folder, removing old one..."
    rm -rf "$DASHBOARD_DST"
fi

echo "✓ Current structure verified"

echo ""
echo "Step 2: Moving dashboard into backend folder..."
mv "$DASHBOARD_SRC" "$DASHBOARD_DST"
echo "✓ Dashboard moved to $DASHBOARD_DST"

echo ""
echo "Step 3: Verifying dashboard structure..."
if [ -f "$DASHBOARD_DST/routes.py" ]; then
    echo "✓ routes.py found"
else
    echo "✗ ERROR: routes.py not found!"
    exit 1
fi

if [ -f "$DASHBOARD_DST/telemetry_middleware.py" ]; then
    echo "✓ telemetry_middleware.py found"
else
    echo "✗ ERROR: telemetry_middleware.py not found!"
    exit 1
fi

echo ""
echo "Step 4: Testing Python import..."
cd "$BACKEND_DIR"
source /opt/polly-backend/venv/bin/activate

# Test if we can import the dashboard modules now
python3 << 'PYTHON_TEST'
import sys
sys.path.insert(0, '/opt/polly-backend/backend')

try:
    from dashboard.routes import router
    print("✓ Successfully imported dashboard.routes")
except Exception as e:
    print(f"✗ Failed to import dashboard.routes: {e}")
    sys.exit(1)

try:
    from dashboard.telemetry_middleware import TelemetryMiddleware
    print("✓ Successfully imported dashboard.telemetry_middleware")
except Exception as e:
    print(f"✗ Failed to import dashboard.telemetry_middleware: {e}")
    sys.exit(1)
PYTHON_TEST

echo ""
echo "Step 5: Restarting backend service..."
systemctl restart polly-backend

echo ""
echo "Step 6: Checking service status..."
sleep 3

if systemctl is-active --quiet polly-backend; then
    echo "✓ Backend is running!"

    # Show recent logs
    echo ""
    echo "Recent logs:"
    journalctl -u polly-backend -n 20 --no-pager
else
    echo "✗ Backend failed to start. Checking logs..."
    journalctl -u polly-backend -n 50 --no-pager
    exit 1
fi

echo ""
echo "=== Fix completed successfully! ==="
echo ""
echo "Dashboard should now be accessible at:"
echo "  http://api.interzonesec.com/dashboard"
echo ""
echo "Test the backend:"
echo "  curl http://localhost:8000/v1/models"
