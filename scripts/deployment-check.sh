#!/bin/bash
# Deployment readiness check for DistroIQ
# Validates that the application is ready for deployment

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

EXIT_CODE=0
WARNINGS=0
CHECKS=0

echo -e "${BLUE}🚀 DistroIQ Deployment Readiness Check${NC}"
echo "=========================================="

# Helper functions
check_pass() {
    echo -e "${GREEN}✅ $1${NC}"
    CHECKS=$((CHECKS + 1))
}

check_fail() {
    echo -e "${RED}❌ $1${NC}"
    EXIT_CODE=1
    CHECKS=$((CHECKS + 1))
}

check_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    WARNINGS=$((WARNINGS + 1))
    CHECKS=$((CHECKS + 1))
}

check_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Environment detection
detect_environment() {
    if [[ "${VERCEL:-}" == "1" ]]; then
        echo "vercel"
    elif [[ "${RENDER:-}" == "true" ]]; then
        echo "render"
    elif [[ "${GITHUB_ACTIONS:-}" == "true" ]]; then
        echo "ci"
    elif [[ "${CI:-}" == "true" ]]; then
        echo "ci"
    else
        echo "local"
    fi
}

ENVIRONMENT=$(detect_environment)
echo -e "${BLUE}Environment: $ENVIRONMENT${NC}"
echo ""

# Frontend checks
echo -e "${BLUE}🎨 Frontend Checks${NC}"
echo "-------------------"

# Check if package.json exists
if [[ -f "package.json" ]]; then
    check_pass "package.json found"

    # Check for required scripts
    if grep -q '"build"' package.json; then
        check_pass "Build script configured"
    else
        check_fail "No build script in package.json"
    fi

    if grep -q '"start"' package.json; then
        check_pass "Start script configured"
    else
        check_warn "No start script in package.json"
    fi

    # Check dependencies
    if [[ -f "package-lock.json" ]] || [[ -f "yarn.lock" ]]; then
        check_pass "Dependencies locked"
    else
        check_warn "No lockfile found (package-lock.json or yarn.lock)"
    fi

    # Check for security vulnerabilities (if available)
    if command -v npm >/dev/null 2>&1; then
        if npm audit --audit-level=high --summary >/dev/null 2>&1; then
            check_pass "No high-severity vulnerabilities"
        else
            check_warn "High-severity vulnerabilities found (run 'npm audit')"
        fi
    fi
else
    check_fail "package.json not found"
fi

# TypeScript configuration
if [[ -f "tsconfig.json" ]]; then
    check_pass "TypeScript configuration found"

    # Check if strict mode is enabled
    if grep -q '"strict".*true' tsconfig.json; then
        check_pass "TypeScript strict mode enabled"
    else
        check_warn "TypeScript strict mode not enabled"
    fi
else
    check_warn "No TypeScript configuration"
fi

# Next.js configuration
if [[ -f "next.config.mjs" ]] || [[ -f "next.config.js" ]]; then
    check_pass "Next.js configuration found"
else
    check_warn "No Next.js configuration file"
fi

# Environment variables
if [[ -f ".env.example" ]]; then
    check_pass ".env.example found"
else
    check_warn "No .env.example file (recommended for documentation)"
fi

# Check for committed secrets
if [[ -f ".env" ]] && git ls-files .env >/dev/null 2>&1; then
    check_fail ".env file is tracked in git (security risk)"
fi

echo ""

# Backend checks
echo -e "${BLUE}🔧 Backend Checks${NC}"
echo "------------------"

if [[ -d "backend" ]]; then
    cd backend

    # Python requirements
    if [[ -f "requirements.txt" ]]; then
        check_pass "requirements.txt found"

        # Check for specific critical dependencies
        critical_deps=("fastapi" "uvicorn" "pydantic" "httpx" "anthropic")
        for dep in "${critical_deps[@]}"; do
            if grep -q "^$dep" requirements.txt; then
                check_pass "$dep dependency found"
            else
                check_fail "$dep dependency missing"
            fi
        done
    else
        check_fail "requirements.txt not found"
    fi

    # Virtual environment
    if [[ -d ".venv" ]] || [[ -d "venv" ]]; then
        check_pass "Virtual environment directory found"
    else
        check_warn "No virtual environment directory"
    fi

    # Backend configuration
    if [[ -f "app/core/config.py" ]]; then
        check_pass "Backend configuration found"

        # Check for Pydantic settings
        if grep -q "BaseSettings" app/core/config.py; then
            check_pass "Pydantic settings configured"
        else
            check_warn "Pydantic BaseSettings not found"
        fi

        # Check for field validators
        if grep -q "field_validator" app/core/config.py; then
            check_pass "Field validators implemented"
        else
            check_warn "No field validators found (recommended for robustness)"
        fi
    else
        check_fail "Backend configuration not found"
    fi

    # Database migrations (if using Alembic)
    if [[ -d "alembic" ]]; then
        check_pass "Database migrations directory found"

        if [[ -f "alembic.ini" ]]; then
            check_pass "Alembic configuration found"
        else
            check_warn "alembic.ini not found"
        fi
    else
        check_info "No database migrations (may not be needed)"
    fi

    # Tests
    if [[ -d "tests" ]]; then
        check_pass "Tests directory found"

        test_files=$(find tests -name "*.py" | wc -l)
        if [[ $test_files -gt 0 ]]; then
            check_pass "$test_files test files found"
        else
            check_warn "Tests directory empty"
        fi
    else
        check_warn "No tests directory"
    fi

    cd ..
