# Evaluation Module

This module provides comprehensive evaluation capabilities for DBSCAN experiments, including performance metrics, quality metrics, and statistical analysis.

## Overview

The evaluation module is part of the Taxi MLOps project and provides:
- **Performance Metrics**: Runtime, memory, CPU usage, scalability analysis
- **Quality Metrics**: Clustering quality scores (silhouette, Davies-Bouldin, etc.)
- **Statistical Analysis**: Hypothesis testing, effect sizes, parameter sweep analysis
- **Experiment Evaluator**: Combined evaluation with overall scoring

## Components

### Performance Metrics (`performance_metrics.py`)

Measures runtime, memory usage, CPU usage, and scalability:

- `measure_runtime()`: Measure execution time
- `get_memory_usage()`: Get memory statistics
- `get_cpu_usage()`: Get CPU statistics
- `measure_with_resources()`: Measure function with full resource tracking
- `compute_scalability_metrics()`: Analyze scalability from multiple runs
- `aggregate_performance_metrics()`: Aggregate metrics from multiple experiments

### Quality Metrics (`quality_metrics.py`)

Evaluates clustering quality:

- `compute_silhouette_score()`: Silhouette coefficient (-1 to 1, higher is better)
- `compute_davies_bouldin_score()`: Davies-Bouldin index (lower is better)
- `compute_calinski_harabasz_score()`: Calinski-Harabasz index (higher is better)
- `compute_adjusted_rand_score()`: Adjusted Rand Index for comparing clusterings
- `compute_cluster_statistics()`: Basic cluster statistics
- `compute_all_quality_metrics()`: Compute all quality metrics at once
- `compare_clusterings()`: Compare two clusterings

### Statistical Analysis (`statistical_analysis.py`)

Provides statistical analysis utilities:

- `compute_summary_statistics()`: Mean, median, std, quartiles, etc.
- `t_test()`: Independent samples t-test
- `mann_whitney_u_test()`: Non-parametric Mann-Whitney U test
- `compare_groups()`: Comprehensive comparison of two groups
- `analyze_parameter_sweep()`: Analyze parameter sweep results

### Experiment Evaluator (`evaluator.py`)

Main evaluator that combines all metrics:

- `evaluate_experiment()`: Comprehensive evaluation of a single experiment
- `compare_experiments()`: Compare two experiments
- `aggregate_evaluations()`: Aggregate multiple evaluations

## Usage Example

```python
from src.evaluation import ExperimentEvaluator, PerformanceMetrics, QualityMetrics
import numpy as np

# Run experiment and collect metrics
X = np.array([[1, 2], [2, 3], [3, 4], ...])
labels = np.array([0, 0, 1, 1, -1, ...])

# Compute quality metrics
quality = QualityMetrics.compute_all_quality_metrics(X, labels)

# Measure performance
def run_clustering():
    return labels  # Your clustering function

result, perf_metrics = PerformanceMetrics.measure_with_resources(run_clustering)

# Comprehensive evaluation
evaluator = ExperimentEvaluator()
evaluation = evaluator.evaluate_experiment(X, labels, perf_metrics)
```

