#!/bin/bash
# Fix script to properly integrate dashboard into main.py
# Run this on the server: sudo bash fix_backend.sh

set -e

echo "=== Polly Backend Dashboard Fix ==="
echo ""

BACKEND_DIR="/opt/polly-backend/backend"
MAIN_PY="$BACKEND_DIR/main.py"
BACKUP="$BACKEND_DIR/main.py.backup"

# Check if we're root
if [ "$EUID" -ne 0 ]; then
    echo "ERROR: Please run as root (use sudo)"
    exit 1
fi

echo "Step 1: Restoring clean backup..."
if [ ! -f "$BACKUP" ]; then
    echo "ERROR: Backup file not found at $BACKUP"
    exit 1
fi

cp "$BACKUP" "$MAIN_PY"
echo "✓ Backup restored"

echo ""
echo "Step 2: Inserting dashboard integration code..."

# Create a Python script to do the insertion properly
python3 << 'PYTHON_SCRIPT'
import sys
from pathlib import Path

main_py_path = Path("/opt/polly-backend/backend/main.py")

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

# Read file
with open(main_py_path, 'r') as f:
    content = f.read()

# Find position to insert (before "if __name__")
if_name_pos = content.find('if __name__ == "__main__":')
if if_name_pos == -1:
    print("ERROR: Could not find 'if __name__' block")
    sys.exit(1)

# Find the start of that line
line_start = content.rfind('\n', 0, if_name_pos) + 1

# Insert dashboard code
new_content = (
    content[:line_start] +
    dashboard_code + '\n\n' +
    content[line_start:]
)

# Write back
with open(main_py_path, 'w') as f:
    f.write(new_content)

print("✓ Dashboard code inserted successfully")
PYTHON_SCRIPT

echo ""
echo "Step 3: Restarting backend service..."
systemctl restart polly-backend

echo ""
echo "Step 4: Checking service status..."
sleep 2

if systemctl is-active --quiet polly-backend; then
    echo "✓ Backend is running!"
else
    echo "✗ Backend failed to start. Checking logs..."
    journalctl -u polly-backend -n 30 --no-pager
    exit 1
fi

echo ""
echo "=== Fix completed successfully! ==="
echo ""
echo "Dashboard should now be accessible at:"
echo "  http://api.interzonesec.com/dashboard"
echo ""
echo "Default credentials:"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
echo "You can check the logs with:"
echo "  sudo journalctl -u polly-backend -f"
