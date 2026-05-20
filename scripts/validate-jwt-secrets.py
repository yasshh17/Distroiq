#!/usr/bin/env python3
"""
Validate JWT secret format and security in environment files.

Checks for proper JWT secret format, length, and entropy.
"""

import base64
import re
import sys
from pathlib import Path
from typing import List, Tuple


class JWTSecretValidator:
    """Validator for JWT secrets in environment files."""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_file(self, file_path: Path) -> bool:
        """Validate JWT secrets in an environment file."""
        if not file_path.exists():
            self.errors.append(f"File not found: {file_path}")
            return False

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            self._validate_content(content, file_path)
            return len(self.errors) == 0

        except Exception as e:
            self.errors.append(f"Error reading {file_path}: {e}")
            return False

    def _validate_content(self, content: str, file_path: Path) -> None:
        """Validate JWT secrets in file content."""
        lines = content.splitlines()

        for line_num, line in enumerate(lines, 1):
            line = line.strip()

            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue

            # Look for JWT secret variables
            if '=' in line:
                var_name, var_value = line.split('=', 1)
                var_name = var_name.strip()
                var_value = var_value.strip()

                if 'JWT' in var_name.upper() and 'SECRET' in var_name.upper():
                    self._validate_jwt_secret(var_name, var_value, file_path, line_num)

    def _validate_jwt_secret(
        self,
        var_name: str,
        var_value: str,
        file_path: Path,
        line_num: int
    ) -> None:
        """Validate a single JWT secret."""
        # Skip example/placeholder values
        placeholder_patterns = [
            '<',
            'your-',
            'example',
            'test-secret',
            'replace-',
            'change-me'
        ]

        if any(pattern in var_value.lower() for pattern in placeholder_patterns):
            return

        location = f"{file_path}:{line_num}"

        # Check minimum length
        if len(var_value) < 32:
            self.errors.append(
                f"{location}: {var_name} is too short ({len(var_value)} chars). "
                f"JWT secrets should be at least 32 characters for security."
            )
            return

        # Check for leading/trailing whitespace
        if var_value != var_value.strip():
            self.errors.append(
                f"{location}: {var_name} has leading or trailing whitespace. "
                f"This will cause JWT verification to fail."
            )

        # Check if it looks like base64
        if self._is_base64_like(var_value):
            try:
                decoded = base64.b64decode(var_value + '==')  # Add padding
                if len(decoded) < 32:
                    self.warnings.append(
                        f"{location}: {var_name} appears to be base64 but decodes to "
                        f"only {len(decoded)} bytes. Consider using a longer secret."
                    )
                else:
                    # Check entropy of decoded bytes
                    entropy = self._calculate_entropy(decoded)
                    if entropy < 6.0:
                        self.warnings.append(
                            f"{location}: {var_name} has low entropy ({entropy:.1f}). "
                            f"Consider using a more random secret."
                        )
            except Exception:
                self.warnings.append(
                    f"{location}: {var_name} looks like base64 but cannot be decoded. "
                    f"Verify the secret format."
                )
        else:
            # Check entropy of raw string
            entropy = self._calculate_entropy(var_value.encode('utf-8'))
            if entropy < 5.0:
                self.warnings.append(
                    f"{location}: {var_name} has low entropy ({entropy:.1f}). "
                    f"Consider using a more random secret."
                )

        # Check for common weak patterns
        weak_patterns = [
            r'(.)\1{3,}',  # Repeated characters
            r'12345',
            r'abcde',
            r'qwerty',
            r'password',
            r'secret',
        ]

        for pattern in weak_patterns:
            if re.search(pattern, var_value.lower()):
                self.warnings.append(
                    f"{location}: {var_name} contains weak pattern '{pattern}'. "
                    f"Use a cryptographically random secret."
                )

    def _is_base64_like(self, value: str) -> bool:
        """Check if a value looks like base64."""
        # Basic heuristic: mostly base64 characters and reasonable length
        base64_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=')
        return (len(value) > 20 and
                len(set(value) - base64_chars) / len(value) < 0.1 and
                len(value) % 4 in [0, 1])  # Base64 padding rules

    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy of data."""
        if not data:
            return 0.0

        # Count frequency of each byte
        frequencies = {}
        for byte in data:
            frequencies[byte] = frequencies.get(byte, 0) + 1

        # Calculate entropy
        entropy = 0.0
        data_len = len(data)
        for count in frequencies.values():
            p = count / data_len
            if p > 0:
                entropy -= p * (p).bit_length() - 1

        return entropy

    def print_results(self) -> None:
        """Print validation results."""
        if self.errors:
            print("❌ JWT secret validation errors:")
            for error in self.errors:
                print(f"   {error}")

        if self.warnings:
            print("⚠️  JWT secret validation warnings:")
            for warning in self.warnings:
                print(f"   {warning}")

        if not self.errors and not self.warnings:
            print("✅ JWT secret validation passed")


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: validate-jwt-secrets.py <env-file> [env-file2] ...")
        return 1

    validator = JWTSecretValidator()
    overall_success = True

    for file_path in sys.argv[1:]:
        path = Path(file_path)
        success = validator.validate_file(path)
        overall_success = overall_success and success

    validator.print_results()

    if not overall_success:
        print()
        print("To fix JWT secret issues:")
        print("  - Generate secrets with: openssl rand -base64 64")
        print("  - Ensure no leading/trailing whitespace")
        print("  - Use at least 32 characters for security")
        print("  - Avoid predictable patterns")

    return 0 if overall_success else 1


if __name__ == "__main__":
    sys.exit(main())