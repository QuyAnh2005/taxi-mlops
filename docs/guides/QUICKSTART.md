# Quick Start Guide

## 1. Start Services

```bash
# Start all Docker services
docker-compose up -d

# Wait ~30 seconds for services to initialize
sleep 30

# Verify setup
python scripts/verify_setup.py
```

## 2. Install Dependencies

```bash
# Using uv (recommended)
uv pip install -r requirements.txt

# Or using pip
pip install -r requirements.txt
```

## 3. Set Up Services

```bash
# Set up MinIO buckets (for MLflow artifacts and data)
python scripts/setup_minio_bucket.py
python scripts/setup_data_bucket.py

# Upload your data to MinIO
python scripts/upload_to_minio.py data/yellow_tripdata_2025-09.parquet \
  --object-name yellow_tripdata_2025-09.parquet \
  --bucket-name taxi-data

# Configure Prefect client
python scripts/setup_prefect.py
# Or manually:
# prefect config set PREFECT_API_URL=http://localhost:4200/api
```

## 4. Run Your First Experiment

### Sequential DBSCAN (from MinIO)
```bash
python scripts/run_experiment.py \
  --data-object yellow_tripdata_2025-09.parquet \
  --adapter-type sklearn \
  --eps 0.5 \
  --min-samples 5
```

### Parallel DBSCAN (from MinIO)
```bash
python scripts/run_experiment.py \
  --data-object yellow_tripdata_2025-09.parquet \
  --adapter-type sklearn_parallel \
  --eps 0.5 \
  --min-samples 5 \
  --n-jobs -1
```

### Compare Both (from MinIO)
```bash
python scripts/compare_adapters.py \
  --data-object yellow_tripdata_2025-09.parquet \
  --eps 0.5 \
  --min-samples 5
```

**Note**: All workflows now load data from MinIO by default. To use local files, add `--no-minio` and specify `--data-source` with a file path.

## 5. View Results

- **Prefect UI**: http://localhost:4200
  - Navigate to "Flow Runs" to see executions
  - See [QUICKSTART_PREFECT.md](QUICKSTART_PREFECT.md) for details
- **MLflow UI**: http://localhost:5000
  - View experiment tracking and metrics
- **MinIO Console**: http://localhost:9001
  - Username: `minioadmin`
  - Password: `minioadmin`

## 6. Advanced Usage

### Parameter Sweep

```bash
python scripts/run_parameter_sweep.py \
  --file-path data/yellow_tripdata_2025-09.parquet \
  --adapter-type sklearn \
  --eps-values 0.3 0.5 0.7 1.0 \
  --min-samples-values 5 10 15
```

### Aggregate Results

```bash
python scripts/run_aggregate_results.py --days 7
```

## Troubleshooting

If services fail to start:
```bash
# Check logs
docker-compose logs

# Restart services
docker-compose restart

# Clean restart
docker-compose down
docker-compose up -d
```

