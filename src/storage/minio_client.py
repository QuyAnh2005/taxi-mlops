"""MinIO client for object storage"""

import io
from typing import Any

from minio import Minio
from minio.error import S3Error

from ..config import settings


class MinIOClient:
    """Client for interacting with MinIO object storage"""

    def __init__(
        self,
        endpoint: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
        secure: bool | None = None,
        bucket_name: str | None = None,
    ):
        """
        Initialize MinIO client

        Args:
            endpoint: MinIO endpoint (default: from settings)
            access_key: Access key (default: from settings)
            secret_key: Secret key (default: from settings)
            secure: Use SSL (default: from settings)
            bucket_name: Default bucket name (default: from settings)
        """
        self.endpoint = endpoint or settings.minio_endpoint
        self.access_key = access_key or settings.minio_root_user
        self.secret_key = secret_key or settings.minio_root_password
        self.secure = secure if secure is not None else settings.minio_use_ssl
        self.bucket_name = bucket_name or settings.minio_bucket_name

        self.client = Minio(
            self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure,
        )

        # Ensure bucket exists
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self) -> None:
        """Create bucket if it doesn't exist"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
        except S3Error as e:
            raise RuntimeError(f"Failed to create bucket {self.bucket_name}: {e}") from e

    def upload_file(
        self, file_path: str, object_name: str, bucket_name: str | None = None
    ) -> str:
        """
        Upload a file to MinIO

        Args:
            file_path: Local file path
            object_name: Object name in MinIO
            bucket_name: Bucket name (default: configured bucket)

        Returns:
            Object URL
        """
        bucket = bucket_name or self.bucket_name
        try:
            self.client.fput_object(bucket, object_name, file_path)
            return f"s3://{bucket}/{object_name}"
        except S3Error as e:
            raise RuntimeError(f"Failed to upload {object_name}: {e}") from e

    def upload_bytes(
        self, data: bytes, object_name: str, bucket_name: str | None = None
    ) -> str:
        """
        Upload bytes to MinIO

        Args:
            data: Data bytes
            object_name: Object name in MinIO
            bucket_name: Bucket name (default: configured bucket)

        Returns:
            Object URL
        """
        bucket = bucket_name or self.bucket_name
        try:
            data_stream = io.BytesIO(data)
            self.client.put_object(
                bucket, object_name, data_stream, length=len(data)
            )
            return f"s3://{bucket}/{object_name}"
        except S3Error as e:
            raise RuntimeError(f"Failed to upload {object_name}: {e}") from e

    def download_file(
        self, object_name: str, file_path: str, bucket_name: str | None = None
    ) -> None:
        """
        Download a file from MinIO

        Args:
            object_name: Object name in MinIO
            file_path: Local file path to save to
            bucket_name: Bucket name (default: configured bucket)
        """
        bucket = bucket_name or self.bucket_name
        try:
            self.client.fget_object(bucket, object_name, file_path)
        except S3Error as e:
            raise RuntimeError(f"Failed to download {object_name}: {e}") from e

    def download_bytes(
        self, object_name: str, bucket_name: str | None = None
    ) -> bytes:
        """
        Download bytes from MinIO

        Args:
            object_name: Object name in MinIO
            bucket_name: Bucket name (default: configured bucket)

        Returns:
            Data bytes
        """
        bucket = bucket_name or self.bucket_name
        try:
            response = self.client.get_object(bucket, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            raise RuntimeError(f"Failed to download {object_name}: {e}") from e

    def list_objects(
        self, prefix: str = "", bucket_name: str | None = None
    ) -> list[str]:
        """
        List objects in bucket

        Args:
            prefix: Object name prefix filter
            bucket_name: Bucket name (default: configured bucket)

        Returns:
            List of object names
        """
        bucket = bucket_name or self.bucket_name
        try:
            objects = self.client.list_objects(bucket, prefix=prefix, recursive=True)
            return [obj.object_name for obj in objects]
        except S3Error as e:
            raise RuntimeError(f"Failed to list objects: {e}") from e

    def delete_object(
        self, object_name: str, bucket_name: str | None = None
    ) -> None:
        """
        Delete an object from MinIO

        Args:
            object_name: Object name in MinIO
            bucket_name: Bucket name (default: configured bucket)
        """
        bucket = bucket_name or self.bucket_name
        try:
            self.client.remove_object(bucket, object_name)
        except S3Error as e:
            raise RuntimeError(f"Failed to delete {object_name}: {e}") from e

