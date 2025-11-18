FROM ghcr.io/mlflow/mlflow:v2.8.1

# Install required dependencies
# - psycopg2-binary: PostgreSQL backend store support
# - boto3: S3/MinIO artifact storage support
RUN pip install --no-cache-dir \
    psycopg2-binary \
    boto3

