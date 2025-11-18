# Configuration Guide

## Overview

Configuration is managed via Pydantic Settings in `src/config.py`. All settings can be overridden via environment variables.

## Configuration File

Location: `src/config.py`

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Prefect Configuration
    prefect_api_url: str = "http://localhost:4200/api"
    
    # PostgreSQL Configuration
    postgres_user: str = "prefect"
    postgres_password: str = "prefect"
    postgres_db: str = "prefect"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    
    # MinIO Configuration
    minio_root_user: str = "minioadmin"
    minio_root_password: str = "minioadmin"
    minio_endpoint: str = "localhost:9000"
    minio_bucket_name: str = "mlflow-artifacts"
    
    # MLflow Configuration
    mlflow_tracking_uri: str = "http://localhost:5000"
    mlflow_s3_endpoint_url: str = "http://localhost:9000"
    aws_access_key_id: str = "minioadmin"
    aws_secret_access_key: str = "minioadmin"
    
    # Experiment Configuration
    experiment_name: str = "dbscan-comparison"
```

## Environment Variables

All settings can be overridden via environment variables:

```bash
# Prefect
export PREFECT_API_URL=http://localhost:4200/api

# PostgreSQL
export POSTGRES_USER=prefect
export POSTGRES_PASSWORD=prefect
export POSTGRES_DB=prefect
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432

# MinIO
export MINIO_ROOT_USER=minioadmin
export MINIO_ROOT_PASSWORD=minioadmin
export MINIO_ENDPOINT=localhost:9000
export MINIO_BUCKET_NAME=mlflow-artifacts

# MLflow
export MLFLOW_TRACKING_URI=http://localhost:5000
export MLFLOW_S3_ENDPOINT_URL=http://localhost:9000
export AWS_ACCESS_KEY_ID=minioadmin
export AWS_SECRET_ACCESS_KEY=minioadmin

# Monitoring
export PUSHGATEWAY_URL=http://localhost:9091
export JAEGER_ENDPOINT=http://localhost:14268/api/traces
```

## .env File

Create a `.env` file in the project root:

```bash
# .env
PREFECT_API_URL=http://localhost:4200/api
POSTGRES_USER=prefect
POSTGRES_PASSWORD=prefect
MLFLOW_TRACKING_URI=http://localhost:5000
PUSHGATEWAY_URL=http://localhost:9091
```

The `.env` file is automatically loaded by Pydantic Settings.

## Docker Compose Configuration

Service configurations are in `docker-compose.yml`. Key settings:

### PostgreSQL
- User: `prefect`
- Password: `prefect`
- Database: `prefect` (Prefect), `mlflow` (MLflow)

### MinIO
- Access Key: `minioadmin`
- Secret Key: `minioadmin`
- Console: http://localhost:9001

### Prefect
- API URL: http://localhost:4200/api
- Database: PostgreSQL

### MLflow
- Tracking URI: http://localhost:5000
- Artifact Store: MinIO (s3://mlflow-artifacts/)

## Production Configuration

### Security
- Change all default passwords
- Use secrets management
- Enable TLS/SSL
- Restrict network access

### Performance
- Tune PostgreSQL settings
- Configure connection pooling
- Set appropriate resource limits
- Enable caching

### Monitoring
- Configure alert notifications
- Set up log aggregation
- Enable distributed tracing
- Configure metrics retention

## Configuration Validation

Settings are validated on startup:

```python
from src.config import settings

# Access settings
print(settings.prefect_api_url)
print(settings.postgres_url)  # Property
```

Invalid configurations will raise validation errors.

## Best Practices

1. **Use Environment Variables**: For sensitive data
2. **Version Control**: Don't commit `.env` files
3. **Documentation**: Document all configuration options
4. **Validation**: Validate configurations early
5. **Defaults**: Provide sensible defaults

