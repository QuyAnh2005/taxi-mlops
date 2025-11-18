#!/usr/bin/env python3
"""Test script to generate metrics and verify they appear in Grafana"""

import os
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set Pushgateway URL
os.environ['PUSHGATEWAY_URL'] = 'http://localhost:9091'

from src.monitoring import MetricsCollector, record_flow_metrics

def main():
    print("Generating test metrics...")
    
    # Generate some test metrics
    with MetricsCollector(adapter_type="sklearn", experiment_id="test-001"):
        time.sleep(0.1)  # Simulate experiment
    
    with MetricsCollector(adapter_type="sklearn_parallel", experiment_id="test-002"):
        time.sleep(0.1)
    
    record_flow_metrics("test_flow", 5.5, True)
    record_flow_metrics("test_flow", 3.2, True)
    
    print("✓ Metrics generated")
    print("\nCheck metrics:")
    print("1. Pushgateway: http://localhost:9091/metrics")
    print("2. Prometheus: http://localhost:9090/graph?g0.expr=experiments_total")
    print("3. Grafana: http://localhost:3000 (wait 15-30 seconds for Prometheus to scrape)")

if __name__ == "__main__":
    main()

