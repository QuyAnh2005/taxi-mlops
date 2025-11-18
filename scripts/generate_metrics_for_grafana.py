#!/usr/bin/env python3
"""Generate multiple metrics to populate Grafana dashboards"""

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
    print("Generating metrics for Grafana dashboards...")
    print("This will create multiple experiment and flow metrics...")
    
    # Generate multiple experiments
    for i in range(5):
        adapter_type = "sklearn" if i % 2 == 0 else "sklearn_parallel"
        with MetricsCollector(adapter_type=adapter_type, experiment_id=f"test-{i:03d}"):
            time.sleep(0.1)  # Simulate experiment
        print(f"  ✓ Generated experiment {i+1}/5")
    
    # Generate flow metrics
    for i in range(3):
        record_flow_metrics("experiment_pipeline", 5.5 + i, True)
        record_flow_metrics("evaluation_pipeline", 3.2 + i, True)
        print(f"  ✓ Generated flow metrics {i+1}/3")
    
    print("\n✓ Metrics generated successfully!")
    print("\nNext steps:")
    print("1. Wait 20-30 seconds for Prometheus to scrape")
    print("2. Open Prometheus: http://localhost:9090")
    print("   - Query: experiments_total")
    print("   - Query: prefect_flow_runs_total")
    print("3. Open Grafana: http://localhost:3000")
    print("   - Go to Explore")
    print("   - Select Prometheus datasource")
    print("   - Query: experiments_total")
    print("   - Or check Dashboards → Browse")

if __name__ == "__main__":
    main()

