#!/usr/bin/env python3
"""Prometheus metrics exporter for Taxi MLOps application"""

import os
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import psutil
import sys

# Add workspace to path
sys.path.insert(0, '/workspace')

# Import metrics from monitoring module (uses default registry)
try:
    from src.monitoring.metrics import (
        experiments_total,
        experiment_duration_seconds,
        experiment_failures_total,
        flow_runs_total,
        flow_run_duration_seconds,
        active_experiments,
    )
    print("✓ Imported metrics from monitoring module")
except ImportError as e:
    print(f"⚠ Could not import metrics from monitoring module: {e}")
    print("Using local metric definitions...")
    # Define metrics locally if import fails
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

# Additional system metrics
database_connections = Gauge(
    'database_connections_active',
    'Number of active database connections'
)

memory_usage_bytes = Gauge(
    'application_memory_usage_bytes',
    'Application memory usage in bytes'
)

cpu_usage_percent = Gauge(
    'application_cpu_usage_percent',
    'Application CPU usage percentage'
)

prefect_active_flows = Gauge(
    'prefect_active_flows',
    'Number of active Prefect flows'
)


class MetricsHandler(BaseHTTPRequestHandler):
    """HTTP handler for Prometheus metrics endpoint"""

    def do_GET(self):
        if self.path == '/metrics':
            # Update dynamic metrics
            update_metrics()
            
            self.send_response(200)
            self.send_header('Content-Type', CONTENT_TYPE_LATEST)
            self.end_headers()
            self.wfile.write(generate_latest())
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Suppress default logging
        pass


def update_metrics():
    """Update dynamic metrics from system and database"""
    # System metrics
    try:
        process = psutil.Process()
        memory_usage_bytes.set(process.memory_info().rss)
        cpu_usage_percent.set(process.cpu_percent(interval=0.1))
    except Exception:
        pass
    
    # Database metrics (if available)
    try:
        from src.storage import PostgresClient
        client = PostgresClient()
        # Query active connections (simplified)
        database_connections.set(1)  # Placeholder
    except Exception:
        database_connections.set(0)
    
    # Prefect metrics (would need Prefect API client)
    # For now, set placeholder values
    prefect_active_flows.set(0)


def main():
    """Start metrics exporter server"""
    port = int(os.environ.get('PROMETHEUS_PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), MetricsHandler)
    print(f'Metrics exporter started on port {port}')
    print(f'Metrics endpoint: http://0.0.0.0:{port}/metrics')
    print(f'Health endpoint: http://0.0.0.0:{port}/health')
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down metrics exporter...')
        server.shutdown()


if __name__ == '__main__':
    main()
