#!/usr/bin/env python3
"""Script to compare sequential vs parallel DBSCAN adapters"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.workflows.experiment_pipeline import experiment_pipeline


def main():
    parser = argparse.ArgumentParser(description="Compare DBSCAN adapters")
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

    print("Running sequential DBSCAN experiment...")
    result_seq = experiment_pipeline(
        data_source=data_source,
        adapter_type="sklearn",
        eps=args.eps,
        min_samples=args.min_samples,
        coordinate_type=args.coordinate_type,
        use_location_ids=args.use_location_ids,
        max_samples=args.max_samples,
        use_minio=use_minio,
    )

    print("\nRunning parallel DBSCAN experiment...")
    result_par = experiment_pipeline(
        data_source=data_source,
        adapter_type="sklearn_parallel",
        eps=args.eps,
        min_samples=args.min_samples,
        coordinate_type=args.coordinate_type,
        use_location_ids=args.use_location_ids,
        max_samples=args.max_samples,
        use_minio=use_minio,
        n_jobs=args.n_jobs,
    )

    print("\n" + "=" * 70)
    print("Comparison Results")
    print("=" * 70)

    print("\nSequential DBSCAN:")
    print(f"  Experiment ID: {result_seq['experiment_id']}")
    print(f"  Clusters: {result_seq['metrics']['n_clusters']}")
    print(f"  Noise points: {result_seq['metrics']['n_noise']}")
    print(f"  Time: {result_seq['metrics']['elapsed_time_seconds']:.2f}s")

    print("\nParallel DBSCAN:")
    print(f"  Experiment ID: {result_par['experiment_id']}")
    print(f"  Clusters: {result_par['metrics']['n_clusters']}")
    print(f"  Noise points: {result_par['metrics']['n_noise']}")
    print(f"  Time: {result_par['metrics']['elapsed_time_seconds']:.2f}s")

    speedup = (
        result_seq["metrics"]["elapsed_time_seconds"]
        / result_par["metrics"]["elapsed_time_seconds"]
    )
    print(f"\nSpeedup: {speedup:.2f}x")

    print("=" * 70)


if __name__ == "__main__":
    main()

