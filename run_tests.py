#!/usr/bin/env python3
"""
Test runner script for the Mergington High School API.
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Run tests with various options."""
    script_dir = Path(__file__).parent
    venv_python = script_dir / ".venv" / "bin" / "python"
    
    if not venv_python.exists():
        print("❌ Virtual environment not found. Please run 'python -m venv .venv' first.")
        sys.exit(1)
    
    # Change to project directory
    os.chdir(script_dir)
    
    # Default command
    cmd = [str(venv_python), "-m", "pytest", "tests/", "-v"]
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "coverage":
            cmd.extend(["--cov=src", "--cov-report=term-missing", "--cov-report=html"])
            print("🧪 Running tests with coverage report...")
        elif sys.argv[1] == "fast":
            cmd.extend(["-x"])  # Stop on first failure
            print("🚀 Running tests in fast mode (stop on first failure)...")
        elif sys.argv[1] == "help":
            print("Usage: python run_tests.py [option]")
            print("Options:")
            print("  coverage  - Run with coverage report")
            print("  fast      - Stop on first failure")
            print("  help      - Show this help message")
            return
        else:
            print(f"❌ Unknown option: {sys.argv[1]}")
            print("Run 'python run_tests.py help' for usage information.")
            sys.exit(1)
    else:
        print("🧪 Running all tests...")
    
    # Run the tests
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("✅ All tests passed!")
        if len(sys.argv) > 1 and sys.argv[1] == "coverage":
            print("📊 Coverage report generated in htmlcov/index.html")
    else:
        print("❌ Some tests failed!")
        sys.exit(result.returncode)

if __name__ == "__main__":
    main()