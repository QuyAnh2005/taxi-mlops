# MLflow Integration Guide

## Overview

MLflow is used for experiment tracking, logging parameters, metrics, and artifacts from DBSCAN experiments.

## Access

**MLflow UI**: http://localhost:5000

## Features

- **Experiment Tracking**: Log all experiment runs
- **Parameter Logging**: Track hyperparameters (eps, min_samples, etc.)
- **Metrics Logging**: Quality and performance metrics
- **Artifact Storage**: Save models, plots, and metadata
- **Run Comparison**: Compare multiple runs side-by-side

## Automatic Logging

All workflows automatically log to MLflow:

### Experiment Pipeline
- Parameters: eps, min_samples, adapter_type, etc.
- Metrics: n_clusters, noise_ratio, elapsed_time
- Artifacts: Metadata JSON

### Evaluation Pipeline
- Parameters: All experiment parameters
- Quality Metrics: Silhouette, Davies-Bouldin, Calinski-Harabasz
- Performance Metrics: Runtime, memory, CPU
- Overall Score: Weighted combination

## Manual Logging

### Log Custom Metrics

```python
import mlflow
from src.config import settings

mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
mlflow.set_experiment("my-experiment")

with mlflow.start_run():
    mlflow.log_param("eps", 0.5)
    mlflow.log_metric("custom_metric", 0.95)
    mlflow.log_dict({"key": "value"}, "metadata.json")
```

### Log Artifacts

```python
with mlflow.start_run():
    # Log file
    mlflow.log_artifact("path/to/file.txt")
    
    # Log directory
    mlflow.log_artifacts("path/to/directory")
    
    # Log model (if applicable)
    mlflow.sklearn.log_model(model, "model")
```

## Viewing Results

### MLflow UI

1. **Open MLflow**: http://localhost:5000
2. **Select Experiment**: Click on experiment name
3. **View Runs**: See all runs with metrics
4. **Compare Runs**: Select multiple runs to compare

### Querying via API

```python
import mlflow
from mlflow.tracking import MlflowClient

client = MlflowClient()
runs = client.search_runs(
    experiment_ids=["1"],
    filter_string="metrics.overall_score > 0.5"
)

for run in runs:
    print(f"Run {run.info.run_id}: {run.data.metrics}")
```

## Experiment Organization

### Default Experiment
- **Name**: `dbscan-comparison`
- **Location**: Auto-created on first run

### Creating Custom Experiments

```python
import mlflow

mlflow.create_experiment(
    name="my-custom-experiment",
    tags={"team": "mlops", "project": "taxi"}
)
```

## Metrics Available

### Quality Metrics
- `silhouette_score`: Cluster separation (-1 to 1)
- `davies_bouldin_score`: Cluster compactness (lower is better)
- `calinski_harabasz_score`: Variance ratio (higher is better)
- `n_clusters`: Number of clusters found
- `noise_ratio`: Proportion of noise points

### Performance Metrics
- `runtime_seconds`: Execution time
- `memory_delta_mb`: Memory usage change
- `cpu_percent`: CPU utilization

### Overall Score
- `overall_score`: Weighted combination (0-1, higher is better)

## Parameters Tracked

- `eps`: DBSCAN eps parameter
- `min_samples`: DBSCAN min_samples parameter
- `adapter_type`: sklearn or sklearn_parallel
- `metric`: Distance metric (euclidean)
- `algorithm`: Clustering algorithm
- `data_source`: Dataset used

## Artifacts

### Metadata JSON
Contains:
- Experiment ID
- Adapter metadata
- Execution details
- System information

### Accessing Artifacts

```python
from mlflow.tracking import MlflowClient

client = MlflowClient()
run = client.get_run(run_id)
artifacts = client.list_artifacts(run_id)
```

## Best Practices

1. **Consistent Naming**: Use descriptive experiment names
2. **Tag Runs**: Add tags for organization
3. **Log Everything**: Parameters, metrics, and artifacts
4. **Compare Regularly**: Use comparison features
5. **Clean Up**: Archive old experiments

## Integration with MinIO

MLflow artifacts are stored in MinIO:
- **Bucket**: `mlflow-artifacts`
- **Endpoint**: http://localhost:9000
- **Credentials**: minioadmin/minioadmin

Artifacts are automatically uploaded to MinIO when logging.

## Troubleshooting

### MLflow Not Starting
- Check PostgreSQL is running
- Verify database exists
- Check connection string
- Review logs: `docker-compose logs mlflow`

### Artifacts Not Uploading
- Verify MinIO is running
- Check AWS credentials
- Verify bucket exists
- Check network connectivity

### Metrics Not Appearing
- Verify logging code executed
- Check experiment name matches
- Review run logs
- Verify MLflow connection

## API Reference

See [MLflow Documentation](https://mlflow.org/docs/latest/index.html) for complete API reference.

