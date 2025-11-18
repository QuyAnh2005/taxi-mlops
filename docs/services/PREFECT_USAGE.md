# Prefect Usage Guide

## Accessing Prefect UI

The Prefect UI is available at: **http://localhost:4200**

**Note**: Prefect 3.x is used in this project. The server runs in Docker, and flows run directly will appear in the UI.

If you see an empty dashboard, this is normal - you need to run or deploy flows first to see them in the UI. See [QUICKSTART_PREFECT.md](../QUICKSTART_PREFECT.md) for quick setup.

## Initial Setup

1. **Configure Prefect client to connect to server:**
   ```bash
   prefect config set PREFECT_API_URL=http://localhost:4200/api
   ```

2. **Or use the setup script:**
   ```bash
   python scripts/setup_prefect.py
   ```

3. **Verify connection:**
   ```bash
   prefect config view
   curl http://localhost:4200/api/health
   ```

## Running Flows

### Option 1: Run Flows Directly (Recommended for Quick Tests)

When you run flows directly (e.g., `python scripts/run_experiment.py`), they will appear in the Prefect UI if the server is running and configured correctly. This is the easiest way to get started.

**Example:**
```bash
# Configure Prefect first
prefect config set PREFECT_API_URL=http://localhost:4200/api

# Run a flow - it will appear in the UI
python scripts/run_experiment.py \
  --file-path data/yellow_tripdata_2025-09.parquet \
  --adapter-type sklearn
```

### Option 2: Deploy Flows to Prefect Server (For Production/Scheduled Runs)

To deploy flows for repeated or scheduled execution:

1. **Deploy a flow:**
   ```bash
   prefect deploy src/workflows/experiment_pipeline.py:experiment_pipeline
   ```

2. **Or create a deployment file:**
   ```bash
   prefect deploy src/workflows/experiment_pipeline.py:experiment_pipeline \
     --name experiment-pipeline \
     --pool default-agent-pool
   ```

3. **Run a deployed flow:**
   ```bash
   prefect deployment run experiment_pipeline/experiment-pipeline
   ```

## Viewing Flows in UI

After deploying and running flows:

1. Open http://localhost:4200 in your browser
2. Navigate to **Flows** to see deployed flows
3. Navigate to **Flow Runs** to see execution history
4. Click on a flow run to see detailed logs and results

## Workflow Types

### 1. Basic Experiment Pipeline

```bash
# Deploy
prefect deploy src/workflows/experiment_pipeline.py:experiment_pipeline

# Run with parameters
prefect deployment run experiment_pipeline/experiment-pipeline \
  --param file_path="data/yellow_tripdata_2025-09.parquet" \
  --param adapter_type="sklearn" \
  --param eps=0.5 \
  --param min_samples=5
```

### 2. Evaluation Pipeline

```bash
# Deploy
prefect deploy src/workflows/evaluation_flows.py:evaluation_pipeline

# Run
prefect deployment run evaluation_pipeline/evaluation-pipeline \
  --param file_path="data/yellow_tripdata_2025-09.parquet" \
  --param adapter_type="sklearn"
```

### 3. Parameter Sweep

```bash
# Deploy
prefect deploy src/workflows/parameter_sweep.py:parameter_sweep_flow

# Run
prefect deployment run parameter_sweep/parameter-sweep \
  --param file_path="data/yellow_tripdata_2025-09.parquet" \
  --param adapter_type="sklearn"
```

### 4. Scheduled Workflows

```bash
# Deploy with schedule
prefect deploy src/workflows/scheduled_workflows.py:daily_adapter_comparison_flow \
  --cron "0 2 * * *"

prefect deploy src/workflows/scheduled_workflows.py:weekly_parameter_sweep_flow \
  --cron "0 3 * * 1"
```

## Prefect Agent

The Prefect agent is running in Docker and will automatically pick up and execute deployed flows. Check agent status:

```bash
docker-compose logs prefect-agent
```

## Troubleshooting

### Empty Dashboard

- **No flows visible**: Run a flow first (see Option 1 above) or deploy flows
- **No flow runs**: Run a flow directly or execute a deployed flow
- **Connection issues**: Verify `PREFECT_API_URL` is set correctly
- **Version mismatch**: Ensure Prefect client and server versions match (both should be 3.x)

### Check Server Status

```bash
# Check if server is running
docker-compose ps prefect-server

# Check server logs
docker-compose logs prefect-server

# Test API
curl http://localhost:4200/api/health
```

### Reset Prefect Database

If you need to start fresh:

```bash
docker-compose down
docker volume rm taxi-mlops_postgres_data
docker-compose up -d
```

## Quick Start Example

```bash
# 1. Set up Prefect connection
prefect config set PREFECT_API_URL=http://localhost:4200/api

# 2. Deploy a flow
prefect deploy src/workflows/experiment_pipeline.py:experiment_pipeline

# 3. Run the flow
prefect deployment run experiment_pipeline/experiment-pipeline \
  --param file_path="data/yellow_tripdata_2025-09.parquet"

# 4. View in UI
# Open http://localhost:4200 and navigate to Flow Runs
```

## Prefect CLI Commands

```bash
# List flows
prefect flow ls

# List deployments
prefect deployment ls

# List flow runs
prefect flow-run ls

# View flow run details
prefect flow-run inspect <run-id>

# View logs
prefect flow-run logs <run-id>
```

