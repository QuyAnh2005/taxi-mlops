# Monitoring & Observability Guide

## Overview

The Taxi MLOps project includes a comprehensive monitoring stack with:

- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- **Loki**: Log aggregation
- **Jaeger**: Distributed tracing
- **Alertmanager**: Alert management

## Services

### Access URLs

- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Alertmanager**: http://localhost:9093
- **Jaeger UI**: http://localhost:16686
- **Loki**: http://localhost:3100

## Setup

### 1. Start Monitoring Stack

```bash
# Start all services including monitoring
docker-compose up -d

# Or start only monitoring services
docker-compose up -d prometheus grafana loki promtail jaeger alertmanager app-metrics
```

### 2. Verify Services

```bash
# Check all services are running
docker-compose ps

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Check Grafana health
curl http://localhost:3000/api/health
```

## Metrics

### Application Metrics

The application exposes Prometheus metrics at `http://localhost:8000/metrics`:

- `experiments_total`: Total experiments by adapter type and status
- `experiment_duration_seconds`: Experiment execution duration histogram
- `experiment_failures_total`: Failed experiments by error type
- `prefect_flow_runs_total`: Prefect flow runs by flow name and status
- `prefect_flow_run_duration_seconds`: Flow run duration histogram
- `active_experiments`: Currently running experiments

### Prefect Metrics

Prefect Server exposes metrics at `/api/metrics` endpoint (if enabled).

## Grafana Dashboards

### Pre-configured Dashboards

1. **Prefect Flow Monitoring**
   - Flow runs over time
   - Flow run duration (95th percentile)
   - Success rate
   - Active flows
   - Flow runs by status

2. **Experiment Monitoring**
   - Experiments over time
   - Experiment duration
   - Success rate
   - Active experiments
   - Experiments by adapter type
   - Failures by error type

### Accessing Dashboards

1. Open Grafana: http://localhost:3000
2. Login with admin/admin
3. Navigate to Dashboards
4. Select "Prefect Flow Monitoring" or "Experiment Monitoring"

### Creating Custom Dashboards

1. Click "+" → "Create Dashboard"
2. Add panels with Prometheus queries
3. Example queries:
   ```promql
   # Experiment success rate
   sum(rate(experiments_total{status="success"}[5m])) / 
   sum(rate(experiments_total[5m])) * 100
   
   # Average experiment duration
   rate(experiment_duration_seconds_sum[5m]) / 
   rate(experiment_duration_seconds_count[5m])
   ```

## Logging with Loki

### Viewing Logs in Grafana

1. Open Grafana
2. Go to "Explore"
3. Select "Loki" data source
4. Query logs:
   ```
   {service="prefect-server"}
   {container="taxi-mlops-prefect-agent"}
   {service="app-metrics"}
   ```

### Log Queries

```logql
# All Prefect logs
{service=~"prefect.*"}

# Error logs
{service="prefect-server"} |= "error"

# Logs from last hour
{service="prefect-server"} [1h]
```

## Tracing with Jaeger

### Viewing Traces

1. Open Jaeger UI: http://localhost:16686
2. Select service: "taxi-mlops"
3. Click "Find Traces"

### Instrumenting Code

```python
from src.monitoring import setup_tracing, get_tracer

# Setup tracing (call once at startup)
setup_tracing(service_name="taxi-mlops")

# Use tracer in your code
tracer = get_tracer("experiment")
with tracer.start_as_current_span("run_experiment") as span:
    span.set_attribute("adapter_type", "sklearn")
    span.set_attribute("eps", 0.5)
    # Your code here
```

## Alerts

### Alert Rules

Alerts are defined in `docker/prometheus/alerts.yml`:

- **PrefectServerDown**: Prefect server unavailable
- **PrefectAgentDown**: Prefect agent unavailable
- **HighFlowFailureRate**: Flow failure rate > 10%
- **SlowFlowExecution**: 95th percentile > 5 minutes
- **HighExperimentFailureRate**: Experiment failure rate > 5%
- **LongExperimentRuntime**: 95th percentile > 10 minutes
- **HighMemoryUsage**: Memory usage > 90%
- **HighCPUUsage**: CPU usage > 80%

### Viewing Alerts

1. **Prometheus**: http://localhost:9090/alerts
2. **Alertmanager**: http://localhost:9093

### Configuring Alert Notifications

Edit `docker/alertmanager/alertmanager.yml` to configure:
- Email notifications
- Slack webhooks
- PagerDuty
- Custom webhooks

## Custom Metrics

### Exporting Custom Metrics

```python
from src.monitoring import MetricsCollector, record_experiment_metrics

# Using context manager
with MetricsCollector(adapter_type="sklearn", experiment_id="exp-123"):
    # Your experiment code
    result = run_experiment(...)

# Or manually
record_experiment_metrics(
    adapter_type="sklearn",
    duration=120.5,
    success=True
)
```

### Flow Metrics

```python
from src.monitoring import record_flow_metrics

record_flow_metrics(
    flow_name="experiment_pipeline",
    duration=300.0,
    success=True
)
```

## Integration with Workflows

Metrics are automatically collected for:
- `experiment_pipeline`: Experiment execution metrics
- `evaluation_pipeline`: Evaluation metrics
- `parameter_sweep_flow`: Parameter sweep metrics

## Troubleshooting

### Prometheus Not Scraping

1. Check targets: http://localhost:9090/targets
2. Verify service endpoints are accessible
3. Check Prometheus logs: `docker-compose logs prometheus`

### Grafana No Data

1. Verify data source connection
2. Check time range
3. Verify metrics are being exported
4. Check Prometheus has data: http://localhost:9090/graph

### Loki No Logs

1. Check Promtail is running: `docker-compose ps promtail`
2. Verify Docker socket is mounted
3. Check Promtail logs: `docker-compose logs promtail`

### Jaeger No Traces

1. Verify tracing is enabled in code
2. Check Jaeger collector is receiving traces
3. Verify service name matches

## Best Practices

1. **Label Metrics Properly**: Use consistent label names
2. **Set Appropriate Buckets**: For histogram metrics
3. **Monitor Alert Fatigue**: Don't create too many alerts
4. **Regular Dashboard Reviews**: Update dashboards as needed
5. **Log Structured Data**: Use JSON logs for better querying
6. **Trace Critical Paths**: Instrument important workflows

## Next Steps

- Configure alert notifications (Slack, email, etc.)
- Create custom dashboards for your use case
- Set up log retention policies
- Configure trace sampling rates
- Add more custom metrics as needed