else
    check_warn "No backend directory found"
fi

echo ""

# Security checks
echo -e "${BLUE}🔒 Security Checks${NC}"
echo "-------------------"

# Check for sensitive files in git
sensitive_patterns=("*.env" "*.key" "*.pem" "*secret*" "*password*")
for pattern in "${sensitive_patterns[@]}"; do
    if git ls-files "$pattern" 2>/dev/null | grep -q .; then
        check_fail "Sensitive files tracked in git: $(git ls-files "$pattern" | head -3 | tr '\n' ' ')"
    fi
done

if [[ $EXIT_CODE -eq 0 ]]; then
    check_pass "No sensitive files tracked in git"
fi

# Check .gitignore
if [[ -f ".gitignore" ]]; then
    check_pass ".gitignore found"

    important_ignores=(".env" "node_modules" ".next" "dist" "__pycache__")
    for ignore in "${important_ignores[@]}"; do
        if grep -q "^$ignore" .gitignore; then
            check_pass "$ignore in .gitignore"
        else
            check_warn "$ignore not explicitly in .gitignore"
        fi
    done
else
    check_fail ".gitignore not found"
fi

# Pre-commit hooks
if [[ -f ".pre-commit-config.yaml" ]]; then
    check_pass "Pre-commit configuration found"
else
    check_warn "No pre-commit hooks configured"
fi

echo ""

# Build and deployment checks
echo -e "${BLUE}🔨 Build & Deployment Checks${NC}"
echo "------------------------------"

# Frontend build
if [[ "$ENVIRONMENT" != "ci" ]]; then
    check_info "Attempting frontend build test..."

    if command -v npm >/dev/null 2>&1; then
        if npm run build >/dev/null 2>&1; then
            check_pass "Frontend build successful"
        else
            check_fail "Frontend build failed"
        fi
    else
        check_warn "npm not available for build test"
    fi
fi

# Backend import test
if [[ -d "backend" ]]; then
    check_info "Testing backend imports..."

    cd backend
    if python3 -c "from app.main import app; print('✅ Backend imports successful')" 2>/dev/null; then
        check_pass "Backend imports successful"
    else
        check_fail "Backend import test failed"
    fi
    cd ..
fi

# Deployment-specific checks
case $ENVIRONMENT in
    "vercel")
        if [[ -f "vercel.json" ]]; then
            check_pass "Vercel configuration found"
        else
            check_warn "No vercel.json configuration"
        fi
        ;;
    "render")
        if [[ -f "render.yaml" ]]; then
            check_pass "Render configuration found"
        else
            check_warn "No render.yaml configuration"
        fi
        ;;
esac

echo ""

# Summary
echo -e "${BLUE}📊 Summary${NC}"
echo "----------"
echo "Total checks: $CHECKS"
echo "Warnings: $WARNINGS"

if [[ $EXIT_CODE -eq 0 ]]; then
    if [[ $WARNINGS -eq 0 ]]; then
        echo -e "${GREEN}🎉 All checks passed! Ready for deployment.${NC}"
    else
        echo -e "${YELLOW}✅ Deployment ready with $WARNINGS warning(s).${NC}"
        echo -e "${YELLOW}Consider addressing warnings for optimal deployment.${NC}"
    fi
else
    echo -e "${RED}❌ Deployment readiness check failed.${NC}"
    echo -e "${RED}Please fix the errors above before deploying.${NC}"
fi

echo ""
echo "For detailed deployment instructions, see: docs/DEPLOYMENT.md"

exit $EXIT_CODE