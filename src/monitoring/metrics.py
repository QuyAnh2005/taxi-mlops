"""Prometheus metrics collection for workflows"""

from typing import Any
from prometheus_client import Counter, Histogram, Gauge, push_to_gateway
import time
import os

# Metrics definitions
experiments_total = Counter(
    'experiments_total',
    'Total number of experiments run',
    ['adapter_type', 'status']
)

experiment_duration_seconds = Histogram(
    'experiment_duration_seconds',
    'Experiment execution duration in seconds',
    ['adapter_type'],
    buckets=[1, 5, 10, 30, 60, 120, 300, 600, 1800, 3600]
)

experiment_failures_total = Counter(
    'experiment_failures_total',
    'Total number of failed experiments',
    ['adapter_type', 'error_type']
)

flow_runs_total = Counter(
    'prefect_flow_runs_total',
    'Total number of Prefect flow runs',
    ['flow_name', 'status']
)

flow_run_duration_seconds = Histogram(
    'prefect_flow_run_duration_seconds',
    'Prefect flow run duration in seconds',
    ['flow_name'],
    buckets=[1, 5, 10, 30, 60, 120, 300, 600, 1800, 3600]
)

active_experiments = Gauge(
    'active_experiments',
    'Number of currently running experiments',
    ['adapter_type']
)


class MetricsCollector:
    """Context manager for collecting experiment metrics"""

    def __init__(self, adapter_type: str, experiment_id: str | None = None):
        self.adapter_type = adapter_type
        self.experiment_id = experiment_id
        self.start_time: float | None = None

    def __enter__(self):
        self.start_time = time.time()
        active_experiments.labels(adapter_type=self.adapter_type).inc()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time if self.start_time else 0
        active_experiments.labels(adapter_type=self.adapter_type).dec()

        if exc_type is None:
            # Success
            experiments_total.labels(
                adapter_type=self.adapter_type,
                status='success'
            ).inc()
            experiment_duration_seconds.labels(
                adapter_type=self.adapter_type
            ).observe(duration)
        else:
            # Failure
            error_type = exc_type.__name__ if exc_type else 'unknown'
            experiments_total.labels(
                adapter_type=self.adapter_type,
                status='failure'
            ).inc()
            experiment_failures_total.labels(
                adapter_type=self.adapter_type,
                error_type=error_type
            ).inc()

        # Push metrics to Pushgateway if configured
        pushgateway_url = os.getenv('PUSHGATEWAY_URL', 'http://localhost:9091')
        try:
            push_to_gateway(
                pushgateway_url,
                job='taxi-mlops-experiments',
                registry=None,  # Use default registry
            )
        except Exception:
            # Silently fail if pushgateway is not available
            pass

        return False  # Don't suppress exceptions


def record_experiment_metrics(
    adapter_type: str,
    duration: float,
    success: bool,
    error_type: str | None = None,
) -> None:
    """
    Record experiment metrics

    Args:
        adapter_type: Type of adapter used
        duration: Experiment duration in seconds
        success: Whether experiment succeeded
        error_type: Type of error if failed
    """
    status = 'success' if success else 'failure'
    experiments_total.labels(
        adapter_type=adapter_type,
        status=status
    ).inc()

    experiment_duration_seconds.labels(
        adapter_type=adapter_type
    ).observe(duration)

    if not success and error_type:
        experiment_failures_total.labels(
            adapter_type=adapter_type,
            error_type=error_type
        ).inc()
    
    # Push metrics to Pushgateway if configured
    pushgateway_url = os.getenv('PUSHGATEWAY_URL', 'http://localhost:9091')
    try:
        push_to_gateway(
            pushgateway_url,
            job='taxi-mlops-experiments',
            registry=None,  # Use default registry
        )
    except Exception:
        # Silently fail if pushgateway is not available
        pass


def record_flow_metrics(
    flow_name: str,
    duration: float,
    success: bool,
) -> None:
    """
    Record Prefect flow metrics

    Args:
        flow_name: Name of the flow
        duration: Flow duration in seconds
        success: Whether flow succeeded
    """
    status = 'success' if success else 'failure'
    flow_runs_total.labels(
        flow_name=flow_name,
        status=status
    ).inc()

    flow_run_duration_seconds.labels(
        flow_name=flow_name
    ).observe(duration)
    
    # Push metrics to Pushgateway if configured
    pushgateway_url = os.getenv('PUSHGATEWAY_URL', 'http://localhost:9091')
    try:
        push_to_gateway(
            pushgateway_url,
            job='taxi-mlops-workflows',
            registry=None,  # Use default registry
        )
    except Exception:
        # Silently fail if pushgateway is not available
        pass

