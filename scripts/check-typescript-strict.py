#!/usr/bin/env python3
"""
Check that TypeScript is configured in strict mode.

Ensures that tsconfig.json has proper strict settings for type safety.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List


class TypeScriptStrictChecker:
    """Checker for TypeScript strict mode configuration."""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def check_file(self, file_path: Path) -> bool:
        """Check a tsconfig.json file for strict mode settings."""
        if not file_path.exists():
            self.errors.append(f"TypeScript config not found: {file_path}")
            return False

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse JSON (with comments support)
            config = self._parse_json_with_comments(content)
            self._validate_config(config, file_path)

            return len(self.errors) == 0

        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON in {file_path}: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Error reading {file_path}: {e}")
            return False

    def _parse_json_with_comments(self, content: str) -> Dict[str, Any]:
        """Parse JSON with comments (basic implementation)."""
        # Remove single-line comments
        lines = []
        for line in content.splitlines():
            # Remove comments, but be careful about strings
            comment_pos = line.find('//')
            if comment_pos != -1:
                # Simple heuristic: if // is inside quotes, keep it
                quote_count = line[:comment_pos].count('"')
                if quote_count % 2 == 0:  # Even number of quotes before //
                    line = line[:comment_pos]
            lines.append(line)

        cleaned_content = '\n'.join(lines)
        return json.loads(cleaned_content)

    def _validate_config(self, config: Dict[str, Any], file_path: Path) -> None:
        """Validate TypeScript configuration for strict mode."""
        compiler_options = config.get('compilerOptions', {})

        # Required strict settings
        required_strict = {
            'strict': True,
            'noImplicitAny': True,
            'noImplicitReturns': True,
            'noFallthroughCasesInSwitch': True,
            'noUncheckedIndexedAccess': True,
        }

        # Recommended additional settings
        recommended_settings = {
            'exactOptionalPropertyTypes': True,
            'noImplicitOverride': True,
            'noPropertyAccessFromIndexSignature': True,
            'noUncheckedIndexedAccess': True,
        }

        # Check required settings
        for setting, expected_value in required_strict.items():
            actual_value = compiler_options.get(setting)

            if actual_value != expected_value:
                if setting == 'strict' and actual_value is None:
                    # strict: true enables many other checks
                    self.errors.append(
                        f"{file_path}: 'strict' must be set to true for type safety"
                    )
                elif setting != 'strict':  # Don't double-report if strict is false
                    if compiler_options.get('strict') is not True:
                        self.errors.append(
                            f"{file_path}: '{setting}' should be {expected_value} "
                            f"(currently {actual_value})"
                        )

        # Check recommended settings
        for setting, expected_value in recommended_settings.items():
            actual_value = compiler_options.get(setting)

            if actual_value != expected_value:
                self.warnings.append(
                    f"{file_path}: Consider setting '{setting}' to {expected_value} "
                    f"for enhanced type safety"
                )

        # Check for problematic settings
        problematic_settings = {
            'any': 'Avoid disabling TypeScript\'s type checking',
            'noImplicitAny': False,  # Should not be false
            'skipLibCheck': True,    # Should generally be false for strict checking
        }

        for setting, issue in problematic_settings.items():
            if isinstance(issue, str):
                # Custom message
                if setting in compiler_options:
                    self.warnings.append(f"{file_path}: {issue}")
            else:
                # Check for specific value
                if compiler_options.get(setting) == issue:
                    self.warnings.append(
                        f"{file_path}: '{setting}' is set to {issue}, "
                        f"which reduces type safety"
                    )

        # Check include/exclude patterns
        include = config.get('include', [])
        exclude = config.get('exclude', [])

        if not include:
            self.warnings.append(
                f"{file_path}: No 'include' patterns specified. "
                f"Consider explicitly including source directories."
            )

        # Check for common exclusions
        recommended_excludes = ['node_modules', '**/*.js', 'dist', 'build']
        for exclude_pattern in recommended_excludes:
            if exclude_pattern not in exclude:
                if exclude_pattern == 'node_modules':
                    self.warnings.append(
                        f"{file_path}: Consider excluding '{exclude_pattern}' "
                        f"for better performance"
                    )

    def print_results(self) -> None:
        """Print validation results."""
        if self.errors:
            print("❌ TypeScript strict mode errors:")
            for error in self.errors:
                print(f"   {error}")

        if self.warnings:
            print("⚠️  TypeScript configuration recommendations:")
            for warning in self.warnings:
                print(f"   {warning}")

        if not self.errors and not self.warnings:
            print("✅ TypeScript strict mode configuration is correct")


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 2:
        # Look for tsconfig.json in current directory
        config_files = ['tsconfig.json']
    else:
        config_files = sys.argv[1:]

    checker = TypeScriptStrictChecker()
    overall_success = True

    for config_file in config_files:
        path = Path(config_file)
        success = checker.check_file(path)
        overall_success = overall_success and success

    checker.print_results()

    if not overall_success:
        print()
        print("To enable TypeScript strict mode:")
        print('  Add "strict": true to compilerOptions in tsconfig.json')
        print("  This enables several type checking options for better safety")
        print("  Consider the additional recommended settings for even stricter checking")

    return 0 if overall_success else 1


if __name__ == "__main__":
    sys.exit(main())