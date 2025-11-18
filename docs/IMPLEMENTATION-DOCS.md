# Distributed & Parallel DBSCAN: Complete MLOps Implementation Documentation

**Final Consolidated Edition - Using Prefect (not Airflow)**

---

## Executive Summary

This documentation provides a complete blueprint for building a production-grade MLOps platform to evaluate and compare DBSCAN clustering implementations across different frameworks. The project leverages existing, battle-tested implementations and uses **Prefect** for modern workflow orchestration.

**Key Changes from Previous Version:**
- ✅ **Prefect** instead of Airflow for workflow orchestration
- ✅ Modern, Pythonic workflow definitions
- ✅ Better developer experience
- ✅ Easier debugging and testing
- ✅ Native async support
- ✅ Self-hosted Prefect Server (no cloud dependency)

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture Design](#2-architecture-design)
3. [Complete Folder Structure](#3-complete-folder-structure)
4. [Technical Requirements](#4-technical-requirements)
5. [Prefect Workflow Orchestration](#5-prefect-workflow-orchestration)
6. [Component Specifications](#6-component-specifications)
7. [Data Management](#7-data-management)
8. [Experiment Tracking & MLflow](#8-experiment-tracking--mlflow)
9. [Monitoring & Observability](#9-monitoring--observability)
10. [Evaluation Framework](#10-evaluation-framework)
11. [Docker Compose Deployment](#11-docker-compose-deployment)
12. [Configuration Management](#12-configuration-management)
13. [Testing Strategy](#13-testing-strategy)
14. [CI/CD Pipeline](#14-cicd-pipeline)
15. [Implementation Roadmap](#15-implementation-roadmap)
16. [Documentation Requirements](#16-documentation-requirements)
17. [Success Criteria](#17-success-criteria)

---

## 1. Project Overview

### 1.1 Why Prefect Instead of Airflow?

```yaml
Prefect Advantages:

Developer Experience:
  - Pure Python (no DAG DSL)
  - Native Python debugging
  - Easier testing
  - Better IDE support
  - More intuitive API

Modern Features:
  - Native async/await support
  - Dynamic workflows
  - Parameterized flows
  - Subflows and nested flows
  - Better error handling

Deployment:
  - Simpler setup
  - Self-hosted Prefect Server
  - No scheduler complexity
  - Better resource management

Monitoring:
  - Modern UI
  - Better observability
  - Real-time updates
  - Task-level visibility

Research/Academic Context:
  - Easier to learn
  - More flexible
  - Better for experimentation
  - Rapid prototyping

Comparison:
  Airflow:
    - More mature
    - Enterprise-proven
    - Complex setup
    - DAG-based
    - Cron scheduling
  
  Prefect:
    - Modern Python
    - Simpler
    - Flow-based
    - Event-driven
    - Better DX
```

### 1.2 Implementation Matrix

| Category | Implementation | Source | Parallelization | Distribution |
|----------|---------------|--------|-----------------|--------------|
| **Sequential** | sklearn DBSCAN | `sklearn.cluster.DBSCAN` | Single-core | No |
| **Parallel** | sklearn DBSCAN | `sklearn.cluster.DBSCAN(n_jobs=-1)` | Multi-core | No |
| **Distributed** | Spark DBSCAN | Third-party library | Multi-node | Yes |

---

## 2. Architecture Design

### 2.1 System Architecture with Prefect

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Web UI     │  │   CLI Tool   │  │   Jupyter    │         │
│  │  (Streamlit) │  │   (Typer)    │  │   Notebook   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     API Gateway Layer                            │
│              FastAPI REST API + WebSockets                       │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              Orchestration & Tracking Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Experiment  │  │   Workflow   │  │     Task     │         │
│  │   Tracker    │  │ Orchestrator │  │    Queue     │         │
│  │   (MLflow)   │  │  (Prefect)   │  │   (Celery)   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                   │
│  Prefect Components:                                             │
│  ┌────────────────────────────────────────────────────┐         │
│  │ Prefect Server → Prefect Agent → Flow Runs         │         │
│  │ (API & UI)       (Workers)        (Execution)       │         │
│  └────────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Algorithm Adapter Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   sklearn    │  │   sklearn    │  │    Spark     │         │
│  │   Adapter    │  │  Parallel    │  │   Adapter    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              Existing DBSCAN Implementations                     │
│  [sklearn DBSCAN]  [sklearn Parallel]  [Spark DBSCAN]          │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data & Storage Layer                          │
│  [PostgreSQL]  [MinIO]  [Redis]                                 │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│               Monitoring & Observability Layer                   │
│  [Prometheus]  [Grafana]  [Loki]  [Jaeger]                     │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Prefect Architecture

```
Prefect Components:

1. Prefect Server:
   - API server
   - Web UI (http://localhost:4200)
   - Flow orchestration
   - Run history
   - Work queues

2. Prefect Agent:
   - Executes flows
   - Polls for work
   - Manages resources
   - Multiple agents supported

3. Storage:
   - PostgreSQL backend
   - Stores flow metadata
   - Run history
   - Logs

4. Work Queues:
   - Named queues for routing
   - Priority support
   - Concurrency limits

Flow Execution:
  User triggers flow
    ↓
  Prefect Server schedules
    ↓
  Agent polls queue
    ↓
  Agent executes flow
    ↓
  Tasks run in sequence/parallel
    ↓
  Results stored
    ↓
  Status updated in UI
```

---

## 3. Complete Folder Structure

```
dbscan-mlops-project/
│
├── README.md
├── LICENSE
├── .gitignore
├── .dockerignore
├── .env.example
├── Makefile
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── setup.py
│
├── docker/                            # Docker configurations
│   ├── docker-compose.yml             # Main compose file
│   ├── docker-compose.dev.yml         # Development overrides
│   ├── docker-compose.prod.yml        # Production overrides
│   ├── docker-compose.spark.yml       # Spark cluster extension
│   ├── docker-compose.monitoring.yml  # Monitoring stack
│   │
│   ├── Dockerfile.base                # Base Python image
│   ├── Dockerfile.api                 # API service
│   ├── Dockerfile.prefect-agent       # Prefect agent
│   ├── Dockerfile.notebook            # Jupyter notebook
│   ├── Dockerfile.mlflow              # MLflow server
│   │
│   ├── spark/
│   │   ├── Dockerfile.spark
│   │   ├── spark-defaults.conf
│   │   └── spark-env.sh
│   │
│   └── nginx/
│       ├── nginx.conf
│       └── ssl/
│
├── config/                            # Configuration files
│   ├── __init__.py
│   ├── default.yaml
│   ├── development.yaml
│   ├── production.yaml
│   │
│   ├── algorithms/
│   │   ├── sklearn_sequential.yaml
│   │   ├── sklearn_parallel.yaml
│   │   └── spark_distributed.yaml
│   │
│   ├── storage/
│   │   ├── minio.yaml
│   │   ├── postgres.yaml
│   │   └── redis.yaml
│   │
│   ├── frameworks/
│   │   └── spark_cluster.yaml
│   │
│   ├── prefect/                       # Prefect configurations
│   │   ├── server_config.yaml
│   │   ├── agent_config.yaml
│   │   └── work_pools.yaml
│   │
│   └── monitoring/
│       ├── prometheus/
│       ├── grafana/
│       └── loki/
│
├── src/                               # Source code
│   ├── __init__.py
│   │
│   ├── core/                          # Core abstractions
│   │   ├── __init__.py
│   │   ├── base_algorithm.py
│   │   ├── algorithm_factory.py
│   │   ├── registry.py
│   │   ├── exceptions.py
│   │   ├── types.py
│   │   └── config.py
│   │
│   ├── adapters/                      # Algorithm adapters
│   │   ├── __init__.py
│   │   ├── sklearn_adapter.py
│   │   ├── sklearn_parallel_adapter.py
│   │   ├── spark_adapter.py
│   │   └── base_adapter.py
│   │
│   ├── frameworks/                    # Framework management
│   │   ├── __init__.py
│   │   └── spark/
│   │       ├── __init__.py
│   │       ├── spark_manager.py
│   │       ├── spark_config.py
│   │       └── spark_utils.py
│   │
│   ├── data/                          # Data handling
│   │   ├── __init__.py
│   │   ├── loaders/
│   │   ├── validators/
│   │   ├── preprocessors/
│   │   └── cache/
│   │
│   ├── storage/                       # Storage integrations
│   │   ├── __init__.py
│   │   ├── minio_client.py
│   │   ├── postgres_client.py
│   │   └── redis_client.py
│   │
│   ├── evaluation/                    # Evaluation metrics
│   │   ├── __init__.py
│   │   ├── quality_metrics.py
│   │   ├── performance_metrics.py
│   │   ├── scalability_metrics.py
│   │   ├── resource_metrics.py
│   │   ├── comparators.py
│   │   └── statistical_tests.py
│   │
│   ├── monitoring/                    # Monitoring & observability
│   │   ├── __init__.py
│   │   ├── metrics/
│   │   ├── logging/
│   │   ├── tracing/
│   │   └── alerts/
│   │
│   ├── experiments/                   # Experiment management
│   │   ├── __init__.py
│   │   ├── runner.py
│   │   ├── config.py
│   │   ├── parameter_grid.py
│   │   ├── mlflow_tracker.py
│   │   ├── reproducibility.py
│   │   └── templates.py
│   │
│   ├── orchestration/                 # Workflow orchestration with Prefect
│   │   ├── __init__.py
│   │   │
│   │   ├── flows/                     # Prefect flows
│   │   │   ├── __init__.py
│   │   │   ├── data_ingestion.py      # Data ingestion flow
│   │   │   ├── experiment_pipeline.py # Experiment execution flow
│   │   │   ├── evaluation_flow.py     # Evaluation flow
│   │   │   ├── comparison_flow.py     # Algorithm comparison flow
│   │   │   ├── scalability_flow.py    # Scalability testing flow
│   │   │   └── monitoring_flow.py     # Monitoring flow
│   │   │
│   │   ├── tasks/                     # Prefect tasks
│   │   │   ├── __init__.py
│   │   │   ├── data_tasks.py          # Data loading/processing tasks
│   │   │   ├── algorithm_tasks.py     # Algorithm execution tasks
│   │   │   ├── evaluation_tasks.py    # Evaluation tasks
│   │   │   ├── storage_tasks.py       # Storage operations
│   │   │   └── notification_tasks.py  # Notification tasks
│   │   │
│   │   ├── deployments/               # Prefect deployments
│   │   │   ├── __init__.py
│   │   │   ├── deploy_experiments.py  # Deploy experiment flows
│   │   │   └── deploy_monitoring.py   # Deploy monitoring flows
│   │   │
│   │   ├── blocks/                    # Prefect blocks (storage, secrets)
│   │   │   ├── __init__.py
│   │   │   ├── storage_blocks.py
│   │   │   └── secret_blocks.py
│   │   │
│   │   ├── schedules/                 # Prefect schedules
│   │   │   ├── __init__.py
│   │   │   └── experiment_schedules.py
│   │   │
│   │   └── utilities/                 # Prefect utilities
│   │       ├── __init__.py
│   │       ├── flow_utils.py
│   │       └── result_handlers.py
│   │
│   ├── api/                           # API services
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── algorithms.py
│   │   │   ├── experiments.py
│   │   │   ├── datasets.py
│   │   │   ├── results.py
│   │   │   ├── monitoring.py
│   │   │   ├── prefect_flows.py       # Trigger Prefect flows via API
│   │   │   └── health.py
│   │   │
│   │   ├── schemas/
│   │   ├── dependencies.py
│   │   ├── middleware.py
│   │   └── websockets.py
│   │
│   ├── cli/                           # Command-line interface
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── commands/
│   │       ├── __init__.py
│   │       ├── run.py
│   │       ├── evaluate.py
│   │       ├── data.py
│   │       ├── docker.py
│   │       ├── monitor.py
│   │       └── prefect_cmd.py         # Prefect-specific commands
│   │
│   ├── ui/                            # User interface
│   │   ├── __init__.py
│   │   ├── app.py
│   │   └── pages/
│   │       ├── __init__.py
│   │       ├── dashboard.py
│   │       ├── experiments.py
│   │       ├── comparison.py
│   │       ├── datasets.py
│   │       ├── monitoring.py
│   │       └── prefect_flows.py       # Prefect flow monitoring
│   │
│   └── utils/
│       ├── __init__.py
│       ├── config_loader.py
│       ├── file_utils.py
│       ├── math_utils.py
│       ├── time_utils.py
│       ├── docker_utils.py
│       ├── visualization.py
│       └── helpers.py
│
├── tests/                             # Test suite
│   ├── __init__.py
│   ├── conftest.py
│   │
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_adapters/
│   │   ├── test_data/
│   │   ├── test_evaluation/
│   │   ├── test_prefect_tasks/        # Test Prefect tasks
│   │   └── test_utils/
│   │
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_sklearn_integration.py
│   │   ├── test_spark_integration.py
│   │   ├── test_api.py
│   │   ├── test_prefect_flows.py      # Test Prefect flows
│   │   └── test_storage.py
│   │
│   ├── performance/
│   │   ├── __init__.py
│   │   ├── benchmarks.py
│   │   ├── test_scalability.py
│   │   └── test_load.py
│   │
│   └── e2e/
│       ├── __init__.py
│       └── test_full_pipeline.py
│
├── scripts/                           # Utility scripts
│   ├── setup/
│   │   ├── install_dependencies.sh
│   │   ├── setup_local_env.sh
│   │   ├── init_databases.sh
│   │   ├── init_minio.sh
│   │   ├── init_monitoring.sh
│   │   ├── init_prefect.sh            # Initialize Prefect
│   │   └── generate_ssl_certs.sh
│   │
│   ├── docker/
│   │   ├── build_all.sh
│   │   ├── start_all.sh
│   │   ├── stop_all.sh
│   │   ├── restart_service.sh
│   │   ├── logs.sh
│   │   ├── health_check.sh
│   │   └── clean_volumes.sh
│   │
│   ├── data/
│   │   ├── download_datasets.py
│   │   ├── generate_synthetic.py
│   │   ├── upload_to_minio.py
│   │   └── validate_data.py
│   │
│   ├── experiments/
│   │   ├── run_baseline.py
│   │   ├── run_scalability.py
│   │   ├── run_comparison.py
│   │   ├── run_parameter_sweep.py
│   │   └── generate_report.py
│   │
│   ├── prefect/                       # Prefect-specific scripts
│   │   ├── start_agent.sh
│   │   ├── register_flows.py
│   │   ├── create_deployments.py
│   │   ├── trigger_flow.py
│   │   └── view_flow_runs.py
│   │
│   └── maintenance/
│       ├── backup_postgres.sh
│       ├── backup_minio.sh
│       ├── restore_postgres.sh
│       ├── restore_minio.sh
│       └── cleanup_experiments.py
│
├── notebooks/                         # Jupyter notebooks
│   ├── 01_data_exploration.ipynb
│   ├── 02_sklearn_baseline.ipynb
│   ├── 03_sklearn_parallel.ipynb
│   ├── 04_spark_distributed.ipynb
│   ├── 05_framework_comparison.ipynb
│   ├── 06_scalability_analysis.ipynb
│   ├── 07_parameter_sensitivity.ipynb
│   ├── 08_prefect_workflows.ipynb     # Prefect workflow examples
│   └── 09_visualization.ipynb
│
├── prefect_deployments/               # Prefect deployment definitions
│   ├── experiment_deployment.yaml
│   ├── monitoring_deployment.yaml
│   └── evaluation_deployment.yaml
│
├── data/                              # Data directory
│   ├── raw/
│   ├── processed/
│   ├── cache/
│   └── metadata/
│       └── catalog.yaml
│
├── results/                           # Experiment results
│   ├── experiments/
│   ├── comparisons/
│   ├── reports/
│   └── artifacts/
│
├── mlruns/                            # MLflow tracking
├── logs/                              # Application logs
├── volumes/                           # Docker volumes
│
└── docs/                              # Documentation
    ├── README.md
    ├── architecture/
    │   ├── system_design.md
    │   ├── adapter_pattern.md
    │   ├── prefect_architecture.md    # Prefect-specific docs
    │   └── data_flow.md
    ├── algorithms/
    ├── deployment/
    ├── storage/
    ├── monitoring/
    ├── prefect/                       # Prefect documentation
    │   ├── getting_started.md
    │   ├── creating_flows.md
    │   ├── deployments.md
    │   └── best_practices.md
    ├── user_guides/
    ├── developer_guides/
    ├── api/
    └── images/
```

---

## 4. Technical Requirements

### 4.1 Python Dependencies

```python
# requirements.txt

# ===== Core Algorithm Libraries =====
scikit-learn>=1.3.0
numpy>=1.24.0
scipy>=1.10.0
pandas>=2.0.0

# ===== Distributed Computing =====
pyspark>=3.4.0

# ===== Data Handling =====
pyarrow>=12.0.0
h5py>=3.9.0

# ===== Storage =====
minio>=7.1.15
psycopg2-binary>=2.9.7
sqlalchemy>=2.0.20
alembic>=1.12.0
redis>=5.0.0

# ===== Workflow Orchestration - PREFECT =====
prefect>=2.14.0
# Prefect provides:
#   - Modern workflow orchestration
#   - Native Python API
#   - Self-hosted server
#   - Web UI
#   - Real-time monitoring

# Prefect extras (optional but recommended)
prefect[postgresql]>=2.14.0  # PostgreSQL backend
prefect[redis]>=2.14.0       # Redis for caching
prefect[dask]>=2.14.0        # Dask integration (optional)

# ===== MLOps & Experiment Tracking =====
mlflow>=2.7.0
celery>=5.3.1                # Still useful for background tasks
celery[redis]>=5.3.1

# ===== API & Web =====
fastapi>=0.103.0
uvicorn[standard]>=0.23.0
pydantic>=2.4.0
pydantic-settings>=2.0.0
python-multipart>=0.0.6
websockets>=11.0

# ===== UI =====
streamlit>=1.27.0
typer[all]>=0.9.0
rich>=13.5.0

# ===== Monitoring =====
prometheus-client>=0.17.0
prometheus-fastapi-instrumentator>=6.1.0
opentelemetry-api>=1.20.0
opentelemetry-sdk>=1.20.0
opentelemetry-instrumentation-fastapi>=0.41b0
opentelemetry-exporter-jaeger>=1.20.0

# ===== Configuration =====
pyyaml>=6.0.1
python-dotenv>=1.0.0
hydra-core>=1.3.2
omegaconf>=2.3.0

# ===== Utilities =====
tqdm>=4.66.0
psutil>=5.9.5
structlog>=23.1.0
python-json-logger>=2.0.7

# ===== Visualization =====
matplotlib>=3.8.0
seaborn>=0.12.2
plotly>=5.17.0

# ===== Testing =====
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-asyncio>=0.21.1
pytest-docker>=2.0.0
pytest-xdist>=3.3.1
locust>=2.16.0

# ===== Code Quality =====
black>=23.9.0
isort>=5.12.0
flake8>=6.1.0
mypy>=1.5.0
pylint>=2.17.5
pre-commit>=3.4.0
bandit>=1.7.5

# ===== Documentation =====
mkdocs>=1.5.0
mkdocs-material>=9.2.0
mkdocstrings[python]>=0.23.0
```

### 4.2 Docker Images

```yaml
Base Images:

Application Services:
  Python Base: python:3.11-slim-bookworm
  Target Size: <500 MB per service

Data Services:
  PostgreSQL: postgres:15-alpine
  Redis: redis:7-alpine
  MinIO: minio/minio:latest

Distributed Computing:
  Spark: bitnami/spark:3.5

MLOps & Orchestration:
  MLflow: Built from python:3.11-slim + mlflow
  Prefect Server: prefecthq/prefect:2-python3.11
  Prefect Agent: Custom (based on python:3.11-slim + prefect)

Monitoring:
  Prometheus: prom/prometheus:latest
  Grafana: grafana/grafana:10.1.0
  Loki: grafana/loki:2.9.0
  Promtail: grafana/promtail:2.9.0
  Jaeger: jaegertracing/all-in-one:1.49
  Node Exporter: prom/node-exporter:latest
  cAdvisor: gcr.io/cadvisor/cadvisor:latest

Reverse Proxy (Optional):
  Nginx: nginx:alpine
```

---

## 5. Prefect Workflow Orchestration

### 5.1 Prefect Architecture Overview

```
Prefect Components in Our System:

1. Prefect Server:
   - Orchestration engine
   - API server (GraphQL)
   - Web UI (React)
   - Flow registry
   - Run history
   - Work queues management

2. Prefect Database:
   - PostgreSQL backend
   - Stores flow metadata
   - Run states and history
   - Logs
   - Artifacts

3. Prefect Agent:
   - Polls work queues
   - Executes flows
   - Reports status
   - Multiple agents supported

4. Work Queues:
   - Route flows to agents
   - Priority support
   - Concurrency limits
   - Named queues (e.g., 'experiments', 'monitoring')

Prefect vs Airflow Comparison:

Feature              | Airflow          | Prefect
---------------------|------------------|------------------
DAG Definition       | DAG DSL          | Pure Python
Dynamic Workflows    | Limited          | Full support
Debugging            | Complex          | Easy (Python debug)
Testing              | Difficult        | Standard pytest
Setup Complexity     | High             | Low
Modern Python        | No               | Yes (async/await)
UI                   | Traditional      | Modern
API                  | REST             | GraphQL + REST
Scheduling           | Cron-based       | Event-driven
Community            | Large, mature    | Growing, modern
```

### 5.2 Prefect Flows

#### 5.2.1 Basic Flow Example

```python
# src/orchestration/flows/experiment_pipeline.py

from prefect import flow, task
from typing import Dict, Any
import numpy as np

from src.core.algorithm_factory import AlgorithmFactory
from src.data.loaders.minio_loader import MinIOLoader
from src.experiments.mlflow_tracker import MLflowTracker
from src.monitoring.logging.structured_logger import get_logger

logger = get_logger(__name__)

@task(name="load_dataset", retries=3, retry_delay_seconds=10)
def load_dataset(dataset_path: str) -> np.ndarray:
    """
    Load dataset from storage.
    
    Prefect task with automatic retries.
    """
    logger.info(f"Loading dataset: {dataset_path}")
    
    loader = MinIOLoader()
    data = loader.load(dataset_path)
    
    logger.info(f"Loaded {len(data)} samples")
    return data

@task(name="validate_dataset")
def validate_dataset(data: np.ndarray) -> bool:
    """Validate dataset quality."""
    logger.info("Validating dataset")
    
    # Check for NaN
    if np.isnan(data).any():
        raise ValueError("Dataset contains NaN values")
    
    # Check shape
    if len(data.shape) != 2:
        raise ValueError(f"Expected 2D array, got shape {data.shape}")
    
    logger.info("Dataset validation passed")
    return True

@task(name="run_algorithm")
def run_algorithm(
    algorithm_name: str,
    config: Dict[str, Any],
    data: np.ndarray
) -> Dict[str, Any]:
    """
    Execute DBSCAN algorithm.
    
    Returns results and metrics.
    """
    logger.info(f"Running {algorithm_name} on {len(data)} samples")
    
    # Create adapter
    adapter = AlgorithmFactory.create(algorithm_name, config)
    
    # Execute
    adapter.fit(data)
    
    # Get results
    results = {
        'labels': adapter.get_labels(),
        'metrics': adapter.get_metrics(),
        'params': adapter.get_params()
    }
    
    # Cleanup
    adapter.cleanup()
    
    logger.info(f"Algorithm completed: {results['metrics']['n_clusters']} clusters")
    return results

@task(name="store_results")
def store_results(
    results: Dict[str, Any],
    experiment_id: str
) -> str:
    """Store results to storage."""
    from src.storage.postgres_client import PostgresClient
    from src.storage.minio_client import MinIOClient
    import pickle
    
    logger.info(f"Storing results for experiment {experiment_id}")
    
    # Store labels to MinIO
    minio_client = MinIOClient()
    labels_path = f"results/{experiment_id}/labels.pkl"
    minio_client.upload_bytes(
        pickle.dumps(results['labels']),
        labels_path
    )
    
    # Store metrics to PostgreSQL
    pg_client = PostgresClient()
    pg_client.store_metrics(experiment_id, results['metrics'])
    
    logger.info("Results stored successfully")
    return labels_path

@flow(name="experiment_pipeline", log_prints=True)
def experiment_pipeline(
    dataset_path: str,
    algorithm_name: str,
    algorithm_config: Dict[str, Any],
    experiment_id: str,
    mlflow_experiment: str = "default"
) -> Dict[str, Any]:
    """
    Complete experiment pipeline flow.
    
    This is a Prefect Flow that orchestrates:
    1. Data loading
    2. Data validation
    3. Algorithm execution
    4. Results storage
    5. MLflow tracking
    
    Args:
        dataset_path: Path to dataset in MinIO
        algorithm_name: Algorithm to use ('sklearn', 'spark')
        algorithm_config: Algorithm configuration
        experiment_id: Unique experiment ID
        mlflow_experiment: MLflow experiment name
    
    Returns:
        Dictionary with results and metadata
    """
    logger.info(f"Starting experiment pipeline: {experiment_id}")
    
    # Initialize MLflow
    mlflow_tracker = MLflowTracker(mlflow_experiment)
    
    with mlflow_tracker.start_run(run_name=experiment_id):
        # Log parameters to MLflow
        mlflow_tracker.log_params({
            'dataset_path': dataset_path,
            'algorithm': algorithm_name,
            **algorithm_config
        })
        
        # Task 1: Load data
        data = load_dataset(dataset_path)
        
        # Task 2: Validate data
        is_valid = validate_dataset(data)
        
        if not is_valid:
            raise ValueError("Dataset validation failed")
        
        # Task 3: Run algorithm
        results = run_algorithm(algorithm_name, algorithm_config, data)
        
        # Log metrics to MLflow
        mlflow_tracker.log_metrics(results['metrics'])
        
        # Task 4: Store results
        results_path = store_results(results, experiment_id)
        
        # Log artifact to MLflow
        mlflow_tracker.set_tag('results_path', results_path)
        
        mlflow_tracker.end_run()
    
    logger.info(f"Experiment pipeline completed: {experiment_id}")
    
    return {
        'experiment_id': experiment_id,
        'status': 'success',
        'metrics': results['metrics'],
        'results_path': results_path
    }


# Usage example:
# from prefect import serve
# 
# if __name__ == "__main__":
#     # Run flow locally
#     result = experiment_pipeline(
#         dataset_path="raw/mnist/train.parquet",
#         algorithm_name="sklearn",
#         algorithm_config={'eps': 0.5, 'min_samples': 5},
#         experiment_id="exp_001"
#     )
```

#### 5.2.2 Comparison Flow (Multiple Algorithms)

```python
# src/orchestration/flows/comparison_flow.py

from prefect import flow, task
from typing import List, Dict, Any
import numpy as np
from concurrent.futures import ThreadPoolExecutor

from src.orchestration.flows.experiment_pipeline import (
    load_dataset,
    validate_dataset,
    run_algorithm,
    store_results
)

@flow(name="comparison_flow", log_prints=True)
def comparison_flow(
    dataset_path: str,
    algorithms: List[Dict[str, Any]],
    experiment_id: str
) -> Dict[str, Any]:
    """
    Compare multiple algorithms on the same dataset.
    
    Args:
        dataset_path: Path to dataset
        algorithms: List of algorithm specs:
            [
                {'name': 'sklearn', 'config': {'eps': 0.5}},
                {'name': 'spark', 'config': {'eps': 0.5}}
            ]
        experiment_id: Unique experiment ID
    
    Returns:
        Comparison results
    """
    logger = get_logger(__name__)
    logger.info(f"Starting comparison flow: {experiment_id}")
    
    # Load data once (shared across all algorithms)
    data = load_dataset(dataset_path)
    validate_dataset(data)
    
    results = {}
    
    # Run algorithms in parallel using Prefect's task concurrency
    for algo_spec in algorithms:
        algo_name = algo_spec['name']
        algo_config = algo_spec['config']
        
        logger.info(f"Running {algo_name}")
        
        # Run algorithm
        algo_results = run_algorithm(algo_name, algo_config, data)
        
        # Store results
        results_path = store_results(
            algo_results,
            f"{experiment_id}_{algo_name}"
        )
        
        results[algo_name] = {
            'metrics': algo_results['metrics'],
            'path': results_path
        }
    
    # Compare results
    comparison = compare_results(results)
    
    logger.info(f"Comparison completed: {experiment_id}")
    
    return {
        'experiment_id': experiment_id,
        'algorithms': list(results.keys()),
        'individual_results': results,
        'comparison': comparison
    }

@task(name="compare_results")
def compare_results(results: Dict[str, Any]) -> Dict[str, Any]:
    """Compare metrics across algorithms."""
    comparison = {
        'execution_times': {},
        'quality_scores': {},
        'cluster_counts': {}
    }
    
    for algo_name, algo_results in results.items():
        metrics = algo_results['metrics']
        
        comparison['execution_times'][algo_name] = metrics.get('execution_time', 0)
        comparison['quality_scores'][algo_name] = metrics.get('silhouette_score', 0)
        comparison['cluster_counts'][algo_name] = metrics.get('n_clusters', 0)
    
    # Find best algorithm by execution time
    best_time = min(comparison['execution_times'].items(), key=lambda x: x[1])
    comparison['fastest_algorithm'] = best_time[0]
    
    # Find best algorithm by quality
    best_quality = max(comparison['quality_scores'].items(), key=lambda x: x[1])
    comparison['best_quality_algorithm'] = best_quality[0]
    
    return comparison
```

#### 5.2.3 Scalability Testing Flow

```python
# src/orchestration/flows/scalability_flow.py

from prefect import flow, task
from typing import List, Dict, Any
import numpy as np

@flow(name="scalability_flow", log_prints=True)
def scalability_flow(
    dataset_sizes: List[int],
    algorithm_name: str,
    algorithm_config: Dict[str, Any],
    experiment_id: str
) -> Dict[str, Any]:
    """
    Test algorithm scalability across different dataset sizes.
    
    Args:
        dataset_sizes: List of dataset sizes to test (e.g., [1000, 10000, 100000])
        algorithm_name: Algorithm to test
        algorithm_config: Algorithm configuration
        experiment_id: Unique experiment ID
    
    Returns:
        Scalability results
    """
    from src.data.loaders.synthetic_loader import SyntheticLoader
    
    logger = get_logger(__name__)
    logger.info(f"Starting scalability flow: {experiment_id}")
    
    results = {}
    
    for size in dataset_sizes:
        logger.info(f"Testing with {size} samples")
        
        # Generate synthetic data of given size
        data = generate_synthetic_data(size, algorithm_config.get('n_features', 50))
        
        # Run algorithm
        algo_results = run_algorithm(algorithm_name, algorithm_config, data)
        
        # Store results
        results[size] = {
            'execution_time': algo_results['metrics']['execution_time'],
            'memory_mb': algo_results['metrics'].get('memory_mb', 0),
            'n_clusters': algo_results['metrics']['n_clusters'],
            'throughput': size / algo_results['metrics']['execution_time']  # points/sec
        }
    
    # Analyze scalability
    analysis = analyze_scalability(results)
    
    logger.info(f"Scalability flow completed: {experiment_id}")
    
    return {
        'experiment_id': experiment_id,
        'algorithm': algorithm_name,
        'results': results,
        'analysis': analysis
    }

@task(name="generate_synthetic_data")
def generate_synthetic_data(n_samples: int, n_features: int) -> np.ndarray:
    """Generate synthetic dataset."""
    from sklearn.datasets import make_blobs
    
    data, _ = make_blobs(
        n_samples=n_samples,
        n_features=n_features,
        centers=5,
        random_state=42
    )
    
    return data

@task(name="analyze_scalability")
def analyze_scalability(results: Dict[int, Dict]) -> Dict[str, Any]:
    """Analyze scalability results."""
    sizes = sorted(results.keys())
    times = [results[s]['execution_time'] for s in sizes]
    
    # Calculate scaling factor
    # If O(n), factor should be ~1
    # If O(n log n), factor should be slightly > 1
    # If O(n^2), factor should be ~2
    
    scaling_factors = []
    for i in range(1, len(sizes)):
        size_ratio = sizes[i] / sizes[i-1]
        time_ratio = times[i] / times[i-1]
        scaling_factor = time_ratio / size_ratio
        scaling_factors.append(scaling_factor)
    
    avg_scaling_factor = np.mean(scaling_factors)
    
    # Determine complexity class
    if avg_scaling_factor < 1.2:
        complexity = "O(n) - Linear"
    elif avg_scaling_factor < 1.5:
        complexity = "O(n log n) - Linearithmic"
    elif avg_scaling_factor < 2.5:
        complexity = "O(n^2) - Quadratic"
    else:
        complexity = "O(n^k) - Polynomial (k > 2)"
    
    return {
        'avg_scaling_factor': avg_scaling_factor,
        'estimated_complexity': complexity,
        'scaling_factors': scaling_factors
    }
```

### 5.3 Prefect Deployments

```python
# src/orchestration/deployments/deploy_experiments.py

from prefect.deployments import Deployment
from prefect.server.schemas.schedules import CronSchedule
from prefect.filesystems import LocalFileSystem

from src.orchestration.flows.experiment_pipeline import experiment_pipeline
from src.orchestration.flows.comparison_flow import comparison_flow
from src.orchestration.flows.scalability_flow import scalability_flow

# Create deployments for different flows

# Deployment 1: On-demand experiment pipeline
experiment_deployment = Deployment.build_from_flow(
    flow=experiment_pipeline,
    name="experiment-pipeline-deployment",
    work_queue_name="experiments",
    tags=["experiment", "dbscan"],
    parameters={
        "dataset_path": "raw/default/data.parquet",
        "algorithm_name": "sklearn",
        "algorithm_config": {"eps": 0.5, "min_samples": 5},
        "experiment_id": "default",
        "mlflow_experiment": "default"
    },
    description="Run a single DBSCAN experiment"
)

# Deployment 2: Scheduled comparison flow (runs daily)
comparison_deployment = Deployment.build_from_flow(
    flow=comparison_flow,
    name="daily-comparison-deployment",
    work_queue_name="comparisons",
    schedule=CronSchedule(cron="0 2 * * *"),  # Run at 2 AM daily
    tags=["comparison", "scheduled"],
    parameters={
        "dataset_path": "raw/mnist/train.parquet",
        "algorithms": [
            {"name": "sklearn", "config": {"eps": 0.5, "min_samples": 5}},
            {"name": "sklearn_parallel", "config": {"eps": 0.5, "min_samples": 5}},
            {"name": "spark", "config": {"eps": 0.5, "min_samples": 5}}
        ],
        "experiment_id": "daily-comparison"
    },
    description="Daily comparison of all algorithms"
)

# Deployment 3: On-demand scalability testing
scalability_deployment = Deployment.build_from_flow(
    flow=scalability_flow,
    name="scalability-testing-deployment",
    work_queue_name="scalability",
    tags=["scalability", "performance"],
    parameters={
        "dataset_sizes": [1000, 10000, 100000, 1000000],
        "algorithm_name": "sklearn",
        "algorithm_config": {"eps": 0.5, "min_samples": 5, "n_features": 50},
        "experiment_id": "scalability-test"
    },
    description="Test algorithm scalability"
)

if __name__ == "__main__":
    # Deploy all flows
    experiment_deployment.apply()
    comparison_deployment.apply()
    scalability_deployment.apply()
    
    print("✅ All deployments created successfully!")
    print("\nTo run a deployment:")
    print("  prefect deployment run 'experiment-pipeline/experiment-pipeline-deployment'")
    print("\nTo view deployments:")
    print("  prefect deployment ls")
```

### 5.4 Prefect Agent

```python
# scripts/prefect/start_agent.py

"""
Start Prefect agent to execute flows.

The agent polls work queues and executes flows when they're scheduled.
"""

from prefect.agent import OrionAgent
from prefect.settings import PREFECT_API_URL
import os

def start_agent():
    """Start Prefect agent."""
    
    # Get Prefect server URL from environment
    api_url = os.getenv('PREFECT_API_URL', 'http://prefect-server:4200/api')
    
    print(f"Starting Prefect agent...")
    print(f"Connecting to: {api_url}")
    
    # Create agent
    agent = OrionAgent(
        work_queues=["experiments", "comparisons", "scalability", "default"],
        prefetch_seconds=10
    )
    
    # Start agent
    print("\n✅ Agent started! Polling for work...")
    agent.start()

if __name__ == "__main__":
    start_agent()
```

### 5.5 Triggering Flows via API

```python
# src/api/routes/prefect_flows.py

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import httpx

from src.monitoring.logging.structured_logger import get_logger

router = APIRouter(prefix="/prefect", tags=["prefect"])
logger = get_logger(__name__)

class FlowRunRequest(BaseModel):
    """Request model for triggering a flow run."""
    deployment_name: str
    parameters: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None

class FlowRunResponse(BaseModel):
    """Response model for flow run."""
    flow_run_id: str
    status: str
    message: str
    ui_url: str

@router.post("/trigger-flow", response_model=FlowRunResponse)
async def trigger_flow(request: FlowRunRequest):
    """
    Trigger a Prefect flow run via API.
    
    Example:
        POST /prefect/trigger-flow
        {
            "deployment_name": "experiment-pipeline/experiment-pipeline-deployment",
            "parameters": {
                "dataset_path": "raw/mnist/train.parquet",
                "algorithm_name": "sklearn",
                "algorithm_config": {"eps": 0.5, "min_samples": 5},
                "experiment_id": "exp_123"
            },
            "tags": ["api-triggered"]
        }
    """
    logger.info(f"Triggering flow: {request.deployment_name}")
    
    try:
        # Get Prefect API URL
        import os
        prefect_api_url = os.getenv('PREFECT_API_URL', 'http://prefect-server:4200/api')
        
        # Create flow run via Prefect API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{prefect_api_url}/deployments/name/{request.deployment_name}/create_flow_run",
                json={
                    "parameters": request.parameters or {},
                    "tags": request.tags or []
                }
            )
            
            response.raise_for_status()
            flow_run_data = response.json()
        
        flow_run_id = flow_run_data['id']
        
        # Build UI URL
        ui_url = f"http://localhost:4200/flow-runs/flow-run/{flow_run_id}"
        
        logger.info(f"Flow run created: {flow_run_id}")
        
        return FlowRunResponse(
            flow_run_id=flow_run_id,
            status="scheduled",
            message="Flow run successfully triggered",
            ui_url=ui_url
        )
        
    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to trigger flow: {e}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Failed to trigger flow: {e.response.text}"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/flow-runs/{flow_run_id}")
async def get_flow_run_status(flow_run_id: str):
    """Get status of a flow run."""
    import os
    prefect_api_url = os.getenv('PREFECT_API_URL', 'http://prefect-server:4200/api')
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{prefect_api_url}/flow_runs/{flow_run_id}"
            )
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Flow run not found: {flow_run_id}"
        )

@router.get("/deployments")
async def list_deployments():
    """List all available Prefect deployments."""
    import os
    prefect_api_url = os.getenv('PREFECT_API_URL', 'http://prefect-server:4200/api')
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{prefect_api_url}/deployments/filter",
                json={}
            )
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list deployments: {e.response.text}"
        )
```

### 5.6 CLI Commands for Prefect

```python
# src/cli/commands/prefect_cmd.py

import typer
from rich.console import Console
from rich.table import Table
import httpx

app = typer.Typer(help="Prefect workflow management commands")
console = Console()

@app.command()
def trigger(
    deployment: str = typer.Argument(..., help="Deployment name (format: flow-name/deployment-name)"),
    dataset: str = typer.Option("raw/default/data.parquet", help="Dataset path"),
    algorithm: str = typer.Option("sklearn", help="Algorithm name"),
    eps: float = typer.Option(0.5, help="DBSCAN eps parameter"),
    min_samples: int = typer.Option(5, help="DBSCAN min_samples parameter"),
):
    """
    Trigger a Prefect flow run.
    
    Example:
        python -m src.cli prefect trigger experiment-pipeline/experiment-pipeline-deployment --dataset raw/mnist/train.parquet
    """
    console.print(f"[bold blue]Triggering deployment:[/bold blue] {deployment}")
    
    # Build parameters
    parameters = {
        "dataset_path": dataset,
        "algorithm_name": algorithm,
        "algorithm_config": {
            "eps": eps,
            "min_samples": min_samples
        },
        "experiment_id": f"cli_{int(time.time())}",
        "mlflow_experiment": "cli-experiments"
    }
    
    # Trigger via API
    try:
        response = httpx.post(
            "http://localhost:8000/prefect/trigger-flow",
            json={
                "deployment_name": deployment,
                "parameters": parameters,
                "tags": ["cli-triggered"]
            }
        )
        response.raise_for_status()
        result = response.json()
        
        console.print(f"[bold green]✓[/bold green] Flow run created: {result['flow_run_id']}")
        console.print(f"[bold]View in UI:[/bold] {result['ui_url']}")
        
    except httpx.HTTPStatusError as e:
        console.print(f"[bold red]✗ Failed to trigger flow:[/bold red] {e.response.text}")
        raise typer.Exit(1)

@app.command()
def status(flow_run_id: str = typer.Argument(..., help="Flow run ID")):
    """Check status of a flow run."""
    console.print(f"[bold blue]Fetching status for:[/bold blue] {flow_run_id}")
    
    try:
        response = httpx.get(f"http://localhost:8000/prefect/flow-runs/{flow_run_id}")
        response.raise_for_status()
        run_data = response.json()
        
        # Display status
        console.print(f"[bold]Status:[/bold] {run_data['state']['type']}")
        console.print(f"[bold]Name:[/bold] {run_data['name']}")
        console.print(f"[bold]Started:[/bold] {run_data.get('start_time', 'Not started')}")
        
    except httpx.HTTPStatusError as e:
        console.print(f"[bold red]✗ Failed to get status:[/bold red] {e.response.text}")
        raise typer.Exit(1)

@app.command()
def list_deployments():
    """List all available deployments."""
    console.print("[bold blue]Available Deployments:[/bold blue]\n")
    
    try:
        response = httpx.get("http://localhost:8000/prefect/deployments")
        response.raise_for_status()
        deployments = response.json()
        
        # Create table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Name")
        table.add_column("Flow")
        table.add_column("Schedule")
        table.add_column("Work Queue")
        
        for deployment in deployments:
            table.add_row(
                deployment['name'],
                deployment['flow_name'],
                deployment.get('schedule', {}).get('cron', 'On-demand'),
                deployment.get('work_queue_name', 'default')
            )
        
        console.print(table)
        
    except httpx.HTTPStatusError as e:
        console.print(f"[bold red]✗ Failed to list deployments:[/bold red] {e}")
        raise typer.Exit(1)

@app.command()
def ui():
    """Open Prefect UI in browser."""
    import webbrowser
    url = "http://localhost:4200"
    console.print(f"[bold blue]Opening Prefect UI:[/bold blue] {url}")
    webbrowser.open(url)

if __name__ == "__main__":
    app()
```

---

## 11. Docker Compose Deployment (with Prefect)

### 11.1 Complete docker-compose.yml

```yaml
# docker/docker-compose.yml

version: '3.8'

networks:
  frontend-network:
    driver: bridge
  backend-network:
    driver: bridge
  data-network:
    driver: bridge
  monitoring-network:
    driver: bridge

volumes:
  postgres-data:
  prefect-postgres-data:  # Separate DB for Prefect
  minio-data:
  redis-data:
  prometheus-data:
  grafana-data:
  mlflow-data:

services:
  # ===== Data Layer =====
  
  postgres:
    image: postgres:15-alpine
    container_name: dbscan-postgres
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-dbscan_user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-dbscan_password}
      POSTGRES_DB: ${POSTGRES_DB:-dbscan_db}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - data-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U dbscan_user"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # Separate PostgreSQL for Prefect
  prefect-postgres:
    image: postgres:15-alpine
    container_name: prefect-postgres
    environment:
      POSTGRES_USER: prefect
      POSTGRES_PASSWORD: prefect_password
      POSTGRES_DB: prefect
    volumes:
      - prefect-postgres-data:/var/lib/postgresql/data
    ports:
      - "5433:5432"
    networks:
      - data-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U prefect"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: dbscan-redis
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data
    ports:
      - "6379:6379"
    networks:
      - data-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  minio:
    image: minio/minio:latest
    container_name: dbscan-minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: ${MINIO_ROOT_USER:-admin}
      MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD:-admin123}
    volumes:
      - minio-data:/data
    ports:
      - "9000:9000"
      - "9001:9001"
    networks:
      - data-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3
    restart: unless-stopped

  minio-init:
    image: minio/mc:latest
    container_name: dbscan-minio-init
    depends_on:
      - minio
    entrypoint: >
      /bin/sh -c "
      sleep 10;
      /usr/bin/mc alias set minio http://minio:9000 admin admin123;
      /usr/bin/mc mb minio/dbscan-data --ignore-existing;
      /usr/bin/mc policy set public minio/dbscan-data;
      exit 0;
      "
    networks:
      - data-network

  # ===== Prefect Orchestration =====
  
  prefect-server:
    image: prefecthq/prefect:2-python3.11
    container_name: prefect-server
    command: prefect server start --host 0.0.0.0
    environment:
      - PREFECT_API_DATABASE_CONNECTION_URL=postgresql+asyncpg://prefect:prefect_password@prefect-postgres:5432/prefect
      - PREFECT_SERVER_API_HOST=0.0.0.0
      - PREFECT_UI_API_URL=http://localhost:4200/api
    ports:
      - "4200:4200"  # Web UI
    volumes:
      - ./config/prefect:/config
    networks:
      - frontend-network
      - data-network
    depends_on:
      prefect-postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:4200/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  prefect-agent:
    build:
      context: .
      dockerfile: docker/Dockerfile.prefect-agent
    container_name: prefect-agent
    environment:
      - PREFECT_API_URL=http://prefect-server:4200/api
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - REDIS_URL=redis://redis:6379/0
      - MINIO_ENDPOINT=minio:9000
      - MINIO_ACCESS_KEY=${MINIO_ROOT_USER}
      - MINIO_SECRET_KEY=${MINIO_ROOT_PASSWORD}
      - MLFLOW_TRACKING_URI=http://mlflow:5000
    volumes:
      - ./src:/app/src
      - ./data:/app/data
      - ./logs/prefect:/app/logs
    networks:
      - backend-network
      - data-network
    depends_on:
      prefect-server:
        condition: service_healthy
    command: >
      prefect agent start
      --work-queue experiments
      --work-queue comparisons
      --work-queue scalability
      --work-queue default
    restart: unless-stopped

  # ===== MLOps Layer =====

  mlflow:
    build:
      context: .
      dockerfile: docker/Dockerfile.mlflow
    container_name: dbscan-mlflow
    environment:
      - MLFLOW_BACKEND_STORE_URI=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/mlflow
      - MLFLOW_S3_ENDPOINT_URL=http://minio:9000
      - AWS_ACCESS_KEY_ID=${MINIO_ROOT_USER}
      - AWS_SECRET_ACCESS_KEY=${MINIO_ROOT_PASSWORD}
    ports:
      - "5000:5000"
    volumes:
      - mlflow-data:/mlflow
    networks:
      - data-network
      - frontend-network
    depends_on:
      postgres:
        condition: service_healthy
      minio:
        condition: service_healthy
    command: >
      mlflow server
      --backend-store-uri postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/mlflow
      --default-artifact-root s3://dbscan-data/mlruns
      --host 0.0.0.0
      --port 5000
    restart: unless-stopped

  # ===== Application Layer =====

  api:
    build:
      context: .
      dockerfile: docker/Dockerfile.api
    container_name: dbscan-api
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - REDIS_URL=redis://redis:6379/0
      - MINIO_ENDPOINT=minio:9000
      - MINIO_ACCESS_KEY=${MINIO_ROOT_USER}
      - MINIO_SECRET_KEY=${MINIO_ROOT_PASSWORD}
      - MLFLOW_TRACKING_URI=http://mlflow:5000
      - PREFECT_API_URL=http://prefect-server:4200/api
    ports:
      - "8000:8000"
    volumes:
      - ./src:/app/src
      - ./data:/app/data
      - ./logs/api:/app/logs
    networks:
      - frontend-network
      - backend-network
      - data-network
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      mlflow:
        condition: service_started
      prefect-server:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  notebook:
    build:
      context: .
      dockerfile: docker/Dockerfile.notebook
    container_name: dbscan-notebook
    environment:
      - JUPYTER_ENABLE_LAB=yes
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - MINIO_ENDPOINT=minio:9000
      - MINIO_ACCESS_KEY=${MINIO_ROOT_USER}
      - MINIO_SECRET_KEY=${MINIO_ROOT_PASSWORD}
      - MLFLOW_TRACKING_URI=http://mlflow:5000
      - PREFECT_API_URL=http://prefect-server:4200/api
    ports:
      - "8888:8888"
    volumes:
      - ./notebooks:/home/jovyan/work
      - ./src:/home/jovyan/src
      - ./data:/home/jovyan/data
    networks:
      - frontend-network
      - data-network
    command: start-notebook.sh --NotebookApp.token='' --NotebookApp.password=''
    restart: unless-stopped

  # ===== Monitoring Layer =====

  prometheus:
    image: prom/prometheus:latest
    container_name: dbscan-prometheus
    volumes:
      - ./config/monitoring/prometheus:/etc/prometheus
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
    ports:
      - "9090:9090"
    networks:
      - monitoring-network
      - backend-network
      - data-network
    restart: unless-stopped

  grafana:
    image: grafana/grafana:10.1.0
    container_name: dbscan-grafana
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_INSTALL_PLUGINS=grafana-clock-panel
    volumes:
      - ./config/monitoring/grafana:/etc/grafana/provisioning
      - grafana-data:/var/lib/grafana
    ports:
      - "3000:3000"
    networks:
      - frontend-network
      - monitoring-network
    depends_on:
      - prometheus
    restart: unless-stopped

  loki:
    image: grafana/loki:2.9.0
    container_name: dbscan-loki
    volumes:
      - ./config/monitoring/loki:/etc/loki
    command: -config.file=/etc/loki/loki-config.yaml
    ports:
      - "3100:3100"
    networks:
      - monitoring-network
    restart: unless-stopped

  promtail:
    image: grafana/promtail:2.9.0
    container_name: dbscan-promtail
    volumes:
      - ./config/monitoring/promtail:/etc/promtail
      - ./logs:/var/log/app:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
    command: -config.file=/etc/promtail/promtail-config.yaml
    networks:
      - monitoring-network
    depends_on:
      - loki
    restart: unless-stopped

  jaeger:
    image: jaegertracing/all-in-one:1.49
    container_name: dbscan-jaeger
    environment:
      - COLLECTOR_ZIPKIN_HOST_PORT=:9411
    ports:
      - "16686:16686"  # UI
      - "14268:14268"  # HTTP collector
    networks:
      - monitoring-network
      - backend-network
    restart: unless-stopped

  node-exporter:
    image: prom/node-exporter:latest
    container_name: dbscan-node-exporter
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    ports:
      - "9100:9100"
    networks:
      - monitoring-network
    restart: unless-stopped

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: dbscan-cadvisor
    privileged: true
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
    ports:
      - "8080:8080"
    networks:
      - monitoring-network
    restart: unless-stopped
```

### 11.2 Prefect Agent Dockerfile

```dockerfile
# docker/Dockerfile.prefect-agent

FROM python:3.11-slim-bookworm

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ src/
COPY config/ config/

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/results

# Set Python path
ENV PYTHONPATH=/app

# Default command (can be overridden)
CMD ["prefect", "agent", "start", "--work-queue", "default"]
```

### 11.3 Deployment Scripts

```bash
# scripts/prefect/register_flows.py

#!/usr/bin/env python
"""
Register all Prefect flows and create deployments.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.orchestration.deployments.deploy_experiments import (
    experiment_deployment,
    comparison_deployment,
    scalability_deployment
)

def main():
    """Register all deployments."""
    print("🚀 Registering Prefect deployments...")
    
    # Apply deployments
    experiment_deployment.apply()
    print("✅ Experiment deployment registered")
    
    comparison_deployment.apply()
    print("✅ Comparison deployment registered")
    
    scalability_deployment.apply()
    print("✅ Scalability deployment registered")
    
    print("\n✅ All deployments registered successfully!")
    print("\nNext steps:")
    print("1. Start Prefect agent:")
    print("   docker-compose up prefect-agent")
    print("\n2. View deployments in UI:")
    print("   http://localhost:4200/deployments")
    print("\n3. Trigger a deployment:")
    print("   prefect deployment run 'experiment-pipeline/experiment-pipeline-deployment'")

if __name__ == "__main__":
    main()
```

---

## 15. Implementation Roadmap (16 Weeks) - Prefect Edition

### Updated Timeline

```
Phase 1: Foundation & Setup (Weeks 1-2)
──────────────────────────────────────
✓ Environment setup (Docker, Docker Compose)
✓ Project structure
✓ Base services (PostgreSQL, Redis, MinIO)
✓ Prefect Server + PostgreSQL setup
✓ Prefect Agent configuration
✓ Basic CI pipeline

Deliverables:
  - Docker Compose with Prefect working
  - All services deployed
  - Prefect UI accessible (http://localhost:4200)
  - CI passing

──────────────────────────────────────

Phase 2: Sklearn Integration + Simple Prefect Flows (Weeks 3-4)
────────────────────────────────────────────────────────────────
✓ SklearnAdapter implementation
✓ SklearnParallelAdapter implementation
✓ Data pipeline (loaders, validators)
✓ Storage integration (MinIO, PostgreSQL)
✓ MLflow integration
✓ Basic Prefect flow: experiment_pipeline
✓ Simple deployment
✓ Unit tests

Deliverables:
  - Working sklearn adapters
  - First Prefect flow running
  - Baseline experiments
  - Experiment tracking functional

──────────────────────────────────────

Phase 3: Spark Integration + Advanced Flows (Weeks 5-7)
────────────────────────────────────────────────────────
✓ Spark cluster setup (Docker Compose)
✓ SparkAdapter implementation
✓ Distributed experiments
✓ Comparison flow (multiple algorithms)
✓ Scalability flow
✓ Prefect deployments
✓ Integration tests

Deliverables:
  - Working Spark DBSCAN
  - 3+ Prefect flows
  - Distributed experiments
  - Multiple deployments

──────────────────────────────────────

Phase 4: Monitoring & Prefect Dashboard Integration (Weeks 8-9)
────────────────────────────────────────────────────────────────
✓ Prometheus setup
✓ Grafana dashboards
✓ Prefect flow monitoring dashboard
✓ Custom metrics export
✓ Loki logging
✓ Jaeger tracing
✓ Alert rules

Deliverables:
  - Complete monitoring stack
  - Prefect-specific dashboards
  - Real-time monitoring
  - Historical analysis

──────────────────────────────────────

Phase 5: Evaluation Framework + Automated Prefect Pipelines (Weeks 10-11)
───────────────────────────────────────────────────────────────────────────
✓ Metrics implementation
✓ Statistical tools
✓ Automated evaluation flows
✓ Scheduled comparisons (Prefect Cron)
✓ Parameter sweep flows
✓ Result aggregation flows

Deliverables:
  - Evaluation framework
  - Automated experiment pipeline
  - Scheduled workflows
  - Statistical tools

──────────────────────────────────────

Phase 6: Comprehensive Experiments with Prefect Orchestration (Weeks 12-14)
─────────────────────────────────────────────────────────────────────────────
✓ All 8 experiments as Prefect flows
✓ Statistical analysis
✓ Visualization
✓ Prefect UI for experiment tracking
✓ Flow run history and comparison

Focus: Run all experiments through Prefect flows

Deliverables:
  - Complete experiment results
  - Statistical analysis
  - Comparison tables
  - Visualization notebooks
  - Prefect flow run history

──────────────────────────────────────

Phase 7: API & UI + Prefect Integration (Week 15)
──────────────────────────────────────────────────
✓ FastAPI implementation
✓ Prefect flow triggering via API
✓ Streamlit dashboard with Prefect monitoring
✓ CLI with Prefect commands
✓ API documentation

Deliverables:
  - Working API with Prefect integration
  - Web dashboard showing Prefect flows
  - User-friendly interface

──────────────────────────────────────

Phase 8: Documentation & Presentation (Week 16)
───────────────────────────────────────────────
✓ Complete documentation
✓ Prefect workflow documentation
✓ User guides (including Prefect)
✓ Architecture documentation
✓ README and quick start
✓ Demo preparation
✓ Presentation slides
✓ Final report

Deliverables:
  - Complete documentation
  - Prefect workflow guide
  - Demo-ready system
  - Presentation materials
  - Reproducibility package
```

---

## 16. Success Criteria (Prefect Edition)

```
Integration Checklist:
□ sklearn sequential working
□ sklearn parallel working
□ Spark distributed working
□ Uniform adapter interface
□ Correctness validated (ARI > 0.95)

Infrastructure Checklist:
□ Docker Compose deployment working
□ Prefect Server operational
□ Prefect Agent running and executing flows
□ PostgreSQL for Prefect operational
□ MinIO, main PostgreSQL, Redis working
□ Spark cluster functional
□ MLflow tracking functional

Prefect Workflow Checklist:
□ 3+ Prefect flows implemented
□ Flows can be triggered via UI
□ Flows can be triggered via API
□ Flows can be triggered via CLI
□ Deployments created and working
□ Scheduled flows running (e.g., daily comparison)
□ Flow run history visible in UI
□ Error handling and retries working

Evaluation Checklist:
□ 8 experiments complete (via Prefect flows)
□ Statistical analysis done
□ Visualizations created
□ Comparison tables generated
□ Prefect UI shows all flow runs

Quality Checklist:
□ >75% test coverage
□ Prefect tasks tested
□ Prefect flows tested
□ CI/CD passing
□ Code linted and formatted
□ Security scan clean
□ Documentation complete (including Prefect)

Documentation Checklist:
□ Prefect setup guide
□ Creating flows guide
□ Deployment guide
□ Triggering flows guide
□ Monitoring flows guide
```

---

## Conclusion

This **Prefect-based implementation** provides several advantages over Airflow for this academic project:

### Why Prefect is Better for This Project:

1. **Simplicity**: Pure Python, no DAG DSL
2. **Developer Experience**: Easier debugging, better testing
3. **Modern**: Native async/await, dynamic workflows
4. **Faster Setup**: Less configuration overhead
5. **Better for Research**: More flexible, easier experimentation
6. **Great UI**: Modern, real-time interface
7. **Pythonic**: Feels natural for Python developers

### Next Steps:

1. **Clone/create repository**
2. **Run `docker-compose up -d`**
3. **Access Prefect UI**: http://localhost:4200
4. **Register flows**: `python scripts/prefect/register_flows.py`
5. **Trigger first flow**: Via UI, API, or CLI
6. **Monitor in real-time**: Watch Prefect UI
7. **Iterate and experiment**: Build more flows

**This is the modern way to build ML pipelines! 🚀**

**Good luck with your Master's project using Prefect! 🎓✨**