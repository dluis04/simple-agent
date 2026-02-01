"""
Setup Verification Script.
Checks if your environment is ready to run the agent.
"""

import importlib.util
import sys


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    print(f"[OK] Python Version: {version.major}.{version.minor}.{version.micro}")

    if version.major == 3 and version.minor >= 9:
        print("     Python version is compatible (3.9+)")
        return True
    else:
        print("     [FAIL] Python 3.9+ required")
        return False


def check_package(package_name):
    """Check if a package is installed."""
    spec = importlib.util.find_spec(package_name)
    if spec is not None:
        try:
            module = importlib.import_module(package_name)
            version = getattr(module, "__version__", "unknown")
            print(f"[OK] {package_name}: {version}")
            return True
        except ImportError:
            print(f"[FAIL] {package_name}: Import failed")
            return False
    else:
        print(f"[FAIL] {package_name}: Not installed")
        return False


def check_env_file():
    """Check if .env file exists and has API key."""
    import os

    # Check multiple possible locations
    possible_paths = [
        ".env",
        "../.env",
        os.path.join(os.path.dirname(__file__), "..", ".env"),
    ]

    env_path = None
    for path in possible_paths:
        if os.path.exists(path):
            env_path = path
            break

    if env_path:
        print(f"[OK] .env file exists at {env_path}")

        from dotenv import load_dotenv

        load_dotenv(env_path)
        api_key = os.getenv("ANTHROPIC_API_KEY")

        if api_key and api_key != "your_api_key_here":
            print(f"     API key configured (length: {len(api_key)})")
            return True
        else:
            print("     [WARN] API key not set or using example value")
            return False
    else:
        print("[FAIL] .env file not found")
        print("     -> Run: cp .env.example .env")
        print("     -> Then edit .env with your API key")
        return False


def check_package_import():
    """Check if simple_agent package can be imported."""
    import os
    import sys

    # Add src to path
    src_path = os.path.join(os.path.dirname(__file__), "..", "src")
    sys.path.insert(0, src_path)

    try:
        from simple_agent import SimpleAgent, AdvancedAgent  # noqa: F401

        print("[OK] simple_agent package imports correctly")
        return True
    except ImportError as e:
        print(f"[FAIL] Cannot import simple_agent: {e}")
        return False


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Simple Agent - Setup Verification")
    print("=" * 60)
    print()

    checks = []

    print("1. Python Environment")
    checks.append(check_python_version())
    print()

    print("2. Required Packages")
    checks.append(check_package("anthropic"))
    checks.append(check_package("dotenv"))
    print()

    print("3. Configuration")
    checks.append(check_env_file())
    print()

    print("4. Package Structure")
    checks.append(check_package_import())
    print()

    print("=" * 60)
    if all(checks):
        print("[SUCCESS] All checks passed!")
        print()
        print("Run the agents:")
        print("  uv run simple-agent       # Simple agent")
        print("  uv run advanced-agent     # Advanced agent")
        print("  uv run python examples/demo.py  # Demo")
    else:
        print("[WARN] Some checks failed. Please fix the issues above.")
        print()
        print("To install dependencies:")
        print("  uv sync")
    print("=" * 60)


if __name__ == "__main__":
    main()
