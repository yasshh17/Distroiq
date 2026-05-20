#!/usr/bin/env python3
"""
Validate backend configuration files for common issues.

Checks Pydantic models, field validators, and configuration patterns.
"""

import ast
import sys
from pathlib import Path
from typing import List, Set, Tuple


class ConfigValidator:
    """Validator for backend configuration files."""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_file(self, file_path: Path) -> bool:
        """Validate a single configuration file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content, filename=str(file_path))
            self._validate_ast(tree, file_path)

            return len(self.errors) == 0

        except SyntaxError as e:
            self.errors.append(f"Syntax error in {file_path}: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Error parsing {file_path}: {e}")
            return False

    def _validate_ast(self, tree: ast.AST, file_path: Path) -> None:
        """Validate the AST of a configuration file."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                self._validate_settings_class(node, file_path)

    def _validate_settings_class(self, node: ast.ClassDef, file_path: Path) -> None:
        """Validate a Settings class definition."""
        if not node.name.endswith('Settings'):
            return

        # Check for proper imports
        self._check_pydantic_imports(node, file_path)

        # Check for field validators
        self._check_field_validators(node, file_path)

        # Check for security-sensitive fields
        self._check_security_fields(node, file_path)

        # Check for proper type annotations
        self._check_type_annotations(node, file_path)

    def _check_pydantic_imports(self, node: ast.ClassDef, file_path: Path) -> None:
        """Check that proper Pydantic imports are used."""
        # This would need the full module context to validate properly
        # For now, we'll check basic patterns
        pass

    def _check_field_validators(self, node: ast.ClassDef, file_path: Path) -> None:
        """Check for field validators on sensitive fields."""
        sensitive_fields = {
            'SUPABASE_JWT_SECRET',
            'SUPABASE_SERVICE_ROLE_KEY',
            'ANTHROPIC_API_KEY',
            'DATABASE_URL',
            'REDIS_URL'
        }

        # Find field definitions
        field_names = set()
        validator_fields = set()

        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                field_names.add(item.target.id)

            elif isinstance(item, ast.FunctionDef):
                # Check if it's a field validator
                for decorator in item.decorator_list:
                    if (isinstance(decorator, ast.Call) and
                        isinstance(decorator.func, ast.Name) and
                        decorator.func.id == 'field_validator'):

                        # Extract validated field names from decorator args
                        for arg in decorator.args:
                            if isinstance(arg, ast.Constant):
                                validator_fields.add(arg.value)

        # Check that sensitive fields have validators
        missing_validators = sensitive_fields & field_names - validator_fields

        for field in missing_validators:
            self.warnings.append(
                f"Field '{field}' in {file_path} should have a field validator "
                f"to prevent configuration issues"
            )

    def _check_security_fields(self, node: ast.ClassDef, file_path: Path) -> None:
        """Check security-related field configurations."""
        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                field_name = item.target.id

                # Check that secrets don't have default values
                if any(secret in field_name.upper() for secret in ['SECRET', 'KEY', 'PASSWORD']):
                    if item.value is not None:
                        # Allow empty string defaults only
                        if not (isinstance(item.value, ast.Constant) and item.value.value == ""):
                            self.errors.append(
                                f"Secret field '{field_name}' in {file_path} "
                                f"should not have a non-empty default value"
                            )

    def _check_type_annotations(self, node: ast.ClassDef, file_path: Path) -> None:
        """Check that all fields have proper type annotations."""
        for item in node.body:
            if isinstance(item, ast.Assign):
                # This is an old-style assignment without annotation
                if isinstance(item.targets[0], ast.Name):
                    field_name = item.targets[0].id
                    if field_name.isupper():  # Looks like a config field
                        self.warnings.append(
                            f"Field '{field_name}' in {file_path} "
                            f"should use type annotation (field: type = value)"
                        )

    def print_results(self) -> None:
        """Print validation results."""
        if self.errors:
            print("❌ Configuration validation errors:")
            for error in self.errors:
                print(f"   {error}")

        if self.warnings:
            print("⚠️  Configuration validation warnings:")
            for warning in self.warnings:
                print(f"   {warning}")

        if not self.errors and not self.warnings:
            print("✅ Configuration validation passed")


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: validate-backend-config.py <config-file>")
        return 1

    config_file = Path(sys.argv[1])

    if not config_file.exists():
        print(f"❌ Configuration file not found: {config_file}")
        return 1

    validator = ConfigValidator()
    success = validator.validate_file(config_file)
    validator.print_results()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())