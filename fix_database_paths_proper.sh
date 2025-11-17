#!/bin/bash
# Properly fix database paths in dashboard code
# Run this on the server: sudo bash fix_database_paths_proper.sh

set -e

echo "=== Fix Database Paths (Proper) ==="
echo ""

DASHBOARD_DIR="/opt/polly-backend/backend/dashboard"

echo "Step 1: Fixing database.py..."
if [ -f "$DASHBOARD_DIR/database.py" ]; then
    # The database is at /opt/polly-backend/backend/requests.db
    # dashboard.py is at /opt/polly-backend/backend/dashboard/database.py
    # So parent.parent gives us /opt/polly-backend/backend/
    # We just need to go up one level and add requests.db

    cat > "$DASHBOARD_DIR/database.py" << 'EOF'
"""Database configuration for dashboard"""
from pathlib import Path
import sqlite3
from typing import Optional

# Database path - dashboard is in backend/dashboard/, db is in backend/
DB_PATH = Path(__file__).parent.parent / "requests.db"

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database if needed"""
    conn = get_db_connection()
    # Tables should already exist from telemetry.py
    conn.close()
EOF
    echo "✓ database.py fixed"
else
    echo "! database.py not found, skipping"
fi

echo ""
echo "Step 2: Fixing telemetry_middleware.py..."
if [ -f "$DASHBOARD_DIR/telemetry_middleware.py" ]; then
    # Same logic - go up one level from dashboard/ to backend/, then add requests.db
    sed -i 's|DB_PATH = .*|DB_PATH = Path(__file__).parent.parent / "requests.db"|g' "$DASHBOARD_DIR/telemetry_middleware.py"
    echo "✓ telemetry_middleware.py fixed"
else
    echo "! telemetry_middleware.py not found, skipping"
fi

echo ""
echo "Step 3: Checking routes.py for database references..."
if [ -f "$DASHBOARD_DIR/routes.py" ]; then
    if grep -q "DB_PATH\|requests.db" "$DASHBOARD_DIR/routes.py"; then
        echo "Found database references in routes.py, fixing..."
        sed -i 's|DB_PATH = .*|DB_PATH = Path(__file__).parent.parent / "requests.db"|g' "$DASHBOARD_DIR/routes.py"
        echo "✓ routes.py fixed"
    else
        echo "✓ No database path in routes.py (probably imports from database.py)"
    fi
fi

echo ""
echo "Step 4: Verifying paths..."
echo ""
grep -n "DB_PATH\|requests\.db" "$DASHBOARD_DIR"/*.py | grep -v "^#" || echo "No database paths found"

echo ""
echo "Step 5: Testing Python imports..."
cd /opt/polly-backend/backend

/opt/polly-backend/venv/bin/python3 << 'PYTHON_TEST'
import sys
sys.path.insert(0, '/opt/polly-backend/backend')

print("Testing imports...")

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

try:
    from dashboard.database import get_db_connection
    print("✓ Successfully imported dashboard.database")

    # Test database connection
    conn = get_db_connection()
    print(f"✓ Database connection successful")
    conn.close()
except Exception as e:
    print(f"✗ Failed with dashboard.database: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✓✓✓ All imports and database connection successful! ✓✓✓")
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

        # Test models endpoint
        echo -n "Testing /v1/models... "
        if curl -s http://localhost:8000/v1/models | grep -q "data"; then
            echo "✓"
        else
            echo "✗"
        fi

        # Test dashboard
        echo -n "Testing /dashboard... "
        if curl -s http://localhost:8000/dashboard | grep -q "login\|dashboard"; then
            echo "✓"
        else
            echo "✗"
        fi

        echo ""
        echo "=== Fix completed successfully! ==="
        echo ""
        echo "Dashboard: http://api.interzonesec.com/dashboard"
        echo "Username: admin"
        echo "Password: admin123"

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
