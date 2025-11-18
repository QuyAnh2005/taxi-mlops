# Deployment Guide

This guide explains how to deploy and run the Taxi MLOps project.

## Prerequisites

- Docker and Docker Compose installed
- Python 3.11+ installed
- `uv` package manager installed (or use pip)

## Quick Start

1. **Clone and navigate to the project:**
   ```bash
   cd /home/quyanh/Projects/taxi-mlops
   ```

2. **Set up environment variables (optional):**
   ```bash
   cp .env.example .env
   # Edit .env if needed
   ```

3. **Start all services:**
   ```bash
   docker-compose up -d
   ```
   Or use the Makefile:
   ```bash
   make up
   ```

4. **Wait for services to be ready (about 30 seconds), then verify:**
   ```bash
   make verify
   ```

5. **Set up MinIO bucket:**
   ```bash
   python scripts/setup_minio_bucket.py
   ```

6. **Install Python dependencies:**
   ```bash
   uv pip install -r requirements.txt
   ```
   Or with pip:
   ```bash
   pip install -r requirements.txt
   ```

## Running Experiments

### Single Experiment

Run a single experiment with the sequential adapter:
```bash
python scripts/run_experiment.py \
  --file-path data/yellow_tripdata_2025-09.parquet \
  --adapter-type sklearn \
  --eps 0.5 \
  --min-samples 5
```

Run with the parallel adapter:
```bash
python scripts/run_experiment.py \
  --file-path data/yellow_tripdata_2025-09.parquet \
  --adapter-type sklearn_parallel \
  --eps 0.5 \
  --min-samples 5 \
  --n-jobs -1
```

### Compare Adapters

Compare both adapters side-by-side:
```bash
python scripts/compare_adapters.py \
  --file-path data/yellow_tripdata_2025-09.parquet \
  --eps 0.5 \
  --min-samples 5
```

## Accessing Services

- **Prefect UI**: http://localhost:4200
- **MLflow UI**: http://localhost:5000
- **MinIO Console**: http://localhost:9001
  - Username: `minioadmin`
  - Password: `minioadmin`

## Using Prefect Workflows

### Prefect Setup

1. **Configure Prefect client:**
   ```bash
   prefect config set PREFECT_API_URL=http://localhost:4200/api
   ```
   Or use: `python scripts/setup_prefect.py`

2. **Verify connection:**
   ```bash
   prefect config view
   curl http://localhost:4200/api/health
   ```

### Running Flows

**Option 1: Run directly (appears in UI)**
```bash
python scripts/run_experiment.py \
  --file-path data/yellow_tripdata_2025-09.parquet \
  --adapter-type sklearn
```

**Option 2: Deploy and run**
```bash
# Create work pool (if needed)
prefect work-pool create default-agent-pool --type process

# Deploy flow
prefect deploy src/workflows/experiment_pipeline.py:experiment_pipeline \
  --name experiment-pipeline \
  --pool default-agent-pool

# Run deployed flow
prefect deployment run experiment_pipeline/experiment-pipeline \
  --param file_path="data/yellow_tripdata_2025-09.parquet"
```

### Available Workflows

- `experiment_pipeline`: Basic experiment execution
- `evaluation_pipeline`: Comprehensive evaluation with metrics
- `parameter_sweep_flow`: Parameter exploration
- `compare_adapters_sweep_flow`: Compare both adapters with sweep
- `daily_adapter_comparison_flow`: Scheduled daily comparison
- `weekly_parameter_sweep_flow`: Scheduled weekly sweep
- `aggregate_results_flow`: Result aggregation and analysis

See [docs/PREFECT_USAGE.md](docs/PREFECT_USAGE.md) for detailed usage.

## Monitoring

### View Logs

```bash
docker-compose logs -f [service-name]
```

Or use the Makefile:
```bash
make logs
```

### Check Service Status

```bash
docker-compose ps
```

## Troubleshooting

### Services not starting

1. Check if ports are already in use:
   ```bash
   netstat -tulpn | grep -E '4200|5000|5432|6379|9000|9001'
   ```

2. Check Docker logs:
   ```bash
   docker-compose logs [service-name]
   ```

### Prefect connection issues

1. **Version mismatch**: Ensure Prefect client and server versions match
   - Server: Prefect 3.x (in Docker)
   - Client: Should be Prefect 3.x
   - Check: `prefect version` and `docker-compose logs prefect-server`

2. **Configure API URL:**
   ```bash
   prefect config set PREFECT_API_URL=http://localhost:4200/api
   prefect config view
   ```

3. **Check if Prefect server is running:**
   ```bash
   docker-compose ps prefect-server
   curl http://localhost:4200/api/health
   ```

4. **Empty UI**: Run a flow first to populate the UI:
   ```bash
   python scripts/quick_start_prefect.py
   ```

### MLflow connection issues

1. Ensure MinIO bucket exists:
   ```bash
   python scripts/setup_minio_bucket.py
   ```

2. Check MLflow tracking URI:
   ```bash
   export MLFLOW_TRACKING_URI=http://localhost:5000
   ```

## Cleanup

To stop all services:
```bash
make down
```

To stop and remove volumes (clean slate):
```bash
make clean
```

