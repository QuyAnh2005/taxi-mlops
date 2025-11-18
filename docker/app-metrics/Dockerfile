FROM python:3.11-slim

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    prometheus-client \
    psutil

# Copy entire workspace (for src imports)
COPY . /workspace/

# Expose metrics port
EXPOSE 8000

# Run metrics exporter
CMD ["python", "docker/app-metrics/metrics_exporter.py"]

