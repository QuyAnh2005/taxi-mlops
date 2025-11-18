"""Statistical analysis utilities for experiment results"""

from typing import Any

import numpy as np
from scipy import stats


class StatisticalAnalyzer:
    """Perform statistical analysis on experiment results"""

    @staticmethod
    def compute_summary_statistics(values: list[float]) -> dict[str, float]:
        """
        Compute summary statistics for a list of values

        Args:
            values: List of numeric values

        Returns:
            Dictionary with summary statistics
        """
        if not values:
            return {}

        arr = np.array(values)
        return {
            "mean": float(np.mean(arr)),
            "median": float(np.median(arr)),
            "std": float(np.std(arr)),
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
            "q25": float(np.percentile(arr, 25)),
            "q75": float(np.percentile(arr, 75)),
            "count": len(values),
        }

    @staticmethod
    def t_test(
        group1: list[float], group2: list[float], alternative: str = "two-sided"
    ) -> dict[str, Any]:
        """
        Perform independent samples t-test

        Args:
            group1: First group of values
            group2: Second group of values
            alternative: Alternative hypothesis ('two-sided', 'less', 'greater')

        Returns:
            Dictionary with test results
        """
        try:
            statistic, pvalue = stats.ttest_ind(group1, group2, alternative=alternative)
            return {
                "statistic": float(statistic),
                "pvalue": float(pvalue),
                "significant": pvalue < 0.05,
                "alternative": alternative,
            }
        except Exception as e:
            return {
                "statistic": None,
                "pvalue": None,
                "significant": False,
                "error": str(e),
            }

    @staticmethod
    def mann_whitney_u_test(
        group1: list[float], group2: list[float], alternative: str = "two-sided"
    ) -> dict[str, Any]:
        """
        Perform Mann-Whitney U test (non-parametric)

        Args:
            group1: First group of values
            group2: Second group of values
            alternative: Alternative hypothesis ('two-sided', 'less', 'greater')

        Returns:
            Dictionary with test results
        """
        try:
            statistic, pvalue = stats.mannwhitneyu(
                group1, group2, alternative=alternative
            )
            return {
                "statistic": float(statistic),
                "pvalue": float(pvalue),
                "significant": pvalue < 0.05,
                "alternative": alternative,
            }
        except Exception as e:
            return {
                "statistic": None,
                "pvalue": None,
                "significant": False,
                "error": str(e),
            }

    @staticmethod
    def compare_groups(
        group1: list[float],
        group2: list[float],
        group1_name: str = "Group 1",
        group2_name: str = "Group 2",
    ) -> dict[str, Any]:
        """
        Comprehensive comparison of two groups

        Args:
            group1: First group of values
            group2: Second group of values
            group1_name: Name for first group
            group2_name: Name for second group

        Returns:
            Dictionary with comparison results
        """
        stats1 = StatisticalAnalyzer.compute_summary_statistics(group1)
        stats2 = StatisticalAnalyzer.compute_summary_statistics(group2)

        # Perform statistical tests
        t_test_result = StatisticalAnalyzer.t_test(group1, group2)
        mw_test_result = StatisticalAnalyzer.mann_whitney_u_test(group1, group2)

        # Effect size (Cohen's d)
        pooled_std = np.sqrt(
            (np.var(group1) + np.var(group2)) / 2
        )
        cohens_d = (
            (np.mean(group1) - np.mean(group2)) / pooled_std
            if pooled_std > 0
            else 0.0
        )

        return {
            group1_name: stats1,
            group2_name: stats2,
            "difference": {
                "mean_diff": stats1["mean"] - stats2["mean"],
                "percent_diff": (
                    (stats1["mean"] - stats2["mean"]) / stats2["mean"] * 100
                    if stats2["mean"] != 0
                    else 0.0
                ),
            },
            "t_test": t_test_result,
            "mann_whitney_u_test": mw_test_result,
            "effect_size_cohens_d": float(cohens_d),
        }

    @staticmethod
    def analyze_parameter_sweep(
        parameter_values: list[Any],
        metric_values: list[float],
        parameter_name: str = "parameter",
    ) -> dict[str, Any]:
        """
        Analyze results from a parameter sweep

        Args:
            parameter_values: List of parameter values tested
            metric_values: Corresponding metric values
            parameter_name: Name of the parameter

        Returns:
            Dictionary with analysis results
        """
        if len(parameter_values) != len(metric_values):
            return {"error": "Parameter and metric lists must have same length"}

        # Find best parameter value
        best_idx = np.argmax(metric_values)
        best_parameter = parameter_values[best_idx]
        best_metric = metric_values[best_idx]

        # Compute correlation
        try:
            # Convert to numeric if possible
            param_numeric = [float(p) for p in parameter_values]
            correlation, pvalue = stats.pearsonr(param_numeric, metric_values)
        except Exception:
            correlation = None
            pvalue = None

        return {
            "best_parameter": best_parameter,
            "best_metric_value": float(best_metric),
            "correlation": float(correlation) if correlation is not None else None,
            "correlation_pvalue": float(pvalue) if pvalue is not None else None,
            "parameter_range": {
                "min": min(parameter_values),
                "max": max(parameter_values),
            },
            "metric_range": {
                "min": float(np.min(metric_values)),
                "max": float(np.max(metric_values)),
            },
        }

