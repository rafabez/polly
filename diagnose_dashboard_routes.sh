#!/bin/bash
# Diagnose why dashboard returns "Not Found"
# Run this on the server: bash diagnose_dashboard_routes.sh (no sudo needed)

echo "=== Dashboard Route Diagnostic ==="
echo ""

MAIN_PY="/opt/polly-backend/backend/main.py"

echo "Step 1: Checking if dashboard integration code exists in main.py..."
echo ""
if grep -q "dashboard" "$MAIN_PY"; then
    echo "✓ Found 'dashboard' references in main.py:"
    echo ""
    grep -n "dashboard" "$MAIN_PY"
    echo ""
else
    echo "✗ NO dashboard references found in main.py!"
    echo "  This is the problem - dashboard was never integrated!"
    exit 0
fi

echo ""
echo "Step 2: Checking where dashboard code is located..."
echo ""
echo "Looking for 'if __name__' line:"
grep -n 'if __name__' "$MAIN_PY"
echo ""

echo "Lines with dashboard integration:"
grep -n -B2 -A2 "from dashboard" "$MAIN_PY"

echo ""
echo "Step 3: Testing if Python can see the dashboard routes..."
cd /opt/polly-backend/backend
/opt/polly-backend/venv/bin/python3 << 'PYTHON_TEST'
import sys
sys.path.insert(0, '/opt/polly-backend/backend')

print("Attempting to import main.py...")
try:
    import main
    print("✓ main.py imported successfully\n")
except Exception as e:
    print(f"✗ Failed to import main.py: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("Checking registered routes in FastAPI app...")
print("")
print("All registered routes:")
print("-" * 60)
for route in main.app.routes:
    if hasattr(route, 'path'):
        print(f"  {route.path}")
print("-" * 60)
print("")

# Check specifically for dashboard routes
dashboard_routes = [route for route in main.app.routes if hasattr(route, 'path') and 'dashboard' in route.path.lower()]

if dashboard_routes:
    print(f"✓ Found {len(dashboard_routes)} dashboard route(s):")
    for route in dashboard_routes:
        methods = getattr(route, 'methods', ['GET'])
        print(f"  {route.path} - {methods}")
    print("")
else:
    print("✗ NO dashboard routes found in app.routes!")
    print("  This means the dashboard router was NOT included in main.py")
    print("")

# Check if middleware is registered
print("Checking middleware...")
if hasattr(main.app, 'user_middleware'):
    middleware_names = [m.cls.__name__ for m in main.app.user_middleware]
    print(f"Registered middleware: {middleware_names}")
    if 'TelemetryMiddleware' in middleware_names:
        print("✓ TelemetryMiddleware is registered")
    else:
        print("✗ TelemetryMiddleware NOT registered")
else:
    print("! Cannot check middleware")

print("")
print("=" * 60)
print("DIAGNOSIS:")
print("=" * 60)

if not dashboard_routes:
    print("❌ PROBLEM FOUND:")
    print("   Dashboard routes are NOT registered in FastAPI app")
    print("")
    print("CAUSE:")
    print("   Either:")
    print("   1. app.include_router(dashboard_router) was never called")
    print("   2. Dashboard integration code is AFTER 'if __name__'")
    print("   3. Dashboard integration has import errors")
    print("")
    print("SOLUTION:")
    print("   Add dashboard integration to main.py BEFORE 'if __name__'")
else:
    print("✓ Dashboard routes ARE registered")
    print("  The problem must be something else")
    print("")
    print("  Try accessing:")
    print("    curl http://localhost:8000/dashboard")
    print("    curl http://localhost:8000/dashboard/login")

PYTHON_TEST

echo ""
echo "Step 4: Testing actual HTTP endpoints..."
echo ""

# Test if backend is running
if ! systemctl is-active --quiet polly-backend; then
    echo "! Backend service is NOT running"
    echo "  Start it with: sudo systemctl start polly-backend"
    exit 0
fi

echo "Testing /v1/models endpoint:"
curl -s http://localhost:8000/v1/models | head -c 100
echo ""
echo ""

echo "Testing /dashboard endpoint:"
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" http://localhost:8000/dashboard)
echo "$RESPONSE"
echo ""

echo "Testing /dashboard/login endpoint:"
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" http://localhost:8000/dashboard/login)
echo "$RESPONSE"
echo ""

echo ""
echo "=== Diagnostic Complete ==="
