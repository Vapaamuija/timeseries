#!/usr/bin/env python3
"""
Development script for weather-tool
Provides convenient commands for code formatting, linting, and testing.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def format_code() -> bool:
    """Format code with black and isort."""
    success = True
    success &= run_command(
        ["black", "src/", "tests/", "scripts/", "bin/", "dev.py"],
        "Formatting with black",
    )
    success &= run_command(
        ["isort", "src/", "tests/", "scripts/", "bin/", "dev.py"],
        "Sorting imports with isort",
    )
    return success


def lint_code() -> bool:
    """Run all linting tools."""
    success = True
    success &= run_command(
        ["black", "--check", "src/", "tests/", "scripts/", "bin/", "dev.py"],
        "Checking black formatting",
    )
    success &= run_command(
        ["isort", "--check-only", "src/", "tests/", "scripts/", "bin/", "dev.py"],
        "Checking isort",
    )
    success &= run_command(
        ["flake8", "src/", "tests/", "scripts/", "bin/", "dev.py"], "Running flake8"
    )
    success &= run_command(["mypy", "src/weather_tool/"], "Running mypy type checking")
    success &= run_command(
        ["bandit", "-r", "src/", "-f", "json", "-o", "bandit-report.json"],
        "Running bandit security check",
    )
    return success


def run_tests() -> bool:
    """Run tests with pytest."""
    return run_command(["pytest", "tests/", "-v"], "Running tests")


def run_tests_with_coverage() -> bool:
    """Run tests with coverage."""
    return run_command(
        [
            "pytest",
            "tests/",
            "--cov=weather_tool",
            "--cov-report=html",
            "--cov-report=term-missing",
        ],
        "Running tests with coverage",
    )


def install_pre_commit() -> bool:
    """Install pre-commit hooks."""
    return run_command(["pre-commit", "install"], "Installing pre-commit hooks")


def run_pre_commit() -> bool:
    """Run pre-commit on all files."""
    return run_command(["pre-commit", "run", "--all-files"], "Running pre-commit hooks")


def clean_build() -> bool:
    """Clean build artifacts."""
    import shutil

    paths_to_clean = [
        "build/",
        "dist/",
        "*.egg-info/",
        "src/*.egg-info/",
        ".pytest_cache/",
        ".coverage",
        "htmlcov/",
        "bandit-report.json",
    ]

    print("🧹 Cleaning build artifacts...")
    for pattern in paths_to_clean:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"  Removed directory: {path}")
            else:
                path.unlink()
                print(f"  Removed file: {path}")

    # Clean __pycache__ directories
    for pycache in Path(".").rglob("__pycache__"):
        shutil.rmtree(pycache)
        print(f"  Removed __pycache__: {pycache}")

    # Clean .pyc files
    for pyc in Path(".").rglob("*.pyc"):
        pyc.unlink()
        print(f"  Removed .pyc file: {pyc}")

    print("✅ Cleanup complete!")
    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Development tools for weather-tool")
    parser.add_argument(
        "command",
        choices=[
            "format",
            "lint",
            "test",
            "test-cov",
            "pre-commit-install",
            "pre-commit-run",
            "clean",
            "all",
        ],
        help="Command to run",
    )

    args = parser.parse_args()

    if args.command == "format":
        success = format_code()
    elif args.command == "lint":
        success = lint_code()
    elif args.command == "test":
        success = run_tests()
    elif args.command == "test-cov":
        success = run_tests_with_coverage()
    elif args.command == "pre-commit-install":
        success = install_pre_commit()
    elif args.command == "pre-commit-run":
        success = run_pre_commit()
    elif args.command == "clean":
        success = clean_build()
    elif args.command == "all":
        success = True
        success &= format_code()
        success &= lint_code()
        success &= run_tests()

    if success:
        print("\n🎉 All operations completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Some operations failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
