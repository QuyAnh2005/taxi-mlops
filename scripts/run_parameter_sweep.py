#!/usr/bin/env python3
"""Script to run parameter sweep experiments"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.workflows.parameter_sweep import parameter_sweep_flow


def main():
    parser = argparse.ArgumentParser(description="Run parameter sweep")
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
        "--eps-values",
        type=float,
        nargs="+",
        default=[0.1, 0.3, 0.5, 0.7, 1.0],
        help="Eps values to test",
    )
    parser.add_argument(
        "--min-samples-values",
        type=int,
        nargs="+",
        default=[3, 5, 10, 15],
        help="Min_samples values to test",
    )
    parser.add_argument(
        "--coordinate-type",
        type=str,
        choices=["pickup", "dropoff", "both"],
        default="both",
        help="Type of coordinates to extract",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=5000,
        help="Maximum number of samples",
    )
    parser.add_argument(
        "--metric",
        type=str,
        choices=["overall_score", "silhouette_score", "runtime_seconds"],
        default="overall_score",
        help="Metric to optimize",
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

    result = parameter_sweep_flow(
        data_source=data_source,
        adapter_type=args.adapter_type,
        eps_values=args.eps_values,
        min_samples_values=args.min_samples_values,
        coordinate_type=args.coordinate_type,
        max_samples=args.max_samples,
        use_minio=use_minio,
        metric=args.metric,
        **kwargs,
    )

    print("\n" + "=" * 70)
    print("Parameter Sweep Results")
    print("=" * 70)
    print(f"Sweep ID: {result['sweep_id']}")
    print(f"Adapter Type: {result['adapter_type']}")
    print(f"Number of Experiments: {result['num_experiments']}")
    print(f"\nBest Parameters:")
    best = result["best_parameters"]
    print(f"  eps: {best['eps']}")
    print(f"  min_samples: {best['min_samples']}")
    print(f"  {args.metric}: {best['metric_value']:.4f}")
    print("=" * 70)


if __name__ == "__main__":
    main()

