# Demo Guide

## Pre-Demo Checklist

### 1. Services Running
```bash
# Check all services
docker-compose ps

# Should show all services as "Up (healthy)"
```

### 2. Data Uploaded
```bash
# Verify data in MinIO
python -c "
from src.storage import MinIOClient
client = MinIOClient(bucket_name='taxi-data')
objects = client.list_objects()
print('Data objects:', objects)
"
```

### 3. Prefect Configured
```bash
# Verify Prefect connection
prefect config view
prefect server start  # If not running
```

### 4. Generate Sample Metrics
```bash
export PUSHGATEWAY_URL=http://localhost:9091
python scripts/generate_metrics_for_grafana.py
```

## Demo Flow

### Part 1: System Overview (5 minutes)

1. **Show Architecture**
   - Explain components
   - Show service relationships
   - Highlight key features

2. **Show Services**
   - Prefect UI: http://localhost:4200
   - MLflow UI: http://localhost:5000
   - Grafana: http://localhost:3000
   - Prometheus: http://localhost:9090

### Part 2: Data Pipeline (5 minutes)

1. **Show MinIO Console**
   - http://localhost:9001
   - Show data buckets
   - Demonstrate data upload

2. **Show Data Loading**
   ```bash
   python -c "
   from src.pipelines import DataLoader
   df = DataLoader.load_data('yellow_tripdata_2025-09.parquet')
   print(f'Loaded {len(df)} rows')
   "
   ```

### Part 3: Experiment Execution (10 minutes)

1. **Run Sequential DBSCAN**
   ```bash
   export PUSHGATEWAY_URL=http://localhost:9091
   python scripts/run_experiment.py \
     --data-object yellow_tripdata_2025-09.parquet \
     --adapter-type sklearn \
     --eps 0.5 \
     --min-samples 5 \
     --max-samples 5000
   ```

2. **Show Prefect UI**
   - Navigate to flow runs
   - Show execution timeline
   - View task logs

3. **Run Parallel DBSCAN**
   ```bash
   python scripts/run_experiment.py \
     --data-object yellow_tripdata_2025-09.parquet \
     --adapter-type sklearn_parallel \
     --eps 0.5 \
     --min-samples 5 \
     --n-jobs -1 \
     --max-samples 5000
   ```

4. **Compare Results**
   - Show MLflow comparison
   - Highlight performance differences
   - Discuss use cases

### Part 4: Evaluation & Metrics (5 minutes)

1. **Show MLflow UI**
   - Experiment runs
   - Metrics comparison
   - Parameter tracking

2. **Show Evaluation Metrics**
   ```bash
   python -c "
   from src.workflows.evaluation_flows import evaluation_pipeline
   result = evaluation_pipeline(
       data_source='yellow_tripdata_2025-09.parquet',
       adapter_type='sklearn',
       eps=0.5,
       min_samples=5,
       max_samples=1000
   )
   print('Overall Score:', result['overall_score'])
   print('Quality:', result['quality'])
   "
   ```

### Part 5: Monitoring & Observability (5 minutes)

1. **Show Grafana Dashboards**
   - Experiment Monitoring
   - Prefect Flow Monitoring
   - Custom queries

2. **Show Prometheus**
   - Query metrics
   - Show targets
   - Demonstrate alerting

3. **Show Jaeger**
   - Trace workflow execution
   - Analyze performance

### Part 6: Advanced Features (5 minutes)

1. **Parameter Sweep**
   ```bash
   python scripts/run_parameter_sweep.py \
     --data-object yellow_tripdata_2025-09.parquet \
     --adapter-type sklearn \
     --eps-values 0.3 0.5 0.7 1.0 \
     --min-samples-values 5 10 15
   ```

2. **Show Results**
   - Best parameters
   - Statistical analysis
   - Performance trends

## Demo Script

### Introduction (1 minute)
"Today I'll demonstrate our MLOps platform for comparing DBSCAN implementations. The system includes workflow orchestration, experiment tracking, monitoring, and automated evaluation."

### Architecture Overview (2 minutes)
"Let me show you the system architecture. We have:
- Prefect for workflow orchestration
- MLflow for experiment tracking
- MinIO for data storage
- A comprehensive monitoring stack"

### Live Demo (15 minutes)
1. Run experiment (show Prefect UI)
2. Show results in MLflow
3. Demonstrate monitoring dashboards
4. Run parameter sweep
5. Show comparison results

### Key Features (2 minutes)
- Automated workflows
- Comprehensive evaluation
- Real-time monitoring
- Scalable architecture

## Troubleshooting During Demo

### If Services Fail
- Have backup screenshots ready
- Explain what should happen
- Show configuration files

### If Experiments Are Slow
- Use smaller datasets (`--max-samples 1000`)
- Pre-run experiments before demo
- Show cached results

### If Metrics Don't Appear
- Pre-generate metrics
- Show Prometheus directly
- Explain the process

## Post-Demo

### Questions to Expect
1. **Scalability**: "How does it scale?"
   - Explain horizontal scaling
   - Show agent configuration
   - Discuss distributed processing

2. **Production Readiness**: "Is it production-ready?"
   - Discuss security considerations
   - Explain deployment options
   - Show monitoring capabilities

3. **Cost**: "What are the costs?"
   - Open-source stack
   - Self-hosted option
   - Cloud alternatives

## Backup Materials

### Screenshots
- Prefect UI with flows
- MLflow experiment comparison
- Grafana dashboards
- Prometheus queries

### Pre-recorded Videos
- Full workflow execution
- Dashboard walkthrough
- Parameter sweep results

### Documentation
- Architecture diagrams
- Workflow diagrams
- System overview

## Success Criteria

Demo is successful if:
- ✅ All services are accessible
- ✅ At least one experiment runs successfully
- ✅ Metrics appear in Grafana
- ✅ Results are visible in MLflow
- ✅ Questions can be answered

