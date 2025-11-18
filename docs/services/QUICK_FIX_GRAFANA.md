# Quick Fix: See Metrics in Grafana

## Problem: No Data in Grafana/Prometheus UI

If you see empty dashboards or "No data queried yet", follow these steps:

## Step 1: Generate Metrics

**IMPORTANT**: Metrics only appear after running experiments!

```bash
# Set Pushgateway URL (REQUIRED!)
export PUSHGATEWAY_URL=http://localhost:9091

# Generate test metrics
python scripts/generate_metrics_for_grafana.py
```

Or run a real experiment:
```bash
export PUSHGATEWAY_URL=http://localhost:9091
python scripts/run_experiment.py \
  --data-object yellow_tripdata_2025-09.parquet \
  --max-samples 1000
```

## Step 2: Wait for Prometheus to Scrape

Wait **20-30 seconds** after generating metrics for Prometheus to scrape Pushgateway.

## Step 3: Query Prometheus

1. Open http://localhost:9090
2. In the query box, type: `experiments_total`
3. Click **"Execute"** button
4. You should see results in the Table or Graph tab

Try these queries:
- `experiments_total` - Total experiments
- `prefect_flow_runs_total` - Flow runs
- `rate(experiments_total[5m])` - Experiment rate

## Step 4: View in Grafana

### Option A: Use Explore (Easiest)

1. Open http://localhost:3000
2. Login: admin/admin
3. Click **"Explore"** (compass icon) in left menu
4. Select **"Prometheus"** datasource (top dropdown)
5. Enter query: `experiments_total`
6. Click **"Run query"**
7. You should see a graph or table

### Option B: Import Dashboard

1. Open http://localhost:3000
2. Click **"+"** → **"Import dashboard"**
3. Copy and paste the dashboard JSON from:
   - `docker/grafana/dashboards/prefect-monitoring.json`
   - `docker/grafana/dashboards/experiment-monitoring.json`
4. Click **"Load"**
5. Select **"Prometheus"** datasource
6. Click **"Import"**

### Option C: Create Simple Dashboard

1. Click **"+"** → **"Create dashboard"**
2. Click **"Add visualization"**
3. Select **"Prometheus"** datasource
4. Enter query: `experiments_total`
5. Click **"Run query"**
6. Click **"Apply"**

## Step 5: Check Time Range

**CRITICAL**: Make sure time range includes when you ran experiments!

1. Click time picker (top right)
2. Select **"Last 1 hour"** or **"Last 6 hours"**
3. Or set custom range to include experiment time

## Troubleshooting

### Still No Data?

1. **Check metrics exist in Pushgateway**:
   ```bash
   curl http://localhost:9091/metrics | grep experiments_total
   ```

2. **Check Prometheus is scraping**:
   - Open http://localhost:9090/targets
   - Verify `pushgateway` target is "up"

3. **Check Prometheus has data**:
   ```bash
   curl 'http://localhost:9090/api/v1/query?query=experiments_total'
   ```

4. **Regenerate metrics**:
   ```bash
   export PUSHGATEWAY_URL=http://localhost:9091
   python scripts/generate_metrics_for_grafana.py
   sleep 30
   ```

5. **Check Grafana datasource**:
   - Configuration → Data Sources
   - Click "Prometheus"
   - Click "Save & Test"
   - Should show "Data source is working"

## Quick Test Script

Run this complete test:

```bash
# 1. Generate metrics
export PUSHGATEWAY_URL=http://localhost:9091
python scripts/generate_metrics_for_grafana.py

# 2. Wait for scraping
echo "Waiting 30 seconds for Prometheus to scrape..."
sleep 30

# 3. Check Prometheus
echo "Check Prometheus: http://localhost:9090"
echo "Query: experiments_total"

# 4. Check Grafana
echo "Check Grafana: http://localhost:3000"
echo "Go to Explore → Prometheus → experiments_total"
```

## Expected Results

After running the script and waiting:
- **Prometheus**: Should show metrics when you query `experiments_total`
- **Grafana Explore**: Should show graph/table with data
- **Grafana Dashboards**: Should show panels with data (if imported)

If you still don't see data, check:
1. `PUSHGATEWAY_URL` is set
2. Metrics were generated (check Pushgateway)
3. Time range includes experiment time
4. Prometheus scraped successfully (check targets)

