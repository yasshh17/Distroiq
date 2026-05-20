#!/bin/bash
# Validate environment files for common configuration issues
# Usage: validate-env-files.sh [file1] [file2] ...

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

EXIT_CODE=0

echo "🔍 Validating environment files..."

for file in "$@"; do
    echo "Checking: $file"

    # Skip if file doesn't exist
    if [[ ! -f "$file" ]]; then
        echo -e "${YELLOW}⚠️  Warning: $file does not exist${NC}"
        continue
    fi

    # Check for leading/trailing whitespace in values
    if grep -q '= ' "$file" 2>/dev/null; then
        echo -e "${RED}❌ Error: Found environment variables with leading spaces in $file${NC}"
        echo "   Variables with leading spaces:"
        grep -n '= ' "$file" | head -5
        EXIT_CODE=1
    fi

    if grep -q ' =' "$file" 2>/dev/null; then
        echo -e "${RED}❌ Error: Found environment variables with trailing spaces in keys in $file${NC}"
        echo "   Variables with trailing spaces in keys:"
        grep -n ' =' "$file" | head -5
        EXIT_CODE=1
    fi

    # Check for empty required variables (in .env.example)
    if [[ "$file" == *.env.example ]]; then
        required_vars=(
            "DATABASE_URL"
            "ANTHROPIC_API_KEY"
            "SUPABASE_URL"
            "SUPABASE_JWT_SECRET"
        )

        for var in "${required_vars[@]}"; do
            if grep -q "^${var}=$" "$file" 2>/dev/null; then
                echo -e "${YELLOW}⚠️  Warning: Required variable $var is empty in $file${NC}"
            fi
        done
    fi

    # Check for actual secrets in non-example files
    if [[ "$file" != *.env.example ]] && [[ "$file" != *.env.local ]]; then
        echo -e "${RED}❌ Error: Found non-example .env file: $file${NC}"
        echo "   .env files should not be committed (they contain secrets)"
        echo "   Add $file to .gitignore or use .env.example format"
        EXIT_CODE=1
    fi

    # Check for suspicious patterns
    suspicious_patterns=(
        "password.*="
        "secret.*="
        "key.*="
        "token.*="
    )

    for pattern in "${suspicious_patterns[@]}"; do
        if grep -qi "$pattern" "$file" 2>/dev/null; then
            if [[ "$file" != *.env.example ]]; then
                echo -e "${RED}❌ Error: Found suspicious pattern '$pattern' in $file${NC}"
                echo "   This might contain secrets that shouldn't be committed"
                EXIT_CODE=1
            fi
        fi
    done

    # Validate URL formats
    if grep -q "SUPABASE_URL=" "$file" 2>/dev/null; then
        supabase_url=$(grep "SUPABASE_URL=" "$file" | cut -d'=' -f2)
        if [[ ! "$supabase_url" =~ ^https://.*\.supabase\.co$ ]] && [[ "$supabase_url" != "<your-supabase-url>" ]]; then
            echo -e "${RED}❌ Error: Invalid SUPABASE_URL format in $file${NC}"
            echo "   Expected: https://*.supabase.co"
            EXIT_CODE=1
        fi
    fi

    # Validate database URL format
    if grep -q "DATABASE_URL=" "$file" 2>/dev/null; then
        db_url=$(grep "DATABASE_URL=" "$file" | cut -d'=' -f2)
        if [[ ! "$db_url" =~ ^postgresql(\\+asyncpg)?:// ]] && [[ "$db_url" != "<your-database-url>" ]]; then
            echo -e "${RED}❌ Error: Invalid DATABASE_URL format in $file${NC}"
            echo "   Expected: postgresql:// or postgresql+asyncpg://"
            EXIT_CODE=1
        fi
    fi

    # Check for minimum JWT secret length
    if grep -q "SUPABASE_JWT_SECRET=" "$file" 2>/dev/null; then
        jwt_secret=$(grep "SUPABASE_JWT_SECRET=" "$file" | cut -d'=' -f2)
        if [[ ${#jwt_secret} -lt 32 ]] && [[ "$jwt_secret" != "<your-jwt-secret>" ]]; then
            echo -e "${RED}❌ Error: SUPABASE_JWT_SECRET too short in $file${NC}"
            echo "   JWT secrets should be at least 32 characters long"
            EXIT_CODE=1
        fi
    fi
done

if [[ $EXIT_CODE -eq 0 ]]; then
    echo -e "${GREEN}✅ All environment files passed validation${NC}"
else
    echo -e "${RED}❌ Environment file validation failed${NC}"
    echo ""
    echo "Common fixes:"
    echo "  - Remove leading/trailing spaces: FOO=bar (not FOO= bar)"
    echo "  - Don't commit actual .env files (use .env.example)"
    echo "  - Ensure JWT secrets are at least 32 characters"
    echo "  - Use proper URL formats for database and Supabase"
fi

exit $EXIT_CODE