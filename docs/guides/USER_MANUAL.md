# User Manual

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Running Experiments](#running-experiments)
4. [Viewing Results](#viewing-results)
5. [Monitoring](#monitoring)
6. [Advanced Usage](#advanced-usage)
7. [Troubleshooting](#troubleshooting)

## Introduction

The Taxi MLOps platform enables you to:

- Compare sequential and parallel DBSCAN implementations
- Track experiments automatically
- Monitor system performance
- Analyze results comprehensively

## Getting Started

### Initial Setup

1. **Start Services**:
   ```bash
   docker-compose up -d
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Services**:
   ```bash
   python scripts/setup_minio_bucket.py
   python scripts/setup_data_bucket.py
   python scripts/setup_prefect.py
   ```

4. **Upload Data**:
   ```bash
   python scripts/upload_to_minio.py data/yellow_tripdata_2025-09.parquet \
     --object-name yellow_tripdata_2025-09.parquet \
     --bucket-name taxi-data
   ```

### Verify Setup

```bash
python scripts/verify_setup.py
```

## Running Experiments

### Basic Experiment

```bash
export PUSHGATEWAY_URL=http://localhost:9091
python scripts/run_experiment.py \
  --data-object yellow_tripdata_2025-09.parquet \
  --adapter-type sklearn \
  --eps 0.5 \
  --min-samples 5
```

### Compare Adapters

```bash
python scripts/compare_adapters.py \
  --data-object yellow_tripdata_2025-09.parquet \
  --eps 0.5 \
  --min-samples 5
```

### Parameter Sweep

```bash
python scripts/run_parameter_sweep.py \
  --data-object yellow_tripdata_2025-09.parquet \
  --adapter-type sklearn \
  --eps-values 0.3 0.5 0.7 1.0 \
  --min-samples-values 5 10 15
```

## Viewing Results

### MLflow UI

1. Open http://localhost:5000
2. Select experiment: "dbscan-comparison"
3. View runs and metrics
4. Compare runs side-by-side

### Prefect UI

1. Open http://localhost:4200
2. Navigate to "Flow Runs"
3. Click on a flow run
4. View execution timeline and logs

### Grafana Dashboards

1. Open http://localhost:3000
2. Login: admin/admin
3. Go to Dashboards → Browse
4. Select "Experiment Monitoring" or "Prefect Flow Monitoring"

### Prometheus

1. Open http://localhost:9090
2. Enter query: `experiments_total`
3. Click "Execute"
4. View results in Table or Graph tab

## Monitoring

### Key Metrics

- **Experiments**: `experiments_total`
- **Flow Runs**: `prefect_flow_runs_total`
- **Duration**: `experiment_duration_seconds`
- **Success Rate**: Calculate from metrics

### Dashboards

- **Experiment Monitoring**: Experiment metrics and trends
- **Prefect Flow Monitoring**: Workflow execution metrics

### Alerts

Configured alerts notify you of:
- High failure rates
- Slow executions
- Service downtime
- Resource issues

## Advanced Usage

### Custom Workflows

See [Prefect Workflows Guide](workflows/PREFECT_WORKFLOWS.md) for creating custom workflows.

### Custom Metrics

See [Monitoring Guide](services/MONITORING.md) for adding custom metrics.

### Data Management

See [MinIO Usage Guide](services/MINIO_USAGE.md) for data management.

## Troubleshooting

See [Troubleshooting Guide](TROUBLESHOOTING.md) for common issues and solutions.

## Additional Resources

- [Quick Start Guide](QUICKSTART.md)
- [Architecture Documentation](../architecture/ARCHITECTURE.md)
- [Service Documentation](../services/)
- [Workflow Documentation](../workflows/)

