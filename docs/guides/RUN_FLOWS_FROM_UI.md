# How to Run Flows from Prefect UI

This guide explains how to deploy and run Prefect flows directly from the Prefect UI.

## Prerequisites

1. **Prefect server is running:**
   ```bash
   docker-compose ps prefect-server
   # Should show "Up" status
   ```

2. **Prefect is configured:**
   ```bash
   prefect config set PREFECT_API_URL=http://localhost:4200/api
   # Or use: python scripts/setup_prefect.py
   ```

3. **Work pool exists:**
   ```bash
   prefect work-pool create default-agent-pool --type process
   ```

## Quick Setup (Automated)

Run the deployment script to deploy all flows at once:

```bash
python scripts/deploy_flows_for_ui.py
```

This will deploy all available flows so you can run them from the UI.

## Manual Deployment

### Step 1: Deploy a Flow

Deploy the experiment pipeline:

```bash
prefect deploy src/workflows/experiment_pipeline.py:experiment_pipeline \
  --name experiment-pipeline \
  --pool default-agent-pool
```

Deploy other flows:

```bash
# Evaluation pipeline
prefect deploy src/workflows/evaluation_flows.py:evaluation_pipeline \
  --name evaluation-pipeline \
  --pool default-agent-pool

# Parameter sweep
prefect deploy src/workflows/parameter_sweep.py:parameter_sweep_flow \
  --name parameter-sweep \
  --pool default-agent-pool

# Compare adapters
prefect deploy src/workflows/parameter_sweep.py:compare_adapters_sweep_flow \
  --name compare-adapters-sweep \
  --pool default-agent-pool
```

### Step 2: Access Prefect UI

1. Open **http://localhost:4200** in your browser
2. Navigate to **"Deployments"** in the left sidebar
3. You should see your deployed flows listed

### Step 3: Run a Flow from UI

1. **Click on a deployment** (e.g., "experiment-pipeline")
2. **Click the "Run" button** (usually in the top-right)
3. **Fill in the parameters:**
   
   **Required Parameters:**
   - `data_source`: 
     - For local file: `"data/yellow_tripdata_2025-09.parquet"`
     - For MinIO: `"yellow_tripdata_2025-09.parquet"`
   - `adapter_type`: `"sklearn"` or `"sklearn_parallel"`
   
   **Optional Parameters:**
   - `eps`: `0.01` (DBSCAN neighborhood radius)
   - `min_samples`: `5` (minimum samples in a cluster)
   - `coordinate_type`: `"pickup"` or `"dropoff"` (default: `"pickup"`)
   - `use_minio`: `true` or `false` (default: `true`)
   - `max_samples`: `5000` (limit for testing, `null` for all data)
   - `use_location_ids`: `true` (default: `true`)

4. **Click "Run"** to start the flow execution

### Step 4: Monitor Flow Execution

1. Navigate to **"Flow Runs"** in the sidebar
2. Click on your flow run to see:
   - **Timeline**: Visual representation of task execution
   - **Logs**: Detailed logs from each task
   - **Parameters**: Input parameters used
   - **State**: Current status (Running, Completed, Failed)
   - **Result**: Output data (if available)

## Available Flows

### 1. experiment-pipeline
**Description**: Basic DBSCAN experiment with MLflow logging

**Parameters:**
- `data_source` (required): Path to data file
- `adapter_type` (required): "sklearn" or "sklearn_parallel"
- `eps`: 0.01 (recommended for taxi data)
- `min_samples`: 5
- `coordinate_type`: "pickup" or "dropoff"
- `use_minio`: true/false
- `max_samples`: Optional limit

**Example Parameters:**
```json
{
  "data_source": "data/yellow_tripdata_2025-09.parquet",
  "adapter_type": "sklearn",
  "eps": 0.01,
  "min_samples": 5,
  "coordinate_type": "pickup",
  "use_minio": false,
  "max_samples": 5000
}
```

### 2. evaluation-pipeline
**Description**: Comprehensive evaluation with quality metrics

**Parameters:** Same as experiment-pipeline

### 3. parameter-sweep
**Description**: Run multiple experiments with different parameters

**Parameters:**
- `data_source` (required)
- `adapter_type` (required)
- `eps_values`: Array of eps values to test
- `min_samples_values`: Array of min_samples values to test

### 4. compare-adapters-sweep
**Description**: Compare both adapters with parameter sweep

**Parameters:** Same as parameter-sweep

## Running from Command Line (Alternative)

You can also trigger deployed flows from the command line:

```bash
prefect deployment run experiment_pipeline/experiment-pipeline \
  --param data_source="data/yellow_tripdata_2025-09.parquet" \
  --param adapter_type="sklearn" \
  --param eps=0.01 \
  --param min_samples=5 \
  --param coordinate_type="pickup" \
  --param use_minio=false
```

## Troubleshooting

### No Deployments Visible

1. **Check if flows are deployed:**
   ```bash
   prefect deployment ls
   ```

2. **Verify work pool exists:**
   ```bash
   prefect work-pool ls
   ```

3. **Check Prefect server is running:**
   ```bash
   docker-compose ps prefect-server
   curl http://localhost:4200/api/health
   ```

### Flow Not Starting

1. **Check worker is running:**
   ```bash
   docker-compose ps prefect-worker
   docker-compose logs prefect-worker
   ```

2. **Verify work pool has workers:**
   ```bash
   prefect work-pool inspect default-agent-pool
   ```

3. **Check flow run logs in UI:**
   - Go to Flow Runs
   - Click on the failed run
   - Check the logs tab for errors

### Parameter Errors

- **Type errors**: Make sure numbers are numbers (not strings)
- **Missing required params**: Check the flow definition for required parameters
- **Invalid values**: 
  - `coordinate_type` must be "pickup" or "dropoff"
  - `adapter_type` must be "sklearn" or "sklearn_parallel"
  - `eps` must be > 0
  - `min_samples` must be >= 2

## Tips

1. **Start with small datasets**: Use `max_samples: 1000` for quick testing
2. **Check logs**: Always check the logs tab if a flow fails
3. **Use local files first**: Set `use_minio: false` to test with local files
4. **Monitor resources**: Large experiments may take time and memory
5. **View results**: Check MLflow UI (http://localhost:5000) for experiment results

## Next Steps

After running flows:
- **View results in MLflow**: http://localhost:5000
- **Check metrics in Grafana**: http://localhost:3000
- **View logs in Prefect UI**: Flow Runs → Select Run → Logs
- **Access UI**: http://localhost:8501 (Streamlit UI)

