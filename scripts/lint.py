#!/usr/bin/env python3
import subprocess
import sys

def run_linters():
    """Run all linting checks."""
    print("Running Black...")
    subprocess.run(["black", "app"])
    
    print("\nRunning Flake8...")
    subprocess.run(["flake8", "app"])
    
    print("\nRunning Pylint...")
    subprocess.run(["pylint", "app"])

if __name__ == "__main__":
    sys.exit(run_linters()) 