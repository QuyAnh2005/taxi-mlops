# Reproducibility Package

## Overview

This document ensures the Taxi MLOps platform can be fully reproduced by others.

## Requirements

### System Requirements
- **OS**: Linux (tested on Ubuntu 22.04+)
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Python**: 3.11+
- **Memory**: 8GB+ RAM recommended
- **Disk**: 10GB+ free space

### Software Dependencies
- Docker & Docker Compose
- Python 3.11+
- `uv` package manager (or `pip`)

## Step-by-Step Reproduction

### 1. Clone Repository
```bash
git clone <repository-url>
cd taxi-mlops
```

### 2. Start Infrastructure
```bash
docker-compose up -d
```

Wait for all services to be healthy:
```bash
docker-compose ps
```

### 3. Install Python Dependencies
```bash
# Using uv
uv pip install -r requirements.txt

# Or using pip
pip install -r requirements.txt
```

### 4. Set Up Services
```bash
# Create MinIO buckets
python scripts/setup_minio_bucket.py
python scripts/setup_data_bucket.py

# Configure Prefect
python scripts/setup_prefect.py
```

### 5. Upload Sample Data
```bash
# Upload data to MinIO
python scripts/upload_to_minio.py data/yellow_tripdata_2025-09.parquet \
  --object-name yellow_tripdata_2025-09.parquet \
  --bucket-name taxi-data
```

### 6. Verify Setup
```bash
python scripts/verify_setup.py
```

### 7. Run Test Experiment
```bash
export PUSHGATEWAY_URL=http://localhost:9091
python scripts/run_experiment.py \
  --data-object yellow_tripdata_2025-09.parquet \
  --adapter-type sklearn \
  --eps 0.5 \
  --min-samples 5 \
  --max-samples 1000
```

### 8. Verify Results
- **Prefect UI**: http://localhost:4200 - Should show flow run
- **MLflow UI**: http://localhost:5000 - Should show experiment
- **Grafana**: http://localhost:3000 - Should show metrics (after 30s)

## Configuration Files

All configuration is in:
- `docker-compose.yml` - Service definitions
- `src/config.py` - Application configuration
- `docker/prometheus/prometheus.yml` - Prometheus config
- `docker/grafana/provisioning/` - Grafana provisioning

## Data Requirements

### Sample Data
- Location: `data/yellow_tripdata_2025-09.parquet`
- Format: Parquet
- Required columns: `PULocationID`, `DOLocationID` (or coordinate columns)

### Data Format
The system expects NYC taxi trip data with:
- Location IDs: `PULocationID`, `DOLocationID`
- Or coordinates: `pickup_longitude`, `pickup_latitude`, etc.

## Environment Variables

Key environment variables (with defaults):

```bash
# Prefect
PREFECT_API_URL=http://localhost:4200/api

# Monitoring
PUSHGATEWAY_URL=http://localhost:9091

# MLflow
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_S3_ENDPOINT_URL=http://localhost:9000

# MinIO
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin
```

## Verification Checklist

- [ ] All Docker services running
- [ ] Prefect UI accessible
- [ ] MLflow UI accessible
- [ ] Grafana accessible
- [ ] Prometheus scraping targets
- [ ] MinIO buckets created
- [ ] Data uploaded to MinIO
- [ ] Test experiment runs successfully
- [ ] Metrics appear in Grafana
- [ ] Results visible in MLflow

## Known Issues & Workarounds

### Issue: Port Conflicts
**Workaround**: Change ports in `docker-compose.yml`

### Issue: Services Not Starting
**Workaround**: Check logs: `docker-compose logs <service>`

### Issue: Metrics Not Appearing
**Workaround**: Set `PUSHGATEWAY_URL` and wait 30 seconds

## Test Data

If sample data is not available, you can:

1. **Download NYC taxi data**:
   - Visit NYC TLC website
   - Download parquet files
   - Place in `data/` directory

2. **Use synthetic data**:
   - Generate test data with script
   - Use smaller sample sizes for testing

## Performance Expectations

### Small Dataset (1K samples)
- Experiment time: < 1 second
- Memory usage: < 100MB
- CPU usage: Low

### Medium Dataset (10K samples)
- Experiment time: 1-5 seconds
- Memory usage: 200-500MB
- CPU usage: Moderate

### Large Dataset (100K+ samples)
- Experiment time: 10-60 seconds
- Memory usage: 1-2GB
- CPU usage: High

## Troubleshooting

See [Troubleshooting Guide](guides/TROUBLESHOOTING.md) for detailed solutions.

## Support

For issues:
1. Check documentation
2. Review logs
3. Check GitHub issues
4. Contact maintainers

## Citation

If using this platform in research, please cite:

```
Taxi MLOps: DBSCAN Clustering Comparison Platform
[Your Name/Organization]
[Year]
```

## License

[Add license information]

