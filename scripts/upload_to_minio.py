#!/usr/bin/env python3
"""Script to upload data files to MinIO"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage import MinIOClient


def main():
    parser = argparse.ArgumentParser(
        description="Upload data files to MinIO",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Upload a single file
  python scripts/upload_to_minio.py data/yellow_tripdata_2025-09.parquet

  # Upload with custom object name
  python scripts/upload_to_minio.py data/yellow_tripdata_2025-09.parquet \\
    --object-name taxi-data/yellow_tripdata_2025-09.parquet

  # Upload all parquet files in a directory
  python scripts/upload_to_minio.py data/ --recursive

  # Upload to specific bucket
  python scripts/upload_to_minio.py data/file.parquet --bucket-name my-bucket
        """,
    )
    parser.add_argument(
        "source",
        type=str,
        help="Source file or directory path",
    )
    parser.add_argument(
        "--object-name",
        type=str,
        default=None,
        help="Object name in MinIO (default: same as source path)",
    )
    parser.add_argument(
        "--bucket-name",
        type=str,
        default=None,
        help="Bucket name (default: from config)",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Upload all files recursively from directory",
    )
    parser.add_argument(
        "--prefix",
        type=str,
        default="",
        help="Prefix for object names when uploading directory",
    )

    args = parser.parse_args()

    source_path = Path(args.source)
    if not source_path.exists():
        print(f"Error: Source path does not exist: {source_path}")
        return 1

    # Initialize MinIO client
    try:
        client = MinIOClient(bucket_name=args.bucket_name)
        print(f"Connected to MinIO at {client.endpoint}")
        print(f"Using bucket: {client.bucket_name}")
    except Exception as e:
        print(f"Error connecting to MinIO: {e}")
        print("Make sure MinIO is running: docker-compose ps minio")
        return 1

    uploaded_files = []

    if source_path.is_file():
        # Upload single file
        object_name = args.object_name or str(source_path)
        print(f"\nUploading {source_path} -> {object_name}...")
        try:
            url = client.upload_file(str(source_path), object_name, args.bucket_name)
            print(f"✓ Uploaded successfully: {url}")
            uploaded_files.append((str(source_path), object_name, url))
        except Exception as e:
            print(f"✗ Upload failed: {e}")
            return 1

    elif source_path.is_dir() and args.recursive:
        # Upload directory recursively
        print(f"\nUploading files from {source_path} (recursive)...")
        pattern = "**/*.parquet" if args.recursive else "*.parquet"
        files = list(source_path.glob(pattern))

        if not files:
            print(f"No parquet files found in {source_path}")
            return 1

        for file_path in files:
            # Create object name with prefix
            relative_path = file_path.relative_to(source_path.parent)
            object_name = args.prefix + str(relative_path) if args.prefix else str(relative_path)
            object_name = object_name.replace("\\", "/")  # Normalize path separators

            print(f"  Uploading {file_path.name} -> {object_name}...")
            try:
                url = client.upload_file(str(file_path), object_name, args.bucket_name)
                print(f"    ✓ {url}")
                uploaded_files.append((str(file_path), object_name, url))
            except Exception as e:
                print(f"    ✗ Failed: {e}")
                return 1

    else:
        print(f"Error: {source_path} is a directory. Use --recursive to upload directory contents.")
        return 1

    print("\n" + "=" * 70)
    print("Upload Summary")
    print("=" * 70)
    print(f"Total files uploaded: {len(uploaded_files)}")
    print("\nUploaded files:")
    for local_path, object_name, url in uploaded_files:
        print(f"  {local_path}")
        print(f"    -> {object_name}")
        print(f"    URL: {url}")
    print("=" * 70)

    print("\nTo use these files in workflows, use the object name:")
    for _, object_name, _ in uploaded_files:
        print(f"  --data-object {object_name}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

