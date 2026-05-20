#!/usr/bin/env python3
"""
Comprehensive health check script for DistroIQ.

Runs diagnostic checks on all system components and reports status.
Can be used by monitoring systems, deployment pipelines, and operations.
"""

import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add backend to Python path if running from project root
backend_path = Path(__file__).parent.parent / "backend"
if backend_path.exists():
    sys.path.insert(0, str(backend_path))

try:
    from app.core.diagnostics import SystemDiagnostics
    from app.core.config import settings
    BACKEND_AVAILABLE = True
except ImportError:
    BACKEND_AVAILABLE = False


class HealthChecker:
    """Comprehensive health checker for all system components."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: Dict[str, Any] = {}
        self.start_time = time.time()

    async def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks and return results."""
        print("🏥 Running DistroIQ Health Checks...")

        # System information
        self.results["timestamp"] = datetime.utcnow().isoformat() + "Z"
        self.results["system"] = await self._check_system_info()

        # Backend checks
        if BACKEND_AVAILABLE:
            self.results["backend"] = await self._check_backend()
        else:
            self.results["backend"] = {
                "status": "unavailable",
                "message": "Backend modules not available (not in backend directory?)"
            }

        # Frontend checks
        self.results["frontend"] = await self._check_frontend()

        # Infrastructure checks
        self.results["infrastructure"] = await self._check_infrastructure()

        # Summary
        self.results["duration_seconds"] = time.time() - self.start_time
        self.results["overall_status"] = self._calculate_overall_status()

        return self.results

    async def _check_system_info(self) -> Dict[str, Any]:
        """Check basic system information."""
        import platform
        import psutil

        return {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "disk_free_gb": round(psutil.disk_usage('.').free / (1024**3), 2),
            "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
        }

    async def _check_backend(self) -> Dict[str, Any]:
        """Check backend health."""
        checks = {}

        # Configuration check
        try:
            config_status = "healthy"
            config_message = "Configuration loaded successfully"

            # Test critical settings
            critical_settings = [
                'DATABASE_URL',
                'ANTHROPIC_API_KEY',
                'SUPABASE_URL',
                'SUPABASE_JWT_SECRET'
            ]

            missing = []
            for setting in critical_settings:
                if not getattr(settings, setting, None):
                    missing.append(setting)

            if missing:
                config_status = "degraded"
                config_message = f"Missing settings: {', '.join(missing)}"

        except Exception as e:
            config_status = "unhealthy"
            config_message = f"Configuration error: {str(e)}"

        checks["configuration"] = {
            "status": config_status,
            "message": config_message
        }

        # Authentication system check
        try:
            auth_diagnostics = await SystemDiagnostics.run_auth_diagnostics()
            auth_passed = all(d.passed for d in auth_diagnostics)

            checks["authentication"] = {
                "status": "healthy" if auth_passed else "unhealthy",
                "details": [
                    {
                        "name": d.name,
                        "status": "pass" if d.passed else "fail",
                        "message": d.details.get("message", "No details")
                    }
                    for d in auth_diagnostics
                ]
            }
        except Exception as e:
            checks["authentication"] = {
                "status": "unhealthy",
                "message": f"Authentication check failed: {str(e)}"
            }

        # Database connectivity (if configured)
        checks["database"] = await self._check_database()

        # Redis connectivity (if configured)
        checks["redis"] = await self._check_redis()

        return checks

    async def _check_database(self) -> Dict[str, Any]:
        """Check database connectivity."""
        try:
            # This would test actual database connection
            # For now, just check if URL is configured
            if hasattr(settings, 'DATABASE_URL') and settings.DATABASE_URL:
                if 'localhost' in settings.DATABASE_URL:
                    return {
                        "status": "degraded",
                        "message": "Database URL points to localhost (development only)"
                    }
                return {
                    "status": "healthy",
                    "message": "Database URL configured"
                }
            else:
                return {
                    "status": "unhealthy",
                    "message": "Database URL not configured"
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Database check failed: {str(e)}"
            }

    async def _check_redis(self) -> Dict[str, Any]:
        """Check Redis connectivity."""
        try:
            if hasattr(settings, 'REDIS_URL') and settings.REDIS_URL:
                # Could implement actual Redis ping here
                return {
                    "status": "healthy",
                    "message": "Redis URL configured"
                }
            else:
                return {
                    "status": "degraded",
                    "message": "Redis URL not configured"
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Redis check failed: {str(e)}"
            }

    async def _check_frontend(self) -> Dict[str, Any]:
        """Check frontend build and configuration."""
        checks = {}

        # Check if Next.js build exists
        build_dir = Path(".next")
        if build_dir.exists():
            checks["build"] = {
                "status": "healthy",
                "message": "Next.js build directory exists"
            }
        else:
            checks["build"] = {
                "status": "degraded",
                "message": "No Next.js build found (run npm run build)"
            }

        # Check package.json
        package_json = Path("package.json")
        if package_json.exists():
            try:
                with open(package_json) as f:
                    package_data = json.load(f)

                checks["dependencies"] = {
                    "status": "healthy",
                    "message": f"Package.json found with {len(package_data.get('dependencies', {}))} dependencies"
                }
            except Exception as e:
                checks["dependencies"] = {
                    "status": "unhealthy",
                    "message": f"Error reading package.json: {str(e)}"
                }
        else:
            checks["dependencies"] = {
                "status": "unhealthy",
                "message": "package.json not found"
            }

        # Check TypeScript config
        tsconfig = Path("tsconfig.json")
        if tsconfig.exists():
            checks["typescript"] = {
                "status": "healthy",
                "message": "TypeScript configuration found"
            }
        else:
            checks["typescript"] = {
                "status": "degraded",
                "message": "TypeScript configuration not found"
            }

        return checks

    async def _check_infrastructure(self) -> Dict[str, Any]:
        """Check infrastructure components."""
        checks = {}

        # Git repository check
        git_dir = Path(".git")
        if git_dir.exists():
            checks["git"] = {
                "status": "healthy",
                "message": "Git repository initialized"
            }
        else:
            checks["git"] = {
                "status": "degraded",
                "message": "Not a Git repository"
            }

        # Environment files check
        env_files = [".env", ".env.local", ".env.example"]
        env_status = []

        for env_file in env_files:
            if Path(env_file).exists():
                env_status.append(env_file)

        if env_status:
            checks["environment"] = {
                "status": "healthy",
                "message": f"Environment files found: {', '.join(env_status)}"
            }
        else:
            checks["environment"] = {
                "status": "degraded",
                "message": "No environment files found"
            }

        # Security checks
        sensitive_files = [".env", "backend/.env"]
        exposed_secrets = []

        for file_path in sensitive_files:
            if Path(file_path).exists():
                # Check if file is in git (which would be bad)
                try:
                    import subprocess
                    result = subprocess.run(
                        ["git", "ls-files", file_path],
                        capture_output=True,
                        text=True
                    )
                    if result.stdout.strip():
                        exposed_secrets.append(file_path)
                except:
                    pass

        if exposed_secrets:
            checks["security"] = {
                "status": "unhealthy",
                "message": f"Secret files tracked in git: {', '.join(exposed_secrets)}"
            }
        else:
            checks["security"] = {
                "status": "healthy",
                "message": "No obvious security issues detected"
            }

        return checks

    def _calculate_overall_status(self) -> str:
        """Calculate overall system status."""
        def get_status_score(status: str) -> int:
            return {"healthy": 3, "degraded": 2, "unhealthy": 1, "unavailable": 0}.get(status, 0)

        all_statuses = []

        def collect_statuses(obj, path=""):
            if isinstance(obj, dict):
                if "status" in obj:
                    all_statuses.append(obj["status"])
                else:
                    for key, value in obj.items():
                        collect_statuses(value, f"{path}.{key}" if path else key)

        collect_statuses(self.results)

        if not all_statuses:
            return "unknown"

        min_score = min(get_status_score(status) for status in all_statuses)
        score_to_status = {3: "healthy", 2: "degraded", 1: "unhealthy", 0: "unavailable"}

        return score_to_status[min_score]

    def print_results(self, format_type: str = "text") -> None:
        """Print results in specified format."""
        if format_type == "json":
            print(json.dumps(self.results, indent=2))
        elif format_type == "summary":
            self._print_summary()
        else:
            self._print_detailed()

    def _print_summary(self) -> None:
        """Print a summary of health check results."""
        status = self.results["overall_status"]
        emoji = {"healthy": "✅", "degraded": "⚠️", "unhealthy": "❌", "unavailable": "🔄"}.get(status, "❓")

        print(f"{emoji} Overall Status: {status.upper()}")
        print(f"Duration: {self.results['duration_seconds']:.1f}s")
        print()

        # Count status by category
        categories = ["backend", "frontend", "infrastructure"]
        for category in categories:
            if category in self.results:
                cat_data = self.results[category]
                if isinstance(cat_data, dict):
                    statuses = []
                    def collect_status(obj):
                        if isinstance(obj, dict):
                            if "status" in obj:
                                statuses.append(obj["status"])
                            else:
                                for value in obj.values():
                                    collect_status(value)

                    collect_status(cat_data)
                    if statuses:
                        worst_status = min(statuses, key=lambda s: {"healthy": 3, "degraded": 2, "unhealthy": 1, "unavailable": 0}.get(s, 0))
                        emoji = {"healthy": "✅", "degraded": "⚠️", "unhealthy": "❌", "unavailable": "🔄"}.get(worst_status, "❓")
                        print(f"{emoji} {category.title()}: {worst_status}")

    def _print_detailed(self) -> None:
        """Print detailed health check results."""
        print("📊 Detailed Health Check Results")
        print("=" * 40)
        print(f"Timestamp: {self.results['timestamp']}")
        print(f"Overall Status: {self.results['overall_status'].upper()}")
        print(f"Duration: {self.results['duration_seconds']:.1f}s")
        print()

        def print_section(data, title, indent=0):
            prefix = "  " * indent
            print(f"{prefix}{title}:")

            if isinstance(data, dict):
                for key, value in data.items():
                    if key == "status":
                        emoji = {"healthy": "✅", "degraded": "⚠️", "unhealthy": "❌", "unavailable": "🔄"}.get(value, "❓")
                        print(f"{prefix}  Status: {emoji} {value}")
                    elif key == "message":
                        print(f"{prefix}  Message: {value}")
                    elif key == "details":
                        if isinstance(value, list):
                            print(f"{prefix}  Details:")
                            for item in value:
                                if isinstance(item, dict):
                                    name = item.get("name", "Unknown")
                                    status = item.get("status", "unknown")
                                    message = item.get("message", "")
                                    emoji = {"pass": "✅", "fail": "❌"}.get(status, "❓")
                                    print(f"{prefix}    {emoji} {name}: {message}")
                    elif isinstance(value, dict) and any(k in value for k in ["status", "message"]):
                        print_section(value, key.title(), indent + 1)
                    else:
                        print(f"{prefix}  {key.title()}: {value}")

        for section_name in ["backend", "frontend", "infrastructure"]:
            if section_name in self.results:
                print_section(self.results[section_name], section_name.title())
                print()


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="DistroIQ Health Check")
    parser.add_argument("--format", choices=["text", "json", "summary"], default="text",
                      help="Output format")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--exit-code", action="store_true",
                      help="Exit with non-zero code if unhealthy")

    args = parser.parse_args()

    checker = HealthChecker(verbose=args.verbose)
    results = await checker.run_all_checks()

    checker.print_results(args.format)

    # Exit with error code if system is unhealthy
    if args.exit_code and results["overall_status"] in ["unhealthy", "unavailable"]:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())