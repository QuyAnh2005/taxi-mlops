#!/usr/bin/env python3
"""Script to run DBSCAN experiments"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.workflows.experiment_pipeline import experiment_pipeline


def main():
    parser = argparse.ArgumentParser(
        description="Run DBSCAN experiment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use MinIO (default)
  python scripts/run_experiment.py --data-object yellow_tripdata_2025-09.parquet

  # Use local file
  python scripts/run_experiment.py --data-source data/yellow_tripdata_2025-09.parquet --no-minio
        """,
    )
    parser.add_argument(
        "--data-source",
        type=str,
        default="yellow_tripdata_2025-09.parquet",
        help="Object name in MinIO or local file path",
    )
    parser.add_argument(
        "--data-object",
        type=str,
        default=None,
        help="Object name in MinIO (alias for --data-source, implies --use-minio)",
    )
    parser.add_argument(
        "--no-minio",
        dest="use_minio",
        action="store_false",
        default=True,
        help="Disable MinIO and use local file system",
    )
    parser.add_argument(
        "--adapter-type",
        type=str,
        choices=["sklearn", "sklearn_parallel"],
        default="sklearn",
        help="Adapter type to use",
    )
    parser.add_argument(
        "--eps",
        type=float,
        default=0.5,
        help="DBSCAN eps parameter",
    )
    parser.add_argument(
        "--min-samples",
        type=int,
        default=5,
        help="DBSCAN min_samples parameter",
    )
    parser.add_argument(
        "--coordinate-type",
        type=str,
        choices=["pickup", "dropoff"],
        default="pickup",
        help="Type of coordinates to extract (only 2D coordinates: pickup or dropoff)",
    )
    parser.add_argument(
        "--use-location-ids",
        action="store_true",
        default=True,
        help="Use location IDs when coordinates not available",
    )
    parser.add_argument(
        "--no-location-ids",
        dest="use_location_ids",
        action="store_false",
        help="Don't use location IDs (fail if coordinates not found)",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=5000,
        help="Maximum number of samples to use (for testing)",
    )
    parser.add_argument(
        "--n-jobs",
        type=int,
        default=-1,
        help="Number of parallel jobs (for parallel adapter)",
    )

    args = parser.parse_args()

    # Use data_object if provided, otherwise use data_source
    data_source = args.data_object if args.data_object else args.data_source
    # If data_object is provided, force use_minio
    use_minio = args.use_minio and (args.data_object is not None or args.use_minio)

    kwargs = {}
    if args.adapter_type == "sklearn_parallel":
        kwargs["n_jobs"] = args.n_jobs

    result = experiment_pipeline(
        data_source=data_source,
        adapter_type=args.adapter_type,
        eps=args.eps,
        min_samples=args.min_samples,
        coordinate_type=args.coordinate_type,
        use_location_ids=args.use_location_ids,
        max_samples=args.max_samples,
        use_minio=use_minio,
        **kwargs,
    )

    print("\n" + "=" * 50)
    print("Experiment Results")
    print("=" * 50)
    print(f"Experiment ID: {result['experiment_id']}")
    print(f"Adapter Type: {result['adapter_type']}")
    print(f"\nMetrics:")
    for key, value in result["metrics"].items():
        print(f"  {key}: {value}")
    print(f"\nParameters:")
    for key, value in result["parameters"].items():
        print(f"  {key}: {value}")
    print("=" * 50)


if __name__ == "__main__":
    main()

