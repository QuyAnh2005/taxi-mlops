#!/usr/bin/env python3
"""Script to set up Prefect connection"""

import subprocess
import sys


def main():
    """Configure Prefect to connect to the server"""
    print("Setting up Prefect connection...")
    
    # Set API URL
    result = subprocess.run(
        ["prefect", "config", "set", "PREFECT_API_URL=http://localhost:4200/api"],
        capture_output=True,
        text=True,
    )
    
    if result.returncode == 0:
        print("✓ Prefect API URL configured")
    else:
        print(f"✗ Error configuring Prefect: {result.stderr}")
        return 1
    
    # Verify connection
    result = subprocess.run(
        ["prefect", "config", "view"],
        capture_output=True,
        text=True,
    )
    
    print("\nCurrent Prefect configuration:")
    print(result.stdout)
    
    # Test connection
    print("\nTesting connection to Prefect server...")
    result = subprocess.run(
        ["curl", "-s", "http://localhost:4200/api/health"],
        capture_output=True,
        text=True,
    )
    
    if result.returncode == 0 and "true" in result.stdout.lower():
        print("✓ Prefect server is accessible")
    else:
        print("✗ Prefect server is not accessible")
        print("  Make sure Docker services are running: docker-compose up -d")
        return 1
    
    print("\n" + "=" * 50)
    print("Prefect Setup Complete!")
    print("=" * 50)
    print("\nAccess Prefect UI at: http://localhost:4200")
    print("\nTo see flows in the UI, you need to:")
    print("1. Run a flow (e.g., python scripts/run_experiment.py)")
    print("2. Or deploy a flow: prefect deploy src/workflows/experiment_pipeline.py:experiment_pipeline")
    print("\n" + "=" * 50)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

