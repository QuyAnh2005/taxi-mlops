# Quick Start: Using Prefect UI

## Overview

This guide helps you get started with Prefect UI for the Taxi MLOps project. Prefect 3.x is used for workflow orchestration.

## Problem: Empty Prefect UI

If you see an empty dashboard at http://localhost:4200, it's because no flows have been run yet. Here's how to fix it:

## Solution 1: Run a Flow Directly (Easiest)

1. **Make sure Prefect is configured:**
   ```bash
   prefect config set PREFECT_API_URL=http://localhost:4200/api
   ```

2. **Run a flow:**
   ```bash
   python scripts/quick_start_prefect.py
   ```
   
   Or run any experiment script:
   ```bash
   python scripts/run_experiment.py \
     --file-path data/yellow_tripdata_2025-09.parquet \
     --adapter-type sklearn \
     --eps 0.5 \
     --min-samples 5 \
     --max-samples 1000
   ```

3. **Refresh the Prefect UI** at http://localhost:4200
   - Navigate to **"Flow Runs"** in the sidebar
   - You should see your flow execution

## Solution 2: Deploy a Flow (For Scheduled/Repeated Runs)

1. **Create a work pool (if needed):**
   ```bash
   prefect work-pool create default-agent-pool --type process
   ```

2. **Deploy the flow:**
   ```bash
   prefect deploy src/workflows/experiment_pipeline.py:experiment_pipeline \
     --name experiment-pipeline \
     --pool default-agent-pool
   ```

3. **Run the deployed flow:**
   ```bash
   prefect deployment run experiment_pipeline/experiment-pipeline \
     --param file_path="data/yellow_tripdata_2025-09.parquet" \
     --param adapter_type="sklearn" \
     --param eps=0.5 \
     --param min_samples=5 \
     --param max_samples=1000
   ```

## Solution 3: Run Evaluation Pipeline

```bash
# The evaluation pipeline includes comprehensive metrics
python -c "
from src.workflows.evaluation_flows import evaluation_pipeline
result = evaluation_pipeline(
    file_path='data/yellow_tripdata_2025-09.parquet',
    adapter_type='sklearn',
    eps=0.5,
    min_samples=5,
    max_samples=1000
)
print(f'Overall Score: {result[\"overall_score\"]:.4f}')
"
```

## What You'll See in the UI

After running a flow:

1. **Flow Runs Page**: Shows all flow executions
   - Status (Running, Completed, Failed)
   - Execution time
   - Parameters used

2. **Flow Run Details**: Click on a run to see:
   - Task execution timeline
   - Logs from each task
   - Results and metrics
   - Error details (if any)

3. **Flows Page**: Shows registered flows (after deployment)

## Troubleshooting

### Still seeing empty UI?

1. **Check Prefect server is running:**
   ```bash
   docker-compose ps prefect-server
   ```

2. **Verify connection:**
   ```bash
   prefect config view
   curl http://localhost:4200/api/health
   ```

3. **Check if flows are running:**
   ```bash
   prefect flow-run ls
   ```

### Connection Issues

If you get connection errors:
```bash
# Reset Prefect config
prefect config set PREFECT_API_URL=http://localhost:4200/api

# Verify
prefect config view
```

## Available Workflows

The project includes several Prefect workflows:

1. **experiment_pipeline**: Basic experiment execution
2. **evaluation_pipeline**: Comprehensive evaluation with performance and quality metrics
3. **parameter_sweep_flow**: Systematic parameter exploration
4. **compare_adapters_sweep_flow**: Compare both adapters with parameter sweep
5. **daily_adapter_comparison_flow**: Scheduled daily comparison (deploy with cron)
6. **weekly_parameter_sweep_flow**: Scheduled weekly parameter sweep (deploy with cron)
7. **aggregate_results_flow**: Aggregate and analyze experiment results

## Next Steps

- See [docs/PREFECT_USAGE.md](docs/PREFECT_USAGE.md) for advanced usage
- See [docs/EVALUATION.md](docs/EVALUATION.md) for evaluation framework details
- Deploy scheduled workflows for automated runs
- Use parameter sweeps for systematic experiments
- Explore evaluation metrics in MLflow UI

