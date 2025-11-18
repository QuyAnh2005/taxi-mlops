# Quick Start: Monitoring Stack

## Start Monitoring Services

```bash
# Start all services including monitoring
docker-compose up -d

# Wait for services to be ready
sleep 30

# Verify services are running
docker-compose ps
```

## Access Dashboards

1. **Grafana**: http://localhost:3000
   - Username: `admin`
   - Password: `admin`
   - Pre-configured dashboards available

2. **Prometheus**: http://localhost:9090
   - View metrics and targets
   - Query metrics with PromQL

3. **Jaeger**: http://localhost:16686
   - View distributed traces

4. **Alertmanager**: http://localhost:9093
   - View and manage alerts

## View Metrics

### In Grafana

1. Login to Grafana
2. Go to "Dashboards" → "Browse"
3. Select:
   - **Prefect Flow Monitoring**: Flow execution metrics
   - **Experiment Monitoring**: Experiment metrics

### In Prometheus

1. Open http://localhost:9090
2. Go to "Graph" tab
3. Try queries:
   ```promql
   # Total experiments
   sum(experiments_total)
   
   # Experiment success rate
   sum(rate(experiments_total{status="success"}[5m])) / 
   sum(rate(experiments_total[5m])) * 100
   
   # Average experiment duration
   rate(experiment_duration_seconds_sum[5m]) / 
   rate(experiment_duration_seconds_count[5m])
   ```

## Run an Experiment to Generate Metrics

**IMPORTANT**: You must set `PUSHGATEWAY_URL` for metrics to be collected:

```bash
# Set Pushgateway URL
export PUSHGATEWAY_URL=http://localhost:9091

# Run an experiment - metrics will be automatically collected
python scripts/run_experiment.py \
  --data-object yellow_tripdata_2025-09.parquet \
  --adapter-type sklearn \
  --max-samples 1000
```

Or use the test script:
```bash
export PUSHGATEWAY_URL=http://localhost:9091
python scripts/test_metrics.py
```

After running, check:
- **Grafana**: Metrics appear in dashboards
- **Prometheus**: Query `experiments_total` to see the count
- **Jaeger**: Traces appear (if tracing is enabled)

## View Logs

1. Open Grafana
2. Go to "Explore"
3. Select "Loki" data source
4. Query: `{service="prefect-server"}`

## Troubleshooting

### Services Not Starting

```bash
# Check logs
docker-compose logs prometheus
docker-compose logs grafana
docker-compose logs loki

# Restart services
docker-compose restart prometheus grafana loki
```

### No Metrics Appearing

1. Check app-metrics is running: `docker-compose ps app-metrics`
2. Check metrics endpoint: `curl http://localhost:8000/metrics`
3. Check Prometheus targets: http://localhost:9090/targets
4. Verify Prometheus is scraping: http://localhost:9090/graph?g0.expr=up

### Grafana No Data

1. Verify data source connection in Grafana
2. Check time range (default is last 6 hours)
3. Verify Prometheus has data
4. Check dashboard queries are correct

## Next Steps

- Configure alert notifications (see `docs/MONITORING.md`)
- Create custom dashboards
- Set up log retention policies
- Configure trace sampling

For detailed information, see [docs/MONITORING.md](docs/MONITORING.md).

