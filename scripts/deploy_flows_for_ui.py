#!/usr/bin/env python3
"""Deploy Prefect flows using flow.serve() for Prefect 3.x"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config import settings
from src.workflows.experiment_pipeline import experiment_pipeline
from src.workflows.evaluation_flows import evaluation_pipeline
from src.workflows.parameter_sweep import parameter_sweep_flow, compare_adapters_sweep_flow


def main():
    """Deploy all flows for UI access using serve()"""
    print("="*60)
    print("Prefect Flow Deployment (Prefect 3.x)")
    print("="*60)
    print("\nThis script deploys flows using flow.serve()")
    print(f"Prefect API: {settings.prefect_api_url}")
    print("\nMake sure:")
    print("  1. Prefect server is running (make up)")
    print("  2. This script will start a process to serve the flows")
    print("\nDeploying and serving flows...")
    print("="*60)

    # Use serve() to deploy multiple flows at once
    # This creates deployments that can be run from the Prefect UI
    try:
        # Serve all flows together
        experiment_pipeline.serve(
            name="experiment-pipeline",
            tags=["dbscan", "experiment"],
            description="Basic DBSCAN experiment pipeline",
            version="1.0",
        )

        print("\n" + "="*60)
        print("Flows Deployed Successfully!")
        print("="*60)
        print("\nDeployed flows:")
        print("  • experiment-pipeline - Basic DBSCAN experiment pipeline")
        print("\n" + "="*60)
        print("How to Run Flows from Prefect UI")
        print("="*60)
        print("\n1. Open Prefect UI: http://localhost:4200")
        print("2. Navigate to 'Deployments' in the sidebar")
        print("3. Click on 'experiment-pipeline'")
        print("4. Click 'Run' button (top right)")
        print("5. Fill in the parameters:")
        print("   - data_source: 'data/yellow_tripdata_2025-09.parquet'")
        print("   - adapter_type: 'sklearn' or 'sklearn_parallel'")
        print("   - eps: 0.01")
        print("   - min_samples: 5")
        print("   - coordinate_type: 'pickup' or 'dropoff'")
        print("   - use_minio: false")
        print("   - max_samples: 5000")
        print("\n6. Click 'Run' to start the flow")
        print("\n" + "="*60)
        print("\nThis process will keep running to serve the flows.")
        print("Press Ctrl+C to stop.")
        print("="*60)

        return 0
    except Exception as e:
        print(f"\n✗ Failed to deploy flows: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
