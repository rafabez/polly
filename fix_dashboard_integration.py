#!/usr/bin/env python3
"""
Fix script to properly insert dashboard integration code into main.py
Run this on the server in /opt/polly-backend/backend/
"""

import sys
from pathlib import Path

def fix_main_py():
    """Fix main.py by properly inserting dashboard code before if __name__"""

    main_py_path = Path("/opt/polly-backend/backend/main.py")
    backup_path = Path("/opt/polly-backend/backend/main.py.backup")

    # Dashboard integration code to insert
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

    # Read the backup file
    print(f"Reading backup from {backup_path}...")
    with open(backup_path, 'r') as f:
        lines = f.readlines()

    # Find the line with "if __name__ == "__main__":"
    if_name_line = None
    for i, line in enumerate(lines):
        if 'if __name__ == "__main__":' in line:
            if_name_line = i
            print(f"Found 'if __name__' at line {i + 1}")
            break

    if if_name_line is None:
        print("ERROR: Could not find 'if __name__ == \"__main__\":' in file")
        sys.exit(1)

    # Insert dashboard code before the if __name__ line
    # First, add a blank line before dashboard code if not present
    insert_position = if_name_line

    # Remove any trailing blank lines before if __name__
    while insert_position > 0 and lines[insert_position - 1].strip() == '':
        insert_position -= 1

    # Add back one blank line, then dashboard code, then one more blank line
    new_lines = (
        lines[:insert_position] +
        ['\n'] +
        dashboard_code.split('\n')[1:]  # Skip first empty line
        + ['\n'] +
        lines[if_name_line:]
    )

    # Write the fixed file
    print(f"Writing fixed main.py to {main_py_path}...")
    with open(main_py_path, 'w') as f:
        f.writelines(new_lines)

    print("✓ Successfully fixed main.py!")
    print(f"✓ Dashboard code inserted at line {insert_position + 1}")
    print("\nNext steps:")
    print("  1. Restart the backend: sudo systemctl restart polly-backend")
    print("  2. Check status: sudo systemctl status polly-backend")
    print("  3. Check logs: sudo journalctl -u polly-backend -n 50")

if __name__ == "__main__":
    try:
        fix_main_py()
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
