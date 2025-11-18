"""Start a Prometheus metrics server to expose metrics"""

import os
from prometheus_client import start_http_server
from .metrics import (
    experiments_total,
    experiment_duration_seconds,
    experiment_failures_total,
    flow_runs_total,
    flow_run_duration_seconds,
    active_experiments,
)


def start_metrics_server(port: int = 8000) -> None:
    """
    Start a Prometheus metrics HTTP server

    Args:
        port: Port to expose metrics on
    """
    start_http_server(port)
    print(f"Metrics server started on port {port}")
    print(f"Metrics available at http://localhost:{port}/metrics")


if __name__ == "__main__":
    port = int(os.environ.get("PROMETHEUS_PORT", 8000))
    start_metrics_server(port)
    # Keep server running
    import time
    while True:
        time.sleep(1)

