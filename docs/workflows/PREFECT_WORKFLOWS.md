# Prefect Workflows Guide

## Overview

This guide covers all Prefect workflows in the Taxi MLOps platform, including how to create, run, schedule, and monitor flows.

## Table of Contents

1. [Workflow Types](#workflow-types)
2. [Running Workflows](#running-workflows)
3. [Scheduling Workflows](#scheduling-workflows)
4. [Monitoring Workflows](#monitoring-workflows)
5. [Creating Custom Workflows](#creating-custom-workflows)
6. [Best Practices](#best-practices)

## Workflow Types

### 1. Experiment Pipeline

**Purpose**: Run a single DBSCAN experiment with tracking

**Flow**: `experiment_pipeline`

**Parameters**:
- `data_source`: MinIO object name or local file path
- `adapter_type`: `sklearn` or `sklearn_parallel`
- `eps`: DBSCAN eps parameter
- `min_samples`: DBSCAN min_samples parameter
- `coordinate_type`: `pickup`, `dropoff`, or `both`
- `use_location_ids`: Use location IDs if coordinates unavailable
- `max_samples`: Limit samples for testing
- `use_minio`: Load from MinIO (default: True)

**Usage**:
```python
from src.workflows.experiment_pipeline import experiment_pipeline

result = experiment_pipeline(
    data_source="yellow_tripdata_2025-09.parquet",
    adapter_type="sklearn",
    eps=0.5,
    min_samples=5,
    max_samples=1000
)
```

### 2. Evaluation Pipeline

**Purpose**: Run experiment with comprehensive evaluation metrics

**Flow**: `evaluation_pipeline`

**Additional Metrics**:
- Quality metrics (Silhouette, Davies-Bouldin, etc.)
- Performance metrics (runtime, memory, CPU)
- Overall score

**Usage**:
```python
from src.workflows.evaluation_flows import evaluation_pipeline

evaluation = evaluation_pipeline(
    data_source="yellow_tripdata_2025-09.parquet",
    adapter_type="sklearn",
    eps=0.5,
    min_samples=5
)
```

### 3. Parameter Sweep

**Purpose**: Test multiple parameter combinations

**Flow**: `parameter_sweep_flow`

**Parameters**:
- `eps_values`: List of eps values to test
- `min_samples_values`: List of min_samples values
- `metric`: Metric to optimize (default: `overall_score`)

**Usage**:
```python
from src.workflows.parameter_sweep import parameter_sweep_flow

results = parameter_sweep_flow(
    data_source="yellow_tripdata_2025-09.parquet",
    adapter_type="sklearn",
    eps_values=[0.3, 0.5, 0.7, 1.0],
    min_samples_values=[5, 10, 15]
)
```

### 4. Adapter Comparison

**Purpose**: Compare sequential vs parallel adapters

**Flow**: `compare_adapters_sweep_flow`

**Usage**:
```python
from src.workflows.parameter_sweep import compare_adapters_sweep_flow

comparison = compare_adapters_sweep_flow(
    data_source="yellow_tripdata_2025-09.parquet",
    eps_values=[0.3, 0.5, 0.7],
    min_samples_values=[5, 10]
)
```

### 5. Scheduled Workflows

**Daily Comparison**: `daily_adapter_comparison_flow`
- Runs daily at 2 AM UTC
- Compares both adapters with default parameters

**Weekly Parameter Sweep**: `weekly_parameter_sweep_flow`
- Runs weekly on Mondays at 3 AM UTC
- Comprehensive parameter exploration

**Result Aggregation**: `aggregate_results_flow`
- Aggregates results from recent experiments
- Performs statistical analysis

## Running Workflows

### Method 1: Direct Python Execution

```python
from src.workflows.experiment_pipeline import experiment_pipeline

if __name__ == "__main__":
    result = experiment_pipeline(
        data_source="yellow_tripdata_2025-09.parquet",
        adapter_type="sklearn",
        eps=0.5,
        min_samples=5
    )
    print(result)
```

### Method 2: Using Scripts

```bash
# Run single experiment
python scripts/run_experiment.py \
  --data-object yellow_tripdata_2025-09.parquet \
  --adapter-type sklearn \
  --eps 0.5 \
  --min-samples 5

# Compare adapters
python scripts/compare_adapters.py \
  --data-object yellow_tripdata_2025-09.parquet

# Parameter sweep
python scripts/run_parameter_sweep.py \
  --data-object yellow_tripdata_2025-09.parquet \
  --eps-values 0.3 0.5 0.7 1.0 \
  --min-samples-values 5 10 15
```

### Method 3: Prefect CLI

```bash
# Run flow directly
prefect deployment run experiment_pipeline/default

# List flows
prefect flow ls

# View flow runs
prefect flow-run ls
```

## Scheduling Workflows

### Using Prefect Deployments

1. **Create deployment**:
   ```python
   from prefect import serve
   from src.workflows.experiment_pipeline import experiment_pipeline

   if __name__ == "__main__":
       experiment_pipeline.serve(
           name="daily-experiments",
           cron="0 2 * * *",  # Daily at 2 AM
           parameters={
               "data_source": "yellow_tripdata_2025-09.parquet",
               "adapter_type": "sklearn"
           }
       )
   ```

2. **Deploy with CLI**:
   ```bash
   prefect deploy src/workflows/experiment_pipeline.py:experiment_pipeline \
     --name daily-experiments \
     --cron "0 2 * * *" \
     --pool default-agent-pool
   ```

### Using Prefect UI

1. Navigate to http://localhost:4200
2. Go to "Deployments"
3. Create new deployment
4. Configure schedule (cron or interval)
5. Set parameters
6. Assign to agent pool

## Monitoring Workflows

### Prefect UI

**Access**: http://localhost:4200

**Features**:
- View all flow runs
- See execution timeline
- Check task logs
- Monitor flow status
- View flow run history

### Grafana Dashboards

**Prefect Flow Monitoring Dashboard**:
- Flow runs over time
- Flow run duration
- Success rate
- Active flows

**Access**: http://localhost:3000 → Dashboards → Prefect Flow Monitoring

### Prometheus Metrics

**Key Metrics**:
- `prefect_flow_runs_total`: Total flow runs
- `prefect_flow_run_duration_seconds`: Flow duration
- `prefect_active_flows`: Currently running flows

**Query Examples**:
```promql
# Flow success rate
sum(rate(prefect_flow_runs_total{status="success"}[5m])) / 
sum(rate(prefect_flow_runs_total[5m])) * 100

# Average flow duration
rate(prefect_flow_run_duration_seconds_sum[5m]) / 
rate(prefect_flow_run_duration_seconds_count[5m])
```

## Creating Custom Workflows

### Basic Flow Template

```python
from prefect import flow, task
from typing import Any

@task
def my_task(input_data: str) -> str:
    """Task that does something"""
    return f"Processed: {input_data}"

@flow(name="my_custom_flow", log_prints=True)
def my_custom_flow(data_source: str) -> dict[str, Any]:
    """Custom flow"""
    result = my_task(data_source)
    return {"result": result}

if __name__ == "__main__":
    result = my_custom_flow("test_data")
    print(result)
```

### Advanced Flow with Error Handling

```python
from prefect import flow, task
from prefect.tasks import task_inputs
import time

@task(retries=3, retry_delay_seconds=5)
def risky_task(data: str) -> str:
    """Task with retry logic"""
    # Your implementation
    return data

@flow(name="robust_flow")
def robust_flow(data_source: str) -> dict:
    """Flow with error handling"""
    try:
        result = risky_task(data_source)
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "failure", "error": str(e)}
```

### Flow with Parallel Execution

```python
from prefect import flow, task
from prefect.tasks import task_inputs
import asyncio

@task
async def async_task(item: str) -> str:
    """Async task"""
    await asyncio.sleep(1)
    return f"Processed {item}"

@flow
async def parallel_flow(items: list[str]) -> list[str]:
    """Flow with parallel tasks"""
    tasks = [async_task(item) for item in items]
    return await asyncio.gather(*tasks)
```

## Best Practices

### 1. Task Design
- Keep tasks focused and single-purpose
- Use appropriate retry strategies
- Handle errors gracefully
- Log important information

### 2. Flow Design
- Use descriptive flow names
- Document parameters clearly
- Return structured results
- Enable logging (`log_prints=True`)

### 3. Resource Management
- Use appropriate task runners
- Configure resource limits
- Clean up temporary resources
- Monitor resource usage

### 4. Error Handling
- Use retries for transient failures
- Implement fallback strategies
- Log errors with context
- Notify on critical failures

### 5. Testing
- Test flows locally first
- Use small datasets for testing
- Verify error handling
- Test edge cases

### 6. Monitoring
- Add custom metrics
- Use appropriate log levels
- Track execution time
- Monitor resource usage

## Troubleshooting

### Flow Not Appearing in UI
- Check Prefect server is running
- Verify flow is registered
- Check agent is connected
- Review flow logs

### Flow Execution Fails
- Check task logs for errors
- Verify dependencies are installed
- Confirm data sources are accessible
- Review error messages

### Slow Execution
- Check resource constraints
- Review task dependencies
- Consider parallelization
- Monitor system resources

### Metrics Not Appearing
- Verify `PUSHGATEWAY_URL` is set
- Check Pushgateway is running
- Confirm Prometheus is scraping
- Review metrics collection code

## Examples

See `scripts/` directory for complete examples:
- `run_experiment.py`: Single experiment
- `compare_adapters.py`: Adapter comparison
- `run_parameter_sweep.py`: Parameter sweep
- `quick_start_prefect.py`: Quick start example

## Additional Resources

- [Prefect Documentation](https://docs.prefect.io/)
- [Prefect Best Practices](https://docs.prefect.io/latest/guides/)
- [Prefect API Reference](https://docs.prefect.io/latest/api-ref/)

