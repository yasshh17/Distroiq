#!/usr/bin/env python3
"""
Debug script for account deletion issues.

Provides detailed diagnostics for account deletion problems,
including configuration validation, connectivity tests, and step-by-step debugging.
"""

import asyncio
import json
import sys
import uuid
from pathlib import Path
from typing import Dict, Any, Optional

# Add backend to Python path
backend_path = Path(__file__).parent.parent / "backend"
if backend_path.exists():
    sys.path.insert(0, str(backend_path))

try:
    from app.core.diagnostics import debug_account_deletion, create_test_jwt, AuthDiagnostics
    from app.core.config import settings
    from app.core.security import verify_jwt, extract_user_id, AuthError
    BACKEND_AVAILABLE = True
except ImportError as e:
    BACKEND_AVAILABLE = False
    IMPORT_ERROR = str(e)


class AccountDeletionDebugger:
    """Interactive debugger for account deletion issues."""

    def __init__(self):
        self.user_id: Optional[str] = None
        self.test_jwt: Optional[str] = None

    async def run_interactive_debug(self) -> None:
        """Run interactive debugging session."""
        print("🔍 Account Deletion Debug Tool")
        print("=" * 40)

        if not BACKEND_AVAILABLE:
            print(f"❌ Backend not available: {IMPORT_ERROR}")
            print("Make sure you're running from the project root directory.")
            return

        while True:
            print("\nOptions:")
            print("1. Test configuration")
            print("2. Debug specific user ID")
            print("3. Test with generated user ID")
            print("4. Test JWT creation and validation")
            print("5. Full system diagnostic")
            print("6. Test Supabase connectivity")
            print("0. Exit")

            choice = input("\nSelect option: ").strip()

            try:
                if choice == "0":
                    break
                elif choice == "1":
                    await self._test_configuration()
                elif choice == "2":
                    await self._debug_specific_user()
                elif choice == "3":
                    await self._test_generated_user()
                elif choice == "4":
                    await self._test_jwt_system()
                elif choice == "5":
                    await self._full_diagnostic()
                elif choice == "6":
                    await self._test_supabase_connectivity()
                else:
                    print("Invalid choice. Please try again.")

            except Exception as e:
                print(f"❌ Error: {e}")
                if input("Continue? (y/n): ").lower() != 'y':
                    break

    async def _test_configuration(self) -> None:
        """Test configuration settings."""
        print("\n🔧 Testing Configuration...")
        print("-" * 30)

        # Test critical settings
        critical_settings = {
            'SUPABASE_URL': 'Supabase project URL',
            'SUPABASE_JWT_SECRET': 'JWT verification secret',
            'SUPABASE_SERVICE_ROLE_KEY': 'Service role key for admin operations',
            'ANTHROPIC_API_KEY': 'Anthropic API key'
        }

        for setting_name, description in critical_settings.items():
            value = getattr(settings, setting_name, None)

            if not value:
                print(f"❌ {setting_name}: Not configured")
            elif value == "":
                print(f"❌ {setting_name}: Empty string")
            elif len(value) < 10:
                print(f"⚠️  {setting_name}: Very short ({len(value)} chars)")
            elif value.startswith(' ') or value.endswith(' '):
                print(f"❌ {setting_name}: Has whitespace padding")
            else:
                # Show safe preview
                safe_preview = value[:8] + "..." if len(value) > 8 else value
                print(f"✅ {setting_name}: Configured ({safe_preview}, {len(value)} chars)")

        print(f"\nEnvironment: {settings.APP_ENV}")

    async def _debug_specific_user(self) -> None:
        """Debug account deletion for a specific user ID."""
        user_id = input("\nEnter user ID to debug: ").strip()

        if not user_id:
            print("❌ No user ID provided")
            return

        try:
            uuid.UUID(user_id)  # Validate UUID format
        except ValueError:
            print("❌ Invalid UUID format")
            return

        print(f"\n🔍 Debugging account deletion for user: {user_id}")
        print("-" * 50)

        result = await debug_account_deletion(user_id)
        self._print_debug_result(result)

    async def _test_generated_user(self) -> None:
        """Test with a generated test user ID."""
        user_id = str(uuid.uuid4())
        print(f"\n🧪 Testing with generated user ID: {user_id}")
        print("-" * 50)

        result = await debug_account_deletion(user_id)
        self._print_debug_result(result)

    async def _test_jwt_system(self) -> None:
        """Test JWT creation and validation system."""
        print("\n🔐 Testing JWT System...")
        print("-" * 30)

        # Test JWT secret validation
        jwt_result = AuthDiagnostics.validate_jwt_secret()
        print(f"JWT Secret: {'✅' if jwt_result.passed else '❌'} {jwt_result.details.get('message')}")

        if not jwt_result.passed:
            print("Cannot proceed with JWT tests due to secret issues.")
            return

        # Generate test JWT
        test_user_id = str(uuid.uuid4())
        print(f"\nGenerating test JWT for user: {test_user_id}")

        try:
            test_jwt = create_test_jwt(user_id=test_user_id)
            print(f"✅ JWT created successfully")
            print(f"Token preview: {test_jwt[:50]}...")

            # Verify the token
            payload = verify_jwt(test_jwt)
            extracted_user_id = extract_user_id(payload)

            if str(extracted_user_id) == test_user_id:
                print(f"✅ JWT verification successful")
                print(f"Extracted user ID: {extracted_user_id}")
            else:
                print(f"❌ JWT verification failed: ID mismatch")

        except AuthError as e:
            print(f"❌ JWT test failed: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

    async def _full_diagnostic(self) -> None:
        """Run full system diagnostic."""
        print("\n🏥 Full System Diagnostic...")
        print("-" * 30)

        # Configuration test
        print("1. Configuration...")
        await self._test_configuration()

        print("\n2. Authentication System...")
        try:
            auth_diagnostics = await AuthDiagnostics.test_supabase_connection()
            print(f"Supabase Connection: {'✅' if auth_diagnostics.passed else '❌'} {auth_diagnostics.details.get('message')}")

            service_role_test = await AuthDiagnostics.test_service_role_permissions()
            print(f"Service Role Permissions: {'✅' if service_role_test.passed else '❌'} {service_role_test.details.get('message')}")

        except Exception as e:
            print(f"❌ Authentication diagnostic failed: {e}")

        print("\n3. JWT System...")
        await self._test_jwt_system()

    async def _test_supabase_connectivity(self) -> None:
        """Test Supabase connectivity specifically."""
        print("\n🔗 Testing Supabase Connectivity...")
        print("-" * 40)

        try:
            # Basic connection test
            conn_result = await AuthDiagnostics.test_supabase_connection()
            print(f"Basic Connection: {'✅' if conn_result.passed else '❌'}")
            print(f"Details: {conn_result.details.get('message', 'No details')}")

            if not conn_result.passed:
                print("\nConnection failed. Check:")
                print("- SUPABASE_URL is correct")
                print("- Network connectivity")
                print("- Supabase service status")
                return

            # Service role test
            role_result = await AuthDiagnostics.test_service_role_permissions()
            print(f"\nService Role: {'✅' if role_result.passed else '❌'}")
            print(f"Details: {role_result.details.get('message', 'No details')}")

            if not role_result.passed:
                print("\nService role issues. Check:")
                print("- SUPABASE_SERVICE_ROLE_KEY is correct")
                print("- Service role has admin permissions")
                print("- Key has not been rotated/revoked")

        except Exception as e:
            print(f"❌ Supabase test failed: {e}")

    def _print_debug_result(self, result: Dict[str, Any]) -> None:
        """Print formatted debug result."""
        print(f"User ID: {result['user_id']}")
        print(f"Overall Status: {result['overall_status']}")
        print(f"Timestamp: {result['timestamp']}")

        print("\nDiagnostic Steps:")
        for i, step in enumerate(result['steps'], 1):
            status_emoji = "✅" if step['passed'] else "❌"
            print(f"{i}. {step['step']}: {status_emoji}")

            if 'details' in step:
                details = step['details']
                if isinstance(details, dict):
                    for key, value in details.items():
                        if key not in ['message']:
                            print(f"   {key}: {value}")

            if not step['passed'] and 'details' in step:
                error_msg = step['details'].get('error', step['details'].get('message', 'Unknown error'))
                print(f"   Error: {error_msg}")

            print()

        if result['overall_status'] != "ready":
            print("🔧 Recommendations:")
            print("- Check configuration settings")
            print("- Verify network connectivity")
            print("- Confirm Supabase service status")
            print("- Review environment variable formatting")


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Debug account deletion issues")
    parser.add_argument("--user-id", help="Debug specific user ID")
    parser.add_argument("--test-jwt", action="store_true", help="Test JWT system only")
    parser.add_argument("--config-only", action="store_true", help="Test configuration only")
    parser.add_argument("--json", action="store_true", help="Output JSON format")

    args = parser.parse_args()

    debugger = AccountDeletionDebugger()

    if not BACKEND_AVAILABLE:
        print(f"❌ Backend not available: {IMPORT_ERROR}")
        return 1

    try:
        if args.config_only:
            await debugger._test_configuration()
        elif args.test_jwt:
            await debugger._test_jwt_system()
        elif args.user_id:
            result = await debug_account_deletion(args.user_id)
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                debugger._print_debug_result(result)
        else:
            await debugger.run_interactive_debug()

        return 0

    except KeyboardInterrupt:
        print("\n👋 Debugging session cancelled")
        return 0
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))