"""Main evaluator class that combines all metrics"""

from typing import Any

import numpy as np

from .performance_metrics import PerformanceMetrics
from .quality_metrics import QualityMetrics
from .statistical_analysis import StatisticalAnalyzer


class ExperimentEvaluator:
    """Comprehensive evaluator for DBSCAN experiments"""

    def __init__(self):
        """Initialize the evaluator"""
        self.performance_metrics = PerformanceMetrics()
        self.quality_metrics = QualityMetrics()
        self.statistical_analyzer = StatisticalAnalyzer()

    def evaluate_experiment(
        self,
        X: np.ndarray,
        labels: np.ndarray,
        performance_metrics: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Evaluate a single experiment with all metrics

        Args:
            X: Feature array
            labels: Cluster labels
            performance_metrics: Optional pre-computed performance metrics

        Returns:
            Dictionary with all evaluation metrics
        """
        evaluation = {}

        # Quality metrics
        quality_metrics = QualityMetrics.compute_all_quality_metrics(X, labels)
        evaluation["quality"] = quality_metrics

        # Performance metrics
        if performance_metrics:
            evaluation["performance"] = performance_metrics
        else:
            evaluation["performance"] = {}

        # Overall score (weighted combination)
        evaluation["overall_score"] = self._compute_overall_score(
            quality_metrics, evaluation["performance"]
        )

        return evaluation

    def _compute_overall_score(
        self,
        quality_metrics: dict[str, Any],
        performance_metrics: dict[str, Any],
    ) -> float:
        """
        Compute overall score from quality and performance metrics

        Args:
            quality_metrics: Quality metrics dictionary
            performance_metrics: Performance metrics dictionary

        Returns:
            Overall score (0-1, higher is better)
        """
        # Normalize quality metrics
        silhouette = max(0, quality_metrics.get("silhouette_score", -1))
        db_score = quality_metrics.get("davies_bouldin_score", float("inf"))
        db_normalized = 1.0 / (1.0 + db_score) if db_score != float("inf") else 0.0

        # Quality component (0-1)
        quality_score = (silhouette + db_normalized) / 2.0

        # Performance component (inverse of normalized time)
        runtime = performance_metrics.get("elapsed_time_seconds", 0)
        if runtime > 0:
            # Normalize to 0-1 (assuming max reasonable time is 3600s)
            perf_score = max(0, 1.0 - (runtime / 3600.0))
        else:
            perf_score = 1.0

        # Weighted combination (70% quality, 30% performance)
        overall = 0.7 * quality_score + 0.3 * perf_score

        return float(overall)

    def compare_experiments(
        self,
        experiment1: dict[str, Any],
        experiment2: dict[str, Any],
        name1: str = "Experiment 1",
        name2: str = "Experiment 2",
    ) -> dict[str, Any]:
        """
        Compare two experiments

        Args:
            experiment1: First experiment results
            experiment2: Second experiment results
            name1: Name for first experiment
            name2: Name for second experiment

        Returns:
            Dictionary with comparison results
        """
        comparison = {}

        # Compare quality metrics
        quality1 = experiment1.get("quality", {})
        quality2 = experiment2.get("quality", {})

        comparison["quality"] = {
            "silhouette_diff": quality1.get("silhouette_score", 0)
            - quality2.get("silhouette_score", 0),
            "davies_bouldin_diff": quality1.get("davies_bouldin_score", float("inf"))
            - quality2.get("davies_bouldin_score", float("inf")),
            "calinski_harabasz_diff": quality1.get("calinski_harabasz_score", 0)
            - quality2.get("calinski_harabasz_score", 0),
            "n_clusters_diff": quality1.get("n_clusters", 0)
            - quality2.get("n_clusters", 0),
        }

        # Compare performance metrics
        perf1 = experiment1.get("performance", {})
        perf2 = experiment2.get("performance", {})

        runtime1 = perf1.get("elapsed_time_seconds", 0)
        runtime2 = perf2.get("elapsed_time_seconds", 0)

        comparison["performance"] = {
            "runtime_diff_seconds": runtime1 - runtime2,
            "runtime_speedup": runtime2 / runtime1 if runtime1 > 0 else 0.0,
            "memory_diff_mb": perf1.get("memory_delta_mb", 0)
            - perf2.get("memory_delta_mb", 0),
        }

        # Overall comparison
        score1 = experiment1.get("overall_score", 0)
        score2 = experiment2.get("overall_score", 0)

        comparison["overall"] = {
            "score_diff": score1 - score2,
            "winner": name1 if score1 > score2 else name2,
        }

        return comparison

    def aggregate_evaluations(
        self, evaluations: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Aggregate multiple evaluations

        Args:
            evaluations: List of evaluation dictionaries

        Returns:
            Aggregated evaluation results
        """
        if not evaluations:
            return {}

        # Extract metrics
        silhouette_scores = [
            e.get("quality", {}).get("silhouette_score", -1) for e in evaluations
        ]
        db_scores = [
            e.get("quality", {}).get("davies_bouldin_score", float("inf"))
            for e in evaluations
        ]
        runtimes = [
            e.get("performance", {}).get("elapsed_time_seconds", 0)
            for e in evaluations
        ]
        overall_scores = [e.get("overall_score", 0) for e in evaluations]

        # Filter out invalid values
        silhouette_scores = [s for s in silhouette_scores if s >= -1]
        db_scores = [s for s in db_scores if s != float("inf")]

        return {
            "num_experiments": len(evaluations),
            "quality": {
                "silhouette": StatisticalAnalyzer.compute_summary_statistics(
                    silhouette_scores
                ),
                "davies_bouldin": StatisticalAnalyzer.compute_summary_statistics(
                    db_scores
                ),
            },
            "performance": {
                "runtime": StatisticalAnalyzer.compute_summary_statistics(runtimes),
            },
            "overall_score": StatisticalAnalyzer.compute_summary_statistics(
                overall_scores
            ),
        }

