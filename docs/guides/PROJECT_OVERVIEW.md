# Taxi MLOps Project Overview

## Project Description

This MLOps project compares different DBSCAN implementations (standard sequential and parallel) using scikit-learn on NYC taxi trip data. The project includes a complete evaluation framework, automated workflows, and comprehensive experiment tracking.

## Architecture

### Infrastructure Services

- **PostgreSQL**: Database for Prefect and MLflow metadata, experiment storage
- **Redis**: Caching and task queue (available for future use)
- **MinIO**: Object storage for MLflow artifacts
- **Prefect Server**: Workflow orchestration server (v3.x)
- **Prefect Agent**: Executes workflows
- **MLflow**: Experiment tracking and model registry

### Application Components

#### 1. Adapters (`src/adapters/`)
- `SklearnAdapter`: Sequential DBSCAN implementation
- `SklearnParallelAdapter`: Parallel DBSCAN with joblib
- Both implement a common `BaseAdapter` interface

#### 2. Data Pipelines (`src/pipelines/`)
- `DataLoader`: Load data from files or MinIO
- `TaxiTripPreprocessor`: Extract and process coordinates from taxi data
  - Supports actual coordinates or location IDs
  - Converts NYC location IDs to approximate coordinates
  - Filters invalid coordinates
- `DataValidator`: Validate data and parameters

#### 3. Storage (`src/storage/`)
- `MinIOClient`: Object storage operations
- `PostgresClient`: Database operations for experiment metadata

#### 4. Evaluation Framework (`src/evaluation/`)
- `PerformanceMetrics`: Runtime, memory, CPU, scalability
- `QualityMetrics`: Silhouette, Davies-Bouldin, Calinski-Harabasz scores
- `StatisticalAnalyzer`: Hypothesis testing, effect sizes, correlations
- `ExperimentEvaluator`: Combined evaluation with overall scoring

#### 5. Workflows (`src/workflows/`)
- `experiment_pipeline`: Basic experiment execution
- `evaluation_pipeline`: Comprehensive evaluation workflow
- `parameter_sweep_flow`: Systematic parameter exploration
- `compare_adapters_sweep_flow`: Compare both adapters
- `daily_adapter_comparison_flow`: Scheduled daily comparison
- `weekly_parameter_sweep_flow`: Scheduled weekly sweep
- `aggregate_results_flow`: Result aggregation and analysis

## Data Flow

1. **Data Loading**: Load parquet files or from MinIO
2. **Preprocessing**: Extract coordinates (pickup/dropoff) using `TaxiTripPreprocessor`
3. **Clustering**: Run DBSCAN with selected adapter
4. **Evaluation**: Compute performance and quality metrics
5. **Tracking**: Log to MLflow and store in PostgreSQL
6. **Analysis**: Aggregate and compare results

## Key Features

### Performance Tracking
- Execution time measurement
- Memory usage monitoring
- CPU utilization tracking
- Scalability analysis (time complexity estimation)

### Quality Assessment
- Silhouette Score (cluster separation)
- Davies-Bouldin Index (cluster compactness)
- Calinski-Harabasz Index (variance ratio)
- Cluster statistics (sizes, noise ratio)

### Statistical Analysis
- Summary statistics (mean, median, std, quartiles)
- Hypothesis testing (t-test, Mann-Whitney U)
- Effect size (Cohen's d)
- Parameter sweep analysis
- Group comparisons

### Automation
- Prefect workflows for experiment execution
- Parameter sweeps for systematic exploration
- Scheduled workflows (daily/weekly)
- Result aggregation and analysis

## Technology Stack

- **Python 3.11+**: Core language
- **Prefect 3.x**: Workflow orchestration
- **MLflow**: Experiment tracking
- **scikit-learn**: DBSCAN implementations
- **PostgreSQL**: Metadata storage
- **MinIO**: Object storage (S3-compatible)
- **Docker**: Containerization
- **pandas/numpy**: Data processing
- **scipy**: Statistical analysis

## Project Status

✅ **Phase 1 Complete**: Environment setup, core infrastructure, CI pipeline
✅ **Phase 2 Complete**: Sklearn integration, data pipelines, storage, MLflow, Prefect workflows
✅ **Phase 3 Complete**: Evaluation framework, parameter sweeps, scheduled workflows

## Next Steps

- Production deployment configurations
- Advanced monitoring and alerting
- Model versioning and registry
- Automated model retraining pipelines
- Performance optimization

