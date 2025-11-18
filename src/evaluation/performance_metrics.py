"""Performance metrics for evaluating DBSCAN implementations"""

import os
import time
from typing import Any

import numpy as np
import psutil


class PerformanceMetrics:
    """Collect and compute performance metrics"""

    @staticmethod
    def measure_runtime(func, *args, **kwargs) -> tuple[Any, float]:
        """
        Measure execution time of a function

        Args:
            func: Function to measure
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function

        Returns:
            Tuple of (function_result, elapsed_time_seconds)
        """
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        return result, elapsed_time

    @staticmethod
    def get_memory_usage() -> dict[str, float]:
        """
        Get current memory usage statistics

        Returns:
            Dictionary with memory metrics in MB
        """
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        return {
            "memory_rss_mb": memory_info.rss / 1024 / 1024,  # Resident Set Size
            "memory_vms_mb": memory_info.vms / 1024 / 1024,  # Virtual Memory Size
            "memory_percent": process.memory_percent(),
        }

    @staticmethod
    def get_cpu_usage() -> dict[str, float]:
        """
        Get current CPU usage statistics

        Returns:
            Dictionary with CPU metrics
        """
        process = psutil.Process(os.getpid())
        return {
            "cpu_percent": process.cpu_percent(interval=0.1),
            "cpu_count": psutil.cpu_count(),
            "cpu_count_logical": psutil.cpu_count(logical=True),
        }

    @staticmethod
    def measure_with_resources(
        func, *args, **kwargs
    ) -> tuple[Any, dict[str, Any]]:
        """
        Measure function execution with resource usage

        Args:
            func: Function to measure
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function

        Returns:
            Tuple of (function_result, metrics_dict)
        """
        # Get initial resource usage
        initial_memory = PerformanceMetrics.get_memory_usage()
        initial_cpu = PerformanceMetrics.get_cpu_usage()

        # Measure execution time and get result
        result, elapsed_time = PerformanceMetrics.measure_runtime(func, *args, **kwargs)

        # Get final resource usage
        final_memory = PerformanceMetrics.get_memory_usage()
        final_cpu = PerformanceMetrics.get_cpu_usage()

        # Calculate deltas
        memory_delta = {
            "memory_rss_delta_mb": final_memory["memory_rss_mb"]
            - initial_memory["memory_rss_mb"],
            "memory_vms_delta_mb": final_memory["memory_vms_mb"]
            - initial_memory["memory_vms_mb"],
        }

        metrics = {
            "elapsed_time_seconds": elapsed_time,
            "initial_memory_mb": initial_memory["memory_rss_mb"],
            "final_memory_mb": final_memory["memory_rss_mb"],
            "memory_delta_mb": memory_delta["memory_rss_delta_mb"],
            "peak_memory_mb": final_memory["memory_rss_mb"],
            "cpu_percent": final_cpu["cpu_percent"],
            "cpu_count": final_cpu["cpu_count"],
        }

        return result, metrics

    @staticmethod
    def compute_scalability_metrics(
        runtimes: list[float], sample_sizes: list[int]
    ) -> dict[str, Any]:
        """
        Compute scalability metrics from multiple runs

        Args:
            runtimes: List of execution times in seconds
            sample_sizes: List of corresponding sample sizes

        Returns:
            Dictionary with scalability metrics
        """
        if len(runtimes) != len(sample_sizes) or len(runtimes) < 2:
            return {}

        runtimes = np.array(runtimes)
        sample_sizes = np.array(sample_sizes)

        # Compute time complexity approximation (O(n^p))
        # log(time) = p * log(n) + c
        log_times = np.log(runtimes + 1e-10)
        log_sizes = np.log(sample_sizes + 1e-10)

        # Linear regression to find exponent
        if len(log_sizes) > 1:
            p = np.polyfit(log_sizes, log_times, 1)[0]
        else:
            p = 0.0

        # Compute speedup (if multiple runs with different sizes)
        if len(runtimes) >= 2:
            speedup = runtimes[0] / runtimes[-1] if runtimes[-1] > 0 else 0.0
            efficiency = speedup / (sample_sizes[-1] / sample_sizes[0])
        else:
            speedup = 0.0
            efficiency = 0.0

        return {
            "complexity_exponent": float(p),
            "estimated_complexity": f"O(n^{p:.2f})",
            "speedup": float(speedup),
            "efficiency": float(efficiency),
            "avg_time_per_sample": float(np.mean(runtimes / sample_sizes)),
        }

    @staticmethod
    def aggregate_performance_metrics(
        metrics_list: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Aggregate performance metrics from multiple runs

        Args:
            metrics_list: List of metrics dictionaries

        Returns:
            Aggregated metrics with statistics
        """
        if not metrics_list:
            return {}

        # Extract metrics
        elapsed_times = [m.get("elapsed_time_seconds", 0) for m in metrics_list]
        memory_deltas = [
            m.get("memory_delta_mb", 0) for m in metrics_list
        ]
        cpu_percents = [m.get("cpu_percent", 0) for m in metrics_list]

        return {
            "num_runs": len(metrics_list),
            "runtime_mean": float(np.mean(elapsed_times)),
            "runtime_std": float(np.std(elapsed_times)),
            "runtime_min": float(np.min(elapsed_times)),
            "runtime_max": float(np.max(elapsed_times)),
            "memory_delta_mean_mb": float(np.mean(memory_deltas)),
            "memory_delta_std_mb": float(np.std(memory_deltas)),
            "cpu_percent_mean": float(np.mean(cpu_percents)),
            "cpu_percent_std": float(np.std(cpu_percents)),
        }

