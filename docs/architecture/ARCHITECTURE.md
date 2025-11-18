# System Architecture

## Overview

The Taxi MLOps platform is a comprehensive system for comparing DBSCAN clustering implementations, featuring automated workflows, experiment tracking, monitoring, and observability.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
├─────────────────────────────────────────────────────────────┤
│  Prefect UI  │  MLflow UI  │  Grafana  │  Prometheus  │ ... │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                  Orchestration Layer                        │
├─────────────────────────────────────────────────────────────┤
│                    Prefect Server                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Flows      │  │   Tasks      │  │   Schedules  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                    Prefect Agent                            │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                  Application Layer                          │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Adapters    │  │ Evaluation   │  │ Monitoring   │     │
│  │  - Sklearn   │  │  - Metrics   │  │  - Metrics   │     │
│  │  - Parallel  │  │  - Analysis  │  │  - Tracing   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐                       │
│  │  Pipelines   │  │  Storage     │                       │
│  │  - Loader    │  │  - MinIO     │                       │
│  │  - Preproc   │  │  - Postgres  │                       │
│  └──────────────┘  └──────────────┘                       │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                  Infrastructure Layer                        │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL  │  Redis  │  MinIO  │  Monitoring Stack      │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Orchestration Layer

**Prefect Server**
- Manages flow definitions and execution
- Stores flow run history
- Provides REST API and UI
- Database: PostgreSQL

**Prefect Agent**
- Executes flows on demand
- Polls for scheduled runs
- Manages task execution
- Reports status to server

### 2. Application Components

#### Adapters
- **SklearnAdapter**: Sequential DBSCAN using scikit-learn
- **SklearnParallelAdapter**: Parallel DBSCAN using joblib

#### Data Pipeline
- **DataLoader**: Loads data from MinIO or local files
- **TaxiTripPreprocessor**: Extracts coordinates and cleans data
- **DataValidator**: Validates data quality

#### Evaluation
- **PerformanceMetrics**: Runtime, memory, CPU tracking
- **QualityMetrics**: Clustering quality scores
- **StatisticalAnalyzer**: Statistical analysis and comparisons

#### Monitoring
- **MetricsCollector**: Prometheus metrics collection
- **Tracing**: OpenTelemetry/Jaeger integration

### 3. Storage Layer

**PostgreSQL**
- Prefect metadata
- MLflow tracking data
- Experiment metadata

**MinIO (S3-compatible)**
- Dataset storage (`taxi-data` bucket)
- MLflow artifacts (`mlflow-artifacts` bucket)

**Redis**
- Caching and message queuing (for Prefect)

### 4. Monitoring Stack

**Prometheus**
- Metrics collection and storage
- Alert rule evaluation
- Query interface

**Grafana**
- Metrics visualization
- Dashboard management
- Alert visualization

**Loki**
- Log aggregation
- Log querying interface

**Jaeger**
- Distributed tracing
- Performance analysis

**Pushgateway**
- Metrics push endpoint
- Ephemeral metrics storage

**Alertmanager**
- Alert routing and notification
- Alert grouping and inhibition

## Data Flow

### Experiment Execution Flow

```
1. User triggers experiment
   ↓
2. Prefect Flow starts
   ↓
3. Load data from MinIO
   ↓
4. Preprocess data (extract coordinates)
   ↓
5. Run DBSCAN (via adapter)
   ↓
6. Collect metrics
   ↓
7. Evaluate results
   ↓
8. Log to MLflow
   ↓
9. Save to PostgreSQL
   ↓
10. Push metrics to Pushgateway
    ↓
11. Prometheus scrapes Pushgateway
    ↓
12. Grafana visualizes metrics
```

### Metrics Collection Flow

```
Workflow Execution
   ↓
MetricsCollector (context manager)
   ↓
Prometheus Client (in-memory)
   ↓
Push to Pushgateway
   ↓
Prometheus Scrapes
   ↓
Grafana Queries Prometheus
   ↓
Dashboard Visualization
```

## Technology Stack

### Core Technologies
- **Python 3.11**: Application runtime
- **Prefect 3.x**: Workflow orchestration
- **MLflow 2.8+**: Experiment tracking
- **scikit-learn**: DBSCAN implementations
- **Pandas/NumPy**: Data processing

### Infrastructure
- **Docker & Docker Compose**: Containerization
- **PostgreSQL 15**: Relational database
- **Redis 7**: Caching and queuing
- **MinIO**: Object storage

### Monitoring
- **Prometheus**: Metrics collection
- **Grafana**: Visualization
- **Loki**: Log aggregation
- **Jaeger**: Distributed tracing
- **Alertmanager**: Alert management

## Deployment Architecture

### Development Environment
- All services run in Docker Compose
- Single-node deployment
- Local data storage
- Development-friendly defaults

### Production Considerations
- Horizontal scaling for Prefect agents
- Separate PostgreSQL instances for Prefect/MLflow
- S3-compatible storage (MinIO or AWS S3)
- High-availability monitoring stack
- Load balancing for UI services

## Security Considerations

### Current Implementation
- Default credentials (development only)
- No authentication on internal services
- Network isolation via Docker networks

### Production Recommendations
- Implement authentication/authorization
- Use secrets management (Vault, AWS Secrets Manager)
- Enable TLS for all services
- Network policies and firewalls
- Regular security updates

## Scalability

### Horizontal Scaling
- **Prefect Agents**: Add more agent instances
- **Workflows**: Parallel execution via Prefect
- **Data Processing**: Distributed processing with Dask/Ray

### Vertical Scaling
- Increase resources for PostgreSQL
- Scale MinIO storage
- Increase Prometheus retention

## Performance Optimization

### Current Optimizations
- Parallel DBSCAN implementation
- Efficient data loading from MinIO
- Caching in Redis
- Batch metrics pushing

### Future Optimizations
- Distributed data processing
- Model caching
- Query optimization
- Metrics sampling

## Monitoring & Observability

### Metrics
- Application metrics (experiments, flows)
- System metrics (CPU, memory, disk)
- Infrastructure metrics (database, storage)

### Logging
- Centralized logging via Loki
- Structured logging format
- Log aggregation and search

### Tracing
- Distributed tracing with Jaeger
- Workflow execution traces
- Performance bottleneck identification

## Disaster Recovery

### Backup Strategy
- PostgreSQL database backups
- MinIO data replication
- Prometheus metrics export
- Configuration version control

### Recovery Procedures
- Database restore from backups
- Data restoration from MinIO
- Service restart procedures
- Configuration rollback

## Future Enhancements

- **Model Serving**: Deploy trained models
- **A/B Testing**: Compare model versions
- **AutoML**: Automated hyperparameter tuning
- **Feature Store**: Centralized feature management
- **Data Versioning**: Track dataset versions
- **Model Registry**: Model lifecycle management

