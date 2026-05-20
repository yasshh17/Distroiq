#!/bin/bash
# Check for potential secrets in environment files
# Usage: check-env-secrets.sh [file1] [file2] ...

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

EXIT_CODE=0

echo "🔐 Checking for potential secrets in environment files..."

# Common patterns that indicate secrets
SECRET_PATTERNS=(
    "sk-"           # OpenAI/Anthropic API keys
    "pk_live_"      # Stripe live keys
    "pk_test_"      # Stripe test keys
    "rk_live_"      # Stripe restricted keys
    "eyJ"           # JWT tokens (base64 encoded)
    "AKIA"          # AWS access keys
    "ASIA"          # AWS session tokens
    "github_pat_"   # GitHub personal access tokens
    "ghp_"          # GitHub personal access tokens
    "gho_"          # GitHub OAuth tokens
    "ghu_"          # GitHub user-to-server tokens
    "ghs_"          # GitHub server-to-server tokens
    "ghr_"          # GitHub refresh tokens
)

# Allowed example values that are safe
ALLOWED_EXAMPLES=(
    "<your-api-key>"
    "<your-secret>"
    "<your-database-url>"
    "<your-supabase-url>"
    "<your-jwt-secret>"
    "your-secret-here"
    "replace-with-actual"
    "example"
    "test"
    "development"
    "localhost"
)

for file in "$@"; do
    echo "Checking: $file"

    if [[ ! -f "$file" ]]; then
        echo -e "${YELLOW}⚠️  Warning: $file does not exist${NC}"
        continue
    fi

    # Skip .env.example files (they should contain example values)
    if [[ "$file" == *.env.example ]]; then
        echo "   Skipping example file: $file"
        continue
    fi

    found_secrets=false

    while IFS= read -r line; do
        # Skip comments and empty lines
        [[ "$line" =~ ^#.*$ ]] && continue
        [[ -z "$line" ]] && continue

        # Extract the value part after =
        if [[ "$line" =~ ^[A-Z_]+=(.*)$ ]]; then
            value="${BASH_REMATCH[1]}"
            variable_name=$(echo "$line" | cut -d'=' -f1)

            # Skip if it's an allowed example value
            is_allowed=false
            for allowed in "${ALLOWED_EXAMPLES[@]}"; do
                if [[ "$value" == "$allowed" ]]; then
                    is_allowed=true
                    break
                fi
            done

            [[ "$is_allowed" == true ]] && continue

            # Check against secret patterns
            for pattern in "${SECRET_PATTERNS[@]}"; do
                if [[ "$value" == *"$pattern"* ]]; then
                    echo -e "${RED}❌ Potential secret found in $file:${NC}"
                    echo -e "   Variable: $variable_name"
                    echo -e "   Pattern: $pattern"
                    echo -e "   Value preview: ${value:0:20}..."
                    found_secrets=true
                    EXIT_CODE=1
                fi
            done

            # Check for suspiciously long random-looking strings
            if [[ ${#value} -gt 32 && "$value" =~ ^[A-Za-z0-9+/=_-]+$ ]]; then
                # Check entropy - very basic heuristic
                unique_chars=$(echo "$value" | fold -w1 | sort | uniq | wc -l)
                if [[ $unique_chars -gt 10 ]]; then
                    echo -e "${YELLOW}⚠️  Suspicious value found in $file:${NC}"
                    echo -e "   Variable: $variable_name"
                    echo -e "   Reason: Long random-looking string (${#value} chars)"
                    echo -e "   Value preview: ${value:0:20}..."
                    echo -e "   If this is a real secret, it should not be committed"
                fi
            fi
        fi
    done < "$file"

    if [[ "$found_secrets" == false ]]; then
        echo -e "${GREEN}   ✅ No obvious secrets found${NC}"
    fi
done

if [[ $EXIT_CODE -eq 0 ]]; then
    echo -e "${GREEN}✅ Secret check passed${NC}"
else
    echo -e "${RED}❌ Potential secrets detected${NC}"
    echo ""
    echo "If these are real secrets:"
    echo "  1. Remove them from the file"
    echo "  2. Add the file to .gitignore"
    echo "  3. Use environment variables or secret management"
    echo ""
    echo "If these are false positives:"
    echo "  1. Move them to .env.example with placeholder values"
    echo "  2. Add them to the allowed examples list in this script"
fi

exit $EXIT_CODE