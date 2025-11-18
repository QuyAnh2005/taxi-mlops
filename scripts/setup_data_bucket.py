#!/usr/bin/env python3
"""Script to set up data bucket in MinIO"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import settings
from src.storage import MinIOClient


def main():
    """Create data bucket in MinIO"""
    print("Setting up data bucket in MinIO...")
    
    # Create a separate bucket for data (different from MLflow artifacts)
    data_bucket = "taxi-data"
    
    try:
        client = MinIOClient(bucket_name=data_bucket)
        print(f"✓ Data bucket '{data_bucket}' is ready!")
        print(f"MinIO endpoint: {client.endpoint}")
        print(f"\nTo upload data:")
        print(f"  python scripts/upload_to_minio.py <file> --bucket-name {data_bucket}")
        return 0
    except Exception as e:
        print(f"✗ Failed to create data bucket: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

