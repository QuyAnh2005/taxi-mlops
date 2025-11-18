"""Data loading utilities"""

import io
from pathlib import Path
from typing import Any

import pandas as pd

from ..config import settings
from ..storage import MinIOClient


class DataLoader:
    """Load data from various sources (MinIO preferred)"""

    @staticmethod
    def load_from_file(file_path: str | Path) -> pd.DataFrame:
        """
        Load data from a local parquet file

        Args:
            file_path: Path to the parquet file

        Returns:
            Loaded DataFrame
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if file_path.suffix == ".parquet":
            return pd.read_parquet(file_path)
        elif file_path.suffix == ".csv":
            return pd.read_csv(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

    @staticmethod
    def load_from_minio(
        object_name: str,
        bucket_name: str | None = None,
        minio_client: MinIOClient | None = None,
    ) -> pd.DataFrame:
        """
        Load data from MinIO (preferred method)

        Args:
            object_name: Object name in MinIO
            bucket_name: Bucket name (optional, uses default from config)
            minio_client: MinIO client instance (optional, creates new if not provided)

        Returns:
            Loaded DataFrame
        """
        if minio_client is None:
            minio_client = MinIOClient(bucket_name=bucket_name)

        data_bytes = minio_client.download_bytes(object_name, bucket_name)
        return pd.read_parquet(io.BytesIO(data_bytes))

    @staticmethod
    def load_data(
        source: str,
        bucket_name: str | None = None,
        minio_client: MinIOClient | None = None,
    ) -> pd.DataFrame:
        """
        Load data from MinIO or local file (MinIO preferred)

        This method tries to load from MinIO first. If the object doesn't exist
        or MinIO is unavailable, it falls back to local file system.

        Args:
            source: Object name in MinIO or local file path
            bucket_name: Bucket name for MinIO (optional)
            minio_client: MinIO client instance (optional)

        Returns:
            Loaded DataFrame
        """
        # Try MinIO first
        try:
            if minio_client is None:
                # Use taxi-data bucket for data by default, or specified bucket
                data_bucket = bucket_name or "taxi-data"
                minio_client = MinIOClient(bucket_name=data_bucket)

            # Try to download directly - if it fails, object doesn't exist
            try:
                return DataLoader.load_from_minio(source, data_bucket, minio_client)
            except Exception as download_error:
                # Object might not exist, try local file
                print(f"Warning: Could not load '{source}' from MinIO ({download_error}), trying local file...")
                raise download_error
        except Exception as e:
            # If MinIO fails completely, try local file as fallback
            try:
                return DataLoader.load_from_file(source)
            except FileNotFoundError:
                raise FileNotFoundError(
                    f"Data source not found in MinIO or local filesystem: {source}\n"
                    f"MinIO error: {e}\n"
                    f"Please upload the file to MinIO first using: python scripts/upload_to_minio.py <file>"
                )

