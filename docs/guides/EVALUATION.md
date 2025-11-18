# Evaluation Framework Documentation

## Overview

The evaluation framework provides comprehensive metrics and analysis tools for DBSCAN experiments, including both performance and quality metrics, statistical analysis, and automated workflows.

## Architecture

### Evaluation Module

Located in `src/evaluation/`, the module consists of:

1. **Performance Metrics** (`performance_metrics.py`)
   - Runtime measurement
   - Memory usage tracking
   - CPU utilization
   - Scalability analysis

2. **Quality Metrics** (`quality_metrics.py`)
   - Silhouette Score
   - Davies-Bouldin Index
   - Calinski-Harabasz Index
   - Adjusted Rand Index
   - Cluster statistics

3. **Statistical Analysis** (`statistical_analysis.py`)
   - Summary statistics
   - Hypothesis testing (t-test, Mann-Whitney U)
   - Effect size (Cohen's d)
   - Parameter sweep analysis

4. **Experiment Evaluator** (`evaluator.py`)
   - Combines all metrics
   - Experiment comparison
   - Result aggregation

## Prefect Workflows

### Evaluation Pipeline

`evaluation_pipeline`: Complete evaluation workflow that:
- Loads and prepares data
- Runs experiment with performance tracking
- Computes quality metrics
- Logs to MLflow
- Returns comprehensive evaluation

### Parameter Sweep

`parameter_sweep_flow`: Systematic parameter exploration:
- Tests multiple eps and min_samples values
- Tracks metrics for each combination
- Identifies best parameters
- Performs statistical analysis

`compare_adapters_sweep_flow`: Compare both adapters with parameter sweep

### Scheduled Workflows

1. **Daily Comparison** (`daily_adapter_comparison_flow`)
   - Runs daily at 2 AM UTC
   - Compares sequential vs parallel adapters
   - Uses default parameter ranges

2. **Weekly Parameter Sweep** (`weekly_parameter_sweep_flow`)
   - Runs weekly on Mondays at 3 AM UTC
   - Comprehensive parameter exploration
   - Larger sample sizes

3. **Result Aggregation** (`aggregate_results_flow`)
   - Aggregates results from database
   - Statistical analysis
   - Can be run on-demand or scheduled

## Metrics Explained

### Performance Metrics

- **Runtime**: Execution time in seconds
- **Memory Usage**: RSS (Resident Set Size) in MB
- **CPU Usage**: CPU percentage utilization
- **Scalability**: Time complexity estimation (O(n^p))

### Quality Metrics

- **Silhouette Score**: Measures how similar objects are to their own cluster vs other clusters (-1 to 1, higher is better)
- **Davies-Bouldin Index**: Average similarity ratio of clusters (lower is better)
- **Calinski-Harabasz Index**: Ratio of between-cluster to within-cluster variance (higher is better)
- **Adjusted Rand Index**: Measures similarity between two clusterings (-1 to 1, higher is better)

### Overall Score

Weighted combination of quality (70%) and performance (30%):
- Quality: Average of normalized silhouette and Davies-Bouldin scores
- Performance: Inverse of normalized runtime
- Range: 0-1 (higher is better)

## Usage Examples

### Basic Evaluation

```python
from src.workflows.evaluation_flows import evaluation_pipeline

result = evaluation_pipeline(
    file_path="data/yellow_tripdata_2025-09.parquet",
    adapter_type="sklearn",
    eps=0.5,
    min_samples=5,
    max_samples=5000,
)

print(f"Overall Score: {result['overall_score']}")
print(f"Silhouette: {result['quality']['silhouette_score']}")
print(f"Runtime: {result['performance']['elapsed_time_seconds']}s")
```

### Parameter Sweep

```python
from src.workflows.parameter_sweep import parameter_sweep_flow

sweep_result = parameter_sweep_flow(
    file_path="data/yellow_tripdata_2025-09.parquet",
    adapter_type="sklearn",
    eps_values=[0.3, 0.5, 0.7, 1.0],
    min_samples_values=[5, 10, 15],
    max_samples=5000,
)

print(f"Best eps: {sweep_result['best_parameters']['eps']}")
print(f"Best min_samples: {sweep_result['best_parameters']['min_samples']}")
```

### Scheduled Workflows

To enable scheduled workflows, deploy them to Prefect with cron schedules:

```bash
# Create work pool first (if needed)
prefect work-pool create default-agent-pool --type process

# Deploy daily comparison with schedule
prefect deploy src/workflows/scheduled_workflows.py:daily_adapter_comparison_flow \
  --name daily-comparison \
  --pool default-agent-pool \
  --cron "0 2 * * *"

# Deploy weekly sweep with schedule
prefect deploy src/workflows/scheduled_workflows.py:weekly_parameter_sweep_flow \
  --name weekly-sweep \
  --pool default-agent-pool \
  --cron "0 3 * * 1"
```

**Note**: In Prefect 3.x, schedules are configured during deployment, not in the flow decorator.

## Integration with MLflow

All evaluation results are automatically logged to MLflow with:
- Parameters (eps, min_samples, adapter_type)
- Quality metrics (silhouette, Davies-Bouldin, etc.)
- Performance metrics (runtime, memory, CPU)
- Overall score

View results in MLflow UI at http://localhost:5000

## Database Storage

Experiment metadata is stored in PostgreSQL:
- Experiment ID
- Adapter type
- Parameters (JSONB)
- Metrics (JSONB)
- Timestamps

Query results using `aggregate_results_flow` or directly via PostgreSQL client.

