#!/bin/bash
# Test that the backend can import without errors
# This catches configuration and import issues early

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🐍 Testing backend import..."

# Change to backend directory if it exists
if [[ -d "backend" ]]; then
    cd backend
elif [[ -f "app/main.py" ]]; then
    # Already in backend directory
    :
else
    echo -e "${RED}❌ Backend directory not found${NC}"
    exit 1
fi

# Check if virtual environment exists and activate it
if [[ -f ".venv/bin/activate" ]]; then
    source .venv/bin/activate
    echo "✅ Activated virtual environment"
elif [[ -f "venv/bin/activate" ]]; then
    source venv/bin/activate
    echo "✅ Activated virtual environment"
else
    echo -e "${YELLOW}⚠️  No virtual environment found, using system Python${NC}"
fi

# Test basic imports
echo "Testing basic imports..."

python3 -c "
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, '.')

try:
    print('Testing core configuration...')
    from app.core.config import settings
    print('✅ Configuration import successful')

    # Test that critical settings can be accessed
    # (This will trigger validation)
    try:
        _ = settings.ANTHROPIC_API_KEY
        print('✅ Settings validation passed')
    except Exception as e:
        print(f'⚠️  Settings validation warning: {e}')

    print('Testing logging setup...')
    from app.core.logging import setup_logging
    print('✅ Logging import successful')

    print('Testing security module...')
    from app.core.security import verify_jwt, AuthError
    print('✅ Security import successful')

    print('Testing audit system...')
    from app.core.audit import AuditLogger, AuditAction
    print('✅ Audit system import successful')

    print('Testing diagnostics...')
    from app.core.diagnostics import SystemDiagnostics
    print('✅ Diagnostics import successful')

    print('Testing metrics...')
    from app.core.metrics import metrics, track_user_action
    print('✅ Metrics import successful')

    print('Testing main app...')
    from app.main import app
    print('✅ Main app import successful')

    print()
    print('🎉 All backend imports successful!')

except ImportError as e:
    print(f'❌ Import error: {e}')
    print()
    print('Common fixes:')
    print('  - Install dependencies: pip install -r requirements.txt')
    print('  - Check Python path and working directory')
    print('  - Verify all modules are present')
    sys.exit(1)

except Exception as e:
    print(f'❌ Configuration error: {e}')
    print()
    print('Common fixes:')
    print('  - Check environment variables in .env file')
    print('  - Verify all required settings are provided')
    print('  - Check for syntax errors in configuration')
    sys.exit(1)
"

exit_code=$?

if [[ $exit_code -eq 0 ]]; then
    echo -e "${GREEN}✅ Backend import test passed${NC}"
else
    echo -e "${RED}❌ Backend import test failed${NC}"
fi

exit $exit_code