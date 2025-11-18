"""Configuration management using Pydantic Settings"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    # Prefect Configuration
    prefect_api_url: str = "http://localhost:4200/api"

    # PostgreSQL Configuration
    postgres_user: str = "prefect"
    postgres_password: str = "prefect"
    postgres_db: str = "prefect"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    @property
    def postgres_url(self) -> str:
        """Get PostgreSQL connection URL"""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # Redis Configuration
    redis_host: str = "localhost"
    redis_port: int = 6379

    # MinIO Configuration
    minio_root_user: str = "minioadmin"
    minio_root_password: str = "minioadmin"
    minio_endpoint: str = "localhost:9000"
    minio_use_ssl: bool = False
    minio_bucket_name: str = "mlflow-artifacts"

    # MLflow Configuration
    mlflow_tracking_uri: str = "http://localhost:5000"
    mlflow_s3_endpoint_url: str = "http://localhost:9000"
    aws_access_key_id: str = "minioadmin"
    aws_secret_access_key: str = "minioadmin"

    # Experiment Configuration
    experiment_name: str = "dbscan-comparison"

    # Monitoring Configuration
    pushgateway_url: str = "http://localhost:9091"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()

