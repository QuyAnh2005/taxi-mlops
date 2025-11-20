# Taxi MLOps: DBSCAN Clustering Comparison Platform

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Prefect](https://img.shields.io/badge/prefect-3.x-orange.svg)](https://www.prefect.io/)
[![MLflow](https://img.shields.io/badge/mlflow-2.8+-green.svg)](https://mlflow.org/)

A comprehensive MLOps platform for comparing sequential and parallel DBSCAN implementations on NYC taxi trip data, featuring automated workflows, experiment tracking, monitoring, and observability.

[demo.webm](https://github.com/user-attachments/assets/3af0fe37-604f-469e-8045-e230c6e35e3b)




## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- `uv` package manager (recommended) or `pip`
- `make` utility

### One-Command Installation

```bash
# Complete setup: downloads data, starts services, configures everything
make install-all
```

That's it! This single command will:
- Download NYC taxi trip data and zones shapefile
- Start all Docker services (PostgreSQL, Redis, MinIO, Prefect, MLflow, monitoring stack)
- Wait for services to be healthy
- Install Python dependencies (using uv or pip)
- Set up MinIO buckets and upload data
- Configure Prefect and deploy flows
- Verify all services are working

### Step-by-Step Installation (Alternative)

If you prefer to run steps individually:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/QuyAnh2005/taxi-mlops.git
   cd taxi-mlops
   ```

2. **Download data**:
   ```bash
   make download-data
   ```

3. **Set up services**:
   ```bash
   make setup-services
   ```

4. **Verify installation**:
   ```bash
   make verify
   ```

### View All Available Commands

```bash
make help
```

## 📊 Services & Access

| Service | URL | Credentials |
|---------|-----|-------------|
| **Prefect UI** | http://localhost:4200 | - |
| **MLflow UI** | http://localhost:5000 | - |
| **Grafana** | http://localhost:3000 | admin/admin |
| **Prometheus** | http://localhost:9090 | - |
| **Jaeger UI** | http://localhost:16686 | - |
| **MinIO Console** | http://localhost:9001 | minioadmin/minioadmin |
| **Alertmanager** | http://localhost:9093 | - |

## 🏗️ Architecture

The platform consists of:

- **Workflow Orchestration**: Prefect 3.x for managing experiment pipelines
- **Experiment Tracking**: MLflow for metrics, parameters, and artifacts
- **Data Storage**: MinIO (S3-compatible) for datasets and artifacts
- **Metadata Storage**: PostgreSQL for experiment metadata
- **Monitoring**: Prometheus + Grafana for metrics visualization
- **Logging**: Loki for centralized log aggregation
- **Tracing**: Jaeger for distributed tracing
- **Alerts**: Alertmanager for notification management

See [docs/architecture/ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md) for detailed architecture documentation.

## 📚 Documentation

### Getting Started
- [Quick Start Guide](docs/guides/QUICKSTART.md) - Get up and running in minutes
- [Prefect Quick Start](docs/guides/QUICKSTART_PREFECT.md) - Prefect UI setup
- [Monitoring Quick Start](docs/guides/QUICKSTART_MONITORING.md) - Monitoring stack setup

### User Guides
- [Prefect Workflows](docs/workflows/PREFECT_WORKFLOWS.md) - Complete Prefect workflow guide
- [MinIO Usage](docs/services/MINIO_USAGE.md) - Data storage and management
- [Monitoring Guide](docs/services/MONITORING.md) - Observability and metrics
- [Evaluation Framework](docs/guides/EVALUATION.md) - Experiment evaluation

### Architecture & Design
- [System Architecture](docs/architecture/ARCHITECTURE.md) - High-level system design
- [Project Overview](docs/guides/PROJECT_OVERVIEW.md) - Project structure and components
- [Deployment Guide](docs/guides/DEPLOYMENT.md) - Production deployment

### Services Documentation
- [Prefect Usage](docs/services/PREFECT_USAGE.md) - Prefect configuration and usage
- [MLflow Integration](docs/services/MLFLOW_USAGE.md) - Experiment tracking
- [Monitoring Stack](docs/services/MONITORING.md) - Prometheus, Grafana, Loki, Jaeger
- [Configuration Guide](docs/services/CONFIGURATION.md) - System configuration

### Demo & Presentation
- [Demo Guide](docs/demo/DEMO_GUIDE.md) - Demo preparation and execution
- [Presentation Materials](docs/demo/PRESENTATION.md) - Slides and talking points

### Reference
- [Changelog](docs/guides/CHANGELOG.md) - Project history and changes
- [Troubleshooting](docs/guides/TROUBLESHOOTING.md) - Common issues and solutions
- [Project Report](docs/guides/PROJECT_REPORT.md) - Final project report

**Complete documentation index**: [docs/README.md](docs/README.md)

## 🎯 Key Features

### Experiment Management
- **Sequential DBSCAN**: Standard scikit-learn implementation
- **Parallel DBSCAN**: Multi-threaded implementation using joblib
- **Parameter Sweeps**: Automated hyperparameter exploration
- **Adapter Comparison**: Side-by-side performance analysis

### Data Pipeline
- **MinIO Integration**: Centralized data storage
- **Data Validation**: Automatic data quality checks
- **Preprocessing**: Coordinate extraction and cleaning
- **Flexible Loading**: MinIO-first with local fallback

### Evaluation & Metrics
- **Performance Metrics**: Runtime, memory, CPU usage
- **Quality Metrics**: Silhouette score, Davies-Bouldin, Calinski-Harabasz
- **Statistical Analysis**: Hypothesis testing, effect size
- **Automated Reports**: Aggregated experiment summaries

### Monitoring & Observability
- **Real-time Metrics**: Prometheus + Grafana dashboards
- **Distributed Tracing**: Jaeger for workflow analysis
- **Log Aggregation**: Loki for centralized logging
- **Alerting**: Automated alerts for failures and anomalies

### Workflow Orchestration
- **Prefect Flows**: Declarative workflow definitions
- **Scheduled Runs**: Automated daily/weekly comparisons
- **Task Management**: Parallel execution and retries
- **Flow Monitoring**: Real-time execution tracking

## 📖 Usage Examples

### Start the Web UI
```bash
make run-ui
# Access at http://localhost:8501
```

### Run Sample Experiment
```bash
make run-experiment
```

### Run Custom Experiments

For custom experiments with specific parameters:

```bash
# Single experiment
export PUSHGATEWAY_URL=http://localhost:9091
.venv/bin/python scripts/run_experiment.py \
  --data-object yellow_tripdata_2025-09.parquet \
  --adapter-type sklearn \
  --eps 0.5 \
  --min-samples 5
```

```bash
# Compare adapters
.venv/bin/python scripts/compare_adapters.py \
  --data-object yellow_tripdata_2025-09.parquet \
  --eps 0.5 \
  --min-samples 5
```

```bash
# Parameter sweep
.venv/bin/python scripts/run_parameter_sweep.py \
  --data-object yellow_tripdata_2025-09.parquet \
  --adapter-type sklearn \
  --eps-values 0.3 0.5 0.7 1.0 \
  --min-samples-values 5 10 15
```

### Service Management

```bash
# Check service status
make status

# View logs
make logs

# Restart services
make restart

# Stop services
make down
```

### View Metrics

Access monitoring dashboards:
- **Prometheus**: http://localhost:9090 (query: `experiments_total`)
- **Grafana**: http://localhost:3000 (Explore → Prometheus)
- **Jaeger**: http://localhost:16686 (distributed tracing)

## 🛠️ Development

### Project Structure
```
taxi-mlops/
├── src/
│   ├── adapters/          # DBSCAN implementations
│   ├── evaluation/        # Metrics and analysis
│   ├── monitoring/        # Prometheus metrics & tracing
│   ├── pipelines/         # Data loading & preprocessing
│   ├── storage/           # MinIO & PostgreSQL clients
│   └── workflows/         # Prefect flows
├── ui/                    # Streamlit web UI
│   ├── app.py            # Main UI application
│   └── components/       # UI components
├── scripts/               # Utility scripts
├── docker/                # Docker configurations
├── docs/                  # Documentation
└── tests/                 # Test suite
```

### Development Commands

All development tasks use `make` for consistency:

```bash
# Run tests
make test

# Format code
make format

# Lint code (check only)
make lint

# Verify all services
make verify
```

### Manual Commands (if needed)

```bash
# Run tests directly
pytest tests/ -v

# Code formatting
black src/ tests/ scripts/
ruff check --fix src/ tests/ scripts/

# Type checking
mypy src/
```

## 🔧 Configuration

Configuration is managed via `src/config.py` using Pydantic Settings with automatic environment variable loading.

### How Configuration Works

The application uses a two-tier configuration system:

1. **Default values** in `src/config.py` - optimized for local development
2. **Environment variables** from `.env` file - override defaults when present

All configuration fields support environment variable overrides (case-insensitive):
- `PREFECT_API_URL` → overrides `prefect_api_url`
- `POSTGRES_USER` → overrides `postgres_user`
- etc.

### Environment Variables

A `.env.example` file is provided with all available configuration options:

```bash
# For local development: defaults work out-of-the-box (no .env needed)
# For production or custom setups: create .env file to override defaults
cp .env.example .env
# Edit .env with your custom values
```

### Key Configuration Sections

- **Prefect**: Workflow orchestration (API URL, database connection)
- **MLflow**: Experiment tracking (tracking URI, S3 endpoint)
- **MinIO**: Object storage (endpoint, credentials, bucket names)
- **PostgreSQL**: Metadata storage (connection details)
- **Redis**: Caching service (host, port)
- **Monitoring**: Metrics collection (Pushgateway URL)

### Configuration Priority

Values are resolved in this order (highest to lowest priority):
1. Environment variables (from `.env` file or system)
2. Default values in `src/config.py`

See [docs/services/CONFIGURATION.md](docs/services/CONFIGURATION.md) for detailed configuration options.

## 📈 Monitoring

### View Metrics
1. **Grafana**: http://localhost:3000
   - Pre-configured dashboards for experiments and flows
   - Custom queries in Explore mode

2. **Prometheus**: http://localhost:9090
   - Query metrics directly
   - View targets and alerts

3. **Jaeger**: http://localhost:16686
   - Trace workflow execution
   - Analyze performance bottlenecks

### Key Metrics
- `experiments_total`: Total experiments by adapter and status
- `experiment_duration_seconds`: Experiment execution time
- `prefect_flow_runs_total`: Flow runs by name and status
- `prefect_flow_run_duration_seconds`: Flow execution time

## 🚨 Troubleshooting

Common issues and solutions:

1. **No metrics in Grafana**: Set `PUSHGATEWAY_URL` and run experiments
2. **Grafana not starting**: Check datasource configuration
3. **Prefect flows not appearing**: Verify Prefect server is running
4. **MLflow connection errors**: Check PostgreSQL and MinIO health

See [docs/guides/TROUBLESHOOTING.md](docs/guides/TROUBLESHOOTING.md) for detailed troubleshooting.
