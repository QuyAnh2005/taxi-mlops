#!/usr/bin/env python3
"""Script to set up MinIO bucket for MLflow"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage import MinIOClient


def main():
    """Create MinIO bucket if it doesn't exist"""
    print("Setting up MinIO bucket for MLflow artifacts...")
    client = MinIOClient()
    print(f"Bucket '{client.bucket_name}' is ready!")
    print(f"MinIO endpoint: {client.endpoint}")


if __name__ == "__main__":
    main()

