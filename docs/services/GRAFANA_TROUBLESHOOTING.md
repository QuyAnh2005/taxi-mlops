# Grafana Troubleshooting: No Metrics Visible

## Quick Fix Checklist

1. ✅ **Set PUSHGATEWAY_URL** (Required!)
   ```bash
   export PUSHGATEWAY_URL=http://localhost:9091
   ```

2. ✅ **Run experiments** to generate metrics:
   ```bash
   python scripts/run_experiment.py --data-object yellow_tripdata_2025-09.parquet
   ```

3. ✅ **Wait 15-30 seconds** for Prometheus to scrape Pushgateway

4. ✅ **Check time range** in Grafana (must include experiment time)

## Step-by-Step Verification

### Step 1: Verify Metrics Are Pushed

```bash
# Check Pushgateway has metrics
curl http://localhost:9091/metrics | grep experiments_total
```

**Expected**: Should see `experiments_total` metrics

### Step 2: Verify Prometheus is Scraping

```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets | python3 -m json.tool | grep -A 5 pushgateway
```

**Expected**: `"health": "up"` for pushgateway job

### Step 3: Query Prometheus Directly

Open http://localhost:9090 and try:
```promql
experiments_total
```

**Expected**: Should see metric values

### Step 4: Check Grafana Data Source

1. Open http://localhost:3000
2. Go to Configuration → Data Sources
3. Click "Prometheus"
4. Click "Save & Test"
5. Should show "Data source is working"

### Step 5: Check Dashboard Time Range

1. Open a dashboard
2. Click time picker (top right)
3. Select "Last 1 hour" or "Last 6 hours"
4. Make sure this includes when you ran experiments

### Step 6: Test Query in Grafana

1. Go to Explore (compass icon)
2. Select "Prometheus" data source
3. Enter query: `experiments_total`
4. Click "Run query"
5. Should see data points

## Common Issues

### Issue: "No data" in Grafana

**Cause**: No metrics generated yet or time range doesn't match

**Fix**:
1. Run experiments with `PUSHGATEWAY_URL` set
2. Wait 30 seconds
3. Check time range includes experiment time
4. Refresh dashboard

### Issue: Prometheus shows empty results

**Cause**: Prometheus hasn't scraped Pushgateway yet

**Fix**:
1. Wait 15-30 seconds after pushing metrics
2. Check Prometheus targets: http://localhost:9090/targets
3. Verify pushgateway target is "up"

### Issue: Pushgateway has no metrics

**Cause**: `PUSHGATEWAY_URL` not set when running experiments

**Fix**:
```bash
export PUSHGATEWAY_URL=http://localhost:9091
python scripts/run_experiment.py --data-object yellow_tripdata_2025-09.parquet
```

### Issue: Dashboard not found

**Cause**: Dashboards not properly provisioned

**Fix**:
1. Restart Grafana: `docker-compose restart grafana`
2. Check dashboard files exist: `ls docker/grafana/dashboards/`
3. Manually import dashboard JSON if needed

## Test Script

Use the test script to generate metrics:

```bash
export PUSHGATEWAY_URL=http://localhost:9091
python scripts/test_metrics.py
```

Then:
1. Wait 20-30 seconds
2. Check Prometheus: http://localhost:9090/graph?g0.expr=experiments_total
3. Check Grafana: http://localhost:3000

## Still Not Working?

1. **Check all services are running**:
   ```bash
   docker-compose ps
   ```

2. **Check service logs**:
   ```bash
   docker-compose logs prometheus | tail -20
   docker-compose logs pushgateway | tail -20
   docker-compose logs grafana | tail -20
   ```

3. **Verify network connectivity**:
   ```bash
   docker-compose exec prometheus wget -qO- http://pushgateway:9091/metrics | head -5
   ```

4. **Restart monitoring stack**:
   ```bash
   docker-compose restart prometheus pushgateway grafana
   ```

