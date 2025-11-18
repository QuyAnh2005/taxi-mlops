#!/usr/bin/env python3
"""Script to aggregate and analyze experiment results"""

import argparse
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.workflows.scheduled_workflows import aggregate_results_flow


def main():
    parser = argparse.ArgumentParser(description="Aggregate experiment results")
    parser.add_argument(
        "--adapter-type",
        type=str,
        choices=["sklearn", "sklearn_parallel"],
        default=None,
        help="Filter by adapter type (None = all)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to look back",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path (JSON format)",
    )

    args = parser.parse_args()

    result = aggregate_results_flow(
        adapter_type=args.adapter_type, days=args.days
    )

    print("\n" + "=" * 70)
    print("Aggregated Results")
    print("=" * 70)
    print(f"Number of Experiments: {result.get('num_experiments', 0)}")

    if "aggregated_metrics" in result:
        print("\nAggregated Metrics:")
        agg = result["aggregated_metrics"]
        if "quality" in agg:
            print("  Quality Metrics:")
            if "silhouette" in agg["quality"]:
                sil = agg["quality"]["silhouette"]
                print(f"    Silhouette Score: {sil.get('mean', 0):.4f} ± {sil.get('std', 0):.4f}")
        if "performance" in agg:
            print("  Performance Metrics:")
            if "runtime" in agg["performance"]:
                rt = agg["performance"]["runtime"]
                print(f"    Runtime: {rt.get('mean', 0):.4f}s ± {rt.get('std', 0):.4f}s")

    if "statistical_analysis" in result:
        print("\nStatistical Analysis:")
        stats = result["statistical_analysis"]
        if "silhouette_stats" in stats:
            print(f"  Silhouette: {stats['silhouette_stats'].get('mean', 0):.4f}")

    print("=" * 70)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()

