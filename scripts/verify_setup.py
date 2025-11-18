#!/usr/bin/env python3
"""Script to verify the setup is working correctly"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import settings
from src.storage import MinIOClient, PostgresClient


def check_postgres():
    """Check PostgreSQL connection"""
    try:
        client = PostgresClient()
        client.create_experiment_table()
        print("✓ PostgreSQL connection successful")
        return True
    except Exception as e:
        print(f"✗ PostgreSQL connection failed: {e}")
        return False


def check_minio():
    """Check MinIO connection"""
    try:
        client = MinIOClient()
        # Try to list objects
        client.list_objects()
        print("✓ MinIO connection successful")
        return True
    except Exception as e:
        print(f"✗ MinIO connection failed: {e}")
        return False


def check_prefect():
    """Check Prefect API"""
    try:
        import requests

        response = requests.get(f"{settings.prefect_api_url}/health")
        if response.status_code == 200:
            print("✓ Prefect API accessible")
            return True
        else:
            print(f"✗ Prefect API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Prefect API check failed: {e}")
        return False


def check_mlflow():
    """Check MLflow tracking"""
    try:
        import requests
        import time

        # First check if the service is responding
        max_retries = 5
        for i in range(max_retries):
            try:
                response = requests.get(
                    f"{settings.mlflow_tracking_uri}/health", timeout=5
                )
                if response.status_code == 200:
                    break
            except requests.exceptions.ConnectionError:
                if i < max_retries - 1:
                    time.sleep(2)
                    continue
                else:
                    raise

        # Now check MLflow API
        import mlflow

        mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
        experiments = mlflow.search_experiments()
        print("✓ MLflow tracking accessible")
        return True
    except Exception as e:
        print(f"✗ MLflow tracking check failed: {e}")
        print("  Hint: Make sure MLflow container is running: docker-compose ps mlflow")
        return False


def main():
    print("Verifying setup...")
    print("-" * 50)

    results = []
    results.append(("PostgreSQL", check_postgres()))
    results.append(("MinIO", check_minio()))
    results.append(("Prefect", check_prefect()))
    results.append(("MLflow", check_mlflow()))

    print("-" * 50)
    all_ok = all(result[1] for result in results)
    if all_ok:
        print("\n✓ All services are working correctly!")
        return 0
    else:
        print("\n✗ Some services are not working. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

