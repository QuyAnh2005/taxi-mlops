# MinIO Usage Guide

## Overview

The Taxi MLOps project uses MinIO for object storage. Data files are stored in MinIO and loaded by workflows, enabling centralized data management and scalability.

## Buckets

The project uses two MinIO buckets:

1. **`mlflow-artifacts`**: Stores MLflow experiment artifacts (models, plots, metadata)
2. **`taxi-data`**: Stores taxi trip data files (parquet files)

## Setup

### 1. Create Buckets

```bash
# Create MLflow artifacts bucket
python scripts/setup_minio_bucket.py

# Create data bucket
python scripts/setup_data_bucket.py
```

### 2. Upload Data

```bash
# Upload a single file
python scripts/upload_to_minio.py data/yellow_tripdata_2025-09.parquet \
  --object-name yellow_tripdata_2025-09.parquet \
  --bucket-name taxi-data

# Upload with custom object name
python scripts/upload_to_minio.py data/file.parquet \
  --object-name taxi-data/2025/yellow_tripdata_2025-09.parquet \
  --bucket-name taxi-data

# Upload all parquet files in a directory
python scripts/upload_to_minio.py data/ \
  --recursive \
  --prefix taxi-data/ \
  --bucket-name taxi-data
```

## Using Data in Workflows

### Default Behavior

By default, all workflows load data from MinIO:

```bash
# Uses MinIO by default
python scripts/run_experiment.py --data-object yellow_tripdata_2025-09.parquet
```

### Explicit MinIO Usage

```bash
# Specify MinIO object name
python scripts/run_experiment.py \
  --data-object yellow_tripdata_2025-09.parquet \
  --adapter-type sklearn
```

### Local File Fallback

To use local files instead:

```bash
# Use local file
python scripts/run_experiment.py \
  --data-source data/yellow_tripdata_2025-09.parquet \
  --no-minio
```

## Data Loading Logic

The `DataLoader.load_data()` method:

1. **First tries MinIO** (default bucket: `taxi-data`)
2. **Falls back to local file** if MinIO fails or object not found
3. **Raises error** if neither source has the data

## MinIO Console

Access MinIO Console at http://localhost:9001

- **Username**: `minioadmin`
- **Password**: `minioadmin`

You can:
- Browse buckets and objects
- Upload/download files via UI
- View object metadata
- Manage bucket policies

## Scripts

### `upload_to_minio.py`

Upload files to MinIO:

```bash
python scripts/upload_to_minio.py <source> [options]

Options:
  --object-name NAME    Object name in MinIO
  --bucket-name NAME    Bucket name (default: from config)
  --recursive           Upload directory recursively
  --prefix PREFIX       Prefix for object names
```

### `setup_data_bucket.py`

Create the data bucket:

```bash
python scripts/setup_data_bucket.py
```

## Best Practices

1. **Organize data by date/version**:
   ```
   taxi-data/
   ├── 2025/
   │   ├── yellow_tripdata_2025-09.parquet
   │   └── yellow_tripdata_2025-10.parquet
   └── 2024/
       └── yellow_tripdata_2024-12.parquet
   ```

2. **Use descriptive object names**: Include date, type, and version

3. **Version control**: Keep multiple versions of datasets

4. **Clean up old data**: Periodically remove outdated files

## Troubleshooting

### Data Not Found

If you get "Data source not found":

1. **Check if file is uploaded**:
   ```bash
   # List objects in bucket
   python -c "from src.storage import MinIOClient; client = MinIOClient(bucket_name='taxi-data'); print(client.list_objects())"
   ```

2. **Verify object name**: Use exact object name as stored in MinIO

3. **Check bucket name**: Default is `taxi-data`

### Connection Issues

If MinIO connection fails:

1. **Check MinIO is running**:
   ```bash
   docker-compose ps minio
   ```

2. **Verify endpoint**: Default is `localhost:9000`

3. **Check credentials**: Default is `minioadmin/minioadmin`

## Integration with Workflows

All Prefect workflows support MinIO:

- `experiment_pipeline`: Loads data from MinIO
- `evaluation_pipeline`: Loads data from MinIO
- `parameter_sweep_flow`: Loads data from MinIO
- `scheduled_workflows`: Loads data from MinIO

Set `use_minio=True` (default) to use MinIO, or `use_minio=False` for local files.

