#!/usr/bin/env python3
"""Quick start script to deploy and run a flow in Prefect"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.workflows.experiment_pipeline import experiment_pipeline


def main():
    """Run a simple experiment to populate Prefect UI"""
    print("Running experiment to populate Prefect UI...")
    print("=" * 50)
    
    result = experiment_pipeline(
        data_source="yellow_tripdata_2025-09.parquet",
        adapter_type="sklearn",
        eps=0.5,
        min_samples=5,
        max_samples=1000,  # Small sample for quick test
        use_minio=True,  # Load from MinIO
    )
    
    print("\n" + "=" * 50)
    print("Experiment completed!")
    print("=" * 50)
    print(f"Experiment ID: {result['experiment_id']}")
    print(f"Check Prefect UI at: http://localhost:4200")
    print("Navigate to 'Flow Runs' to see the execution")
    print("=" * 50)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

