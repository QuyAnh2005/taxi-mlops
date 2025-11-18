# Prefect UI Quick Reference

## 🚀 Quick Start: Run Flows from UI

### 1. Deploy Flows (One-time setup)

```bash
# Automated - deploys all flows
python scripts/deploy_flows_for_ui.py

# OR manually deploy one flow
prefect deploy src/workflows/experiment_pipeline.py:experiment_pipeline \
  --name experiment-pipeline \
  --pool default-agent-pool
```

### 2. Access Prefect UI

Open: **http://localhost:4200**

### 3. Run a Flow

1. Go to **"Deployments"** → Click on a deployment
2. Click **"Run"** button
3. Fill parameters (see below)
4. Click **"Run"**

### 4. Monitor Execution

Go to **"Flow Runs"** → Click on your run → View logs and timeline

---

## 📋 Parameter Reference

### experiment-pipeline

**Required:**
```json
{
  "data_source": "data/yellow_tripdata_2025-09.parquet",
  "adapter_type": "sklearn"
}
```

**Recommended:**
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

**For MinIO:**
```json
{
  "data_source": "yellow_tripdata_2025-09.parquet",
  "adapter_type": "sklearn",
  "eps": 0.01,
  "min_samples": 5,
  "coordinate_type": "pickup",
  "use_minio": true
}
```

---

## 🔍 Common Tasks

### List Deployments
```bash
prefect deployment ls
```

### List Flow Runs
```bash
prefect flow-run ls
```

### View Flow Run Details
```bash
prefect flow-run inspect <run-id>
```

### View Logs
```bash
prefect flow-run logs <run-id>
```

### Run from CLI
```bash
prefect deployment run experiment_pipeline/experiment-pipeline \
  --param data_source="data/yellow_tripdata_2025-09.parquet" \
  --param adapter_type="sklearn" \
  --param eps=0.01 \
  --param min_samples=5
```

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| No deployments visible | Run `python scripts/deploy_flows_for_ui.py` |
| Flow not starting | Check `docker-compose ps prefect-worker` |
| Parameter errors | Check parameter types (numbers vs strings) |
| Connection issues | Run `prefect config set PREFECT_API_URL=http://localhost:4200/api` |

---

## 📊 View Results

- **Prefect UI**: http://localhost:4200 (Flow Runs)
- **MLflow UI**: http://localhost:5000 (Experiments)
- **Streamlit UI**: http://localhost:8501 (Visualization)

