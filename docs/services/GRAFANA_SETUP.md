# Grafana Dashboard Setup Guide

## Issue: No Metrics Visible

If you don't see metrics in Grafana dashboards, follow these steps:

## Step 1: Verify Services Are Running

```bash
docker-compose ps | grep -E "(prometheus|grafana|pushgateway|app-metrics)"
```

All services should show "Up (healthy)".

## Step 2: Generate Metrics

Metrics are only visible after running experiments:

```bash
# Run an experiment to generate metrics
export PUSHGATEWAY_URL=http://localhost:9091
python scripts/run_experiment.py \
  --data-object yellow_tripdata_2025-09.parquet \
  --max-samples 1000
```

## Step 3: Verify Metrics in Prometheus

1. Open http://localhost:9090
2. Go to "Graph" tab
3. Try queries:
   ```promql
   experiments_total
   prefect_flow_runs_total
   rate(experiments_total[5m])
   ```

If you see results, metrics are being collected.

## Step 4: Check Grafana Data Source

1. Open Grafana: http://localhost:3000
2. Login: admin/admin
3. Go to Configuration → Data Sources
4. Verify "Prometheus" data source:
   - URL: http://prometheus:9090
   - Status: Green (working)

## Step 5: Import/View Dashboards

### Option A: Use Pre-configured Dashboards

1. Go to Dashboards → Browse
2. You should see:
   - "Prefect Flow Monitoring"
   - "Experiment Monitoring"

### Option B: Create New Dashboard

1. Click "+" → "Create Dashboard"
2. Add panel → "Add visualization"
3. Select "Prometheus" data source
4. Enter query: `experiments_total`
5. Click "Run query"

## Step 6: Check Time Range

**Important**: Make sure the time range includes when you ran experiments:

1. Click time picker (top right)
2. Select "Last 6 hours" or "Last 1 hour"
3. Or set custom range to include experiment time

## Step 7: Verify Metrics Are Pushed

Check Pushgateway:

```bash
curl http://localhost:9091/metrics | grep experiments_total
```

## Common Issues

### No Data in Prometheus

1. **Check targets**: http://localhost:9090/targets
   - `taxi-mlops-app` should be "up"
   - `pushgateway` should be "up"

2. **Check metrics endpoint**:
   ```bash
   curl http://localhost:8000/metrics
   curl http://localhost:9091/metrics
   ```

3. **Run an experiment** to generate metrics:
   ```bash
   export PUSHGATEWAY_URL=http://localhost:9091
   python scripts/run_experiment.py --data-object yellow_tripdata_2025-09.parquet
   ```

### Grafana Shows "No Data"

1. **Check time range**: Make sure it includes experiment execution time
2. **Check query**: Verify the PromQL query is correct
3. **Check data source**: Verify Prometheus connection
4. **Refresh dashboard**: Click refresh button

### Metrics Not Appearing After Running Experiments

1. **Check PUSHGATEWAY_URL**: Must be set when running experiments
2. **Check Pushgateway is running**: `docker-compose ps pushgateway`
3. **Check Prometheus is scraping Pushgateway**: http://localhost:9090/targets
4. **Wait a few seconds**: Prometheus scrapes every 15s

## Quick Test

Run this complete test:

```bash
# 1. Start services
docker-compose up -d

# 2. Wait for services
sleep 30

# 3. Run experiment with metrics
export PUSHGATEWAY_URL=http://localhost:9091
python scripts/run_experiment.py \
  --data-object yellow_tripdata_2025-09.parquet \
  --max-samples 100

# 4. Wait for Prometheus to scrape
sleep 20

# 5. Check Prometheus
curl "http://localhost:9090/api/v1/query?query=experiments_total"

# 6. Open Grafana and check dashboard
# http://localhost:3000
```

## Expected Results

After running experiments, you should see:

- **Prometheus**: Metrics in queries
- **Grafana Dashboards**: Panels showing data
- **Pushgateway**: Metrics at http://localhost:9091/metrics

If metrics still don't appear, check:
1. Services are running
2. Time range includes experiment time
3. Metrics were actually generated (run experiments)
4. Prometheus is scraping successfully

