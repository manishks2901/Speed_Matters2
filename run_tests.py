#!/usr/bin/env python3
"""
Test runner script for the Speed_Matters video processing application.

This script provides convenient ways to run different types of tests with
appropriate configurations and reporting.
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and handle errors"""
    if description:
        print(f"🔄 {description}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"❌ Command not found: {cmd[0]}")
        print("Please ensure pytest is installed: pip install -r requirements.txt")
        return False


def check_dependencies():
    """Check if required testing dependencies are available"""
    print("🔍 Checking test dependencies...")
    
    try:
        import pytest
        import numpy
        import scipy
        print("✅ All core dependencies available")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies: pip install -r requirements.txt")
        return False


def run_unit_tests(verbose=False, coverage=False):
    """Run unit tests"""
    cmd = ["python", "-m", "pytest", "tests/"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=variant", "--cov-report=html", "--cov-report=term"])
    
    # Add markers to run only unit tests
    cmd.extend(["-m", "not slow"])
    
    return run_command(cmd, "Running unit tests")


def run_integration_tests(verbose=False):
    """Run integration tests"""
    cmd = ["python", "-m", "pytest", "tests/test_integration.py"]
    
    if verbose:
        cmd.append("-v")
    
    return run_command(cmd, "Running integration tests")


def run_performance_tests(verbose=False):
    """Run performance tests"""
    cmd = ["python", "-m", "pytest", "tests/", "-m", "slow"]
    
    if verbose:
        cmd.append("-v")
    
    return run_command(cmd, "Running performance tests")


def run_all_tests(verbose=False, coverage=False):
    """Run all tests"""
    cmd = ["python", "-m", "pytest", "tests/"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=variant", "--cov-report=html", "--cov-report=term"])
    
    return run_command(cmd, "Running all tests")


def run_specific_test(test_path, verbose=False):
    """Run a specific test file or test function"""
    cmd = ["python", "-m", "pytest", test_path]
    
    if verbose:
        cmd.append("-v")
    
    return run_command(cmd, f"Running specific test: {test_path}")


def lint_tests():
    """Run linting on test files"""
    print("🔍 Checking test code quality...")
    
    # Try to run flake8 if available
    try:
        cmd = ["python", "-m", "flake8", "tests/", "--max-line-length=100"]
        return run_command(cmd, "Running flake8 linting")
    except:
        print("⚠️  flake8 not available, skipping linting")
        return True


def clean_test_artifacts():
    """Clean up test artifacts"""
    print("🧹 Cleaning test artifacts...")
    
    artifacts = [
        ".pytest_cache",
        "htmlcov",
        ".coverage",
        "__pycache__",
        "tests/__pycache__",
    ]
    
    import shutil
    
    for artifact in artifacts:
        if os.path.exists(artifact):
            if os.path.isdir(artifact):
                shutil.rmtree(artifact)
                print(f"🗑️  Removed directory: {artifact}")
            else:
                os.remove(artifact)
                print(f"🗑️  Removed file: {artifact}")
    
    print("✅ Cleanup complete")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Test runner for Speed_Matters")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--performance", action="store_true", help="Run performance tests only")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--test", type=str, help="Run specific test file or function")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage reporting")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--lint", action="store_true", help="Run linting on test code")
    parser.add_argument("--clean", action="store_true", help="Clean test artifacts")
    parser.add_argument("--check-deps", action="store_true", help="Check test dependencies")
    
    args = parser.parse_args()
    
    # Change to project root directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print("🚀 Speed_Matters Test Runner")
    print(f"📁 Working directory: {os.getcwd()}")
    print()
    
    success = True
    
    if args.clean:
        clean_test_artifacts()
        return
    
    if args.check_deps:
        success = check_dependencies()
        if not success:
            sys.exit(1)
        return
    
    if args.lint:
        success = lint_tests()
        if not success:
            sys.exit(1)
        return
    
    # Check dependencies before running tests
    if not check_dependencies():
        sys.exit(1)
    
    if args.test:
        success = run_specific_test(args.test, args.verbose)
    elif args.unit:
        success = run_unit_tests(args.verbose, args.coverage)
    elif args.integration:
        success = run_integration_tests(args.verbose)
    elif args.performance:
        success = run_performance_tests(args.verbose)
    elif args.all:
        success = run_all_tests(args.verbose, args.coverage)
    else:
        # Default: run unit tests
        print("No specific test type selected, running unit tests...")
        success = run_unit_tests(args.verbose, args.coverage)
    
    if success:
        print("\n✅ All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()