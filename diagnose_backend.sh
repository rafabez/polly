#!/bin/bash
# Diagnose the actual backend error
# Run this on the server: sudo bash diagnose_backend.sh

echo "=== Polly Backend Diagnostic Script ==="
echo ""

# Stop the service so we can see real errors
echo "Step 1: Stopping systemd service to prevent restarts..."
systemctl stop polly-backend
echo "✓ Service stopped"

echo ""
echo "Step 2: Trying to import the application to see the real error..."
cd /opt/polly-backend/backend

# Activate venv and try to import
source /opt/polly-backend/venv/bin/activate

echo ""
echo "--- Attempting to import main.py ---"
python3 -c "import sys; sys.path.insert(0, '/opt/polly-backend/backend'); import main" 2>&1

echo ""
echo ""
echo "Step 3: Checking if dashboard directory exists..."
if [ -d "/opt/polly-backend/backend/dashboard" ]; then
    echo "✓ Dashboard directory exists"
    ls -la /opt/polly-backend/backend/dashboard/
else
    echo "✗ Dashboard directory NOT FOUND - this is the problem!"
fi

echo ""
echo "Step 4: Checking main.py for dashboard imports..."
echo "Lines with 'dashboard' in main.py:"
grep -n "dashboard" /opt/polly-backend/backend/main.py || echo "No dashboard references found"

echo ""
echo "Step 5: Checking where 'if __name__' is located..."
grep -n 'if __name__' /opt/polly-backend/backend/main.py

echo ""
echo "=== Diagnostic Complete ==="
echo ""
echo "To manually test the backend:"
echo "  cd /opt/polly-backend/backend"
echo "  source /opt/polly-backend/venv/bin/activate"
echo "  python3 main.py"
echo ""
echo "To restart the service:"
echo "  sudo systemctl start polly-backend"
