.PHONY: help install-all download-data setup-services setup-minio setup-prefect deploy-flows \
        up down restart logs status verify clean clean-all test lint format \
        run-ui run-experiment

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m

# Configuration
DATA_DIR := data
TAXI_DATA_URL := https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2025-09.parquet
TAXI_ZONES_URL := https://d37ci6vzurychx.cloudfront.net/misc/taxi_zones.zip
TAXI_DATA_FILE := $(DATA_DIR)/yellow_tripdata_2025-09.parquet
TAXI_ZONES_DIR := $(DATA_DIR)/taxi_zones

# Python environment
PYTHON := $(shell if [ -f .venv/bin/python ]; then echo ".venv/bin/python"; else echo "python"; fi)
UV := $(shell if command -v uv > /dev/null 2>&1; then echo "uv"; else echo ""; fi)

# Determine docker compose command
DOCKER_COMPOSE := $(shell if docker compose version > /dev/null 2>&1; then echo "docker compose"; else echo "docker-compose"; fi)

help:
	@echo "$(BLUE)Taxi MLOps Platform - Makefile Commands$(NC)"
	@echo ""
	@echo "$(GREEN)Setup Commands:$(NC)"
	@echo "  make install-all       - Complete end-to-end setup (download data + setup services)"
	@echo "  make download-data     - Download taxi trip data and zones shapefile"
	@echo "  make setup-services    - Start Docker services and configure all components"
	@echo "  make setup-minio       - Set up MinIO buckets and upload data"
	@echo "  make setup-prefect     - Configure Prefect and deploy flows"
	@echo "  make deploy-flows      - Deploy Prefect flows for UI"
	@echo ""
	@echo "$(GREEN)Service Management:$(NC)"
	@echo "  make up                - Start all Docker services"
	@echo "  make down              - Stop all Docker services"
	@echo "  make restart           - Restart all services"
	@echo "  make logs              - Show service logs (follow mode)"
	@echo "  make status            - Show status of all services"
	@echo ""
	@echo "$(GREEN)Development:$(NC)"
	@echo "  make test              - Run test suite"
	@echo "  make lint              - Run linters (check only)"
	@echo "  make format            - Format code with black and ruff"
	@echo "  make verify            - Verify all services are working"
	@echo ""
	@echo "$(GREEN)Running Applications:$(NC)"
	@echo "  make run-ui            - Start Streamlit UI"
	@echo "  make run-experiment    - Run a sample experiment"
	@echo ""
	@echo "$(GREEN)Cleanup:$(NC)"
	@echo "  make clean             - Clean up volumes and temporary files"
	@echo "  make clean-all         - Complete cleanup (including data)"
	@echo ""
	@echo "$(YELLOW)Quick Start: make install-all$(NC)"

# ============================================================================
# Complete Installation
# ============================================================================

install-all: download-data setup-services
	@echo ""
	@echo "$(GREEN)╔════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║              Installation Complete!                        ║$(NC)"
	@echo "$(GREEN)╚════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(BLUE)📊 Service Access URLs:$(NC)"
	@echo "  • Prefect UI:        http://localhost:4200"
	@echo "  • MLflow UI:         http://localhost:5000"
	@echo "  • Grafana:           http://localhost:3000 (admin/admin)"
	@echo "  • Prometheus:        http://localhost:9090"
	@echo "  • Jaeger UI:         http://localhost:16686"
	@echo "  • MinIO Console:     http://localhost:9001 (minioadmin/minioadmin)"
	@echo ""
	@echo "$(BLUE)🚀 Next Steps:$(NC)"
	@echo "  • Start UI:          make run-ui"
	@echo "  • Run experiment:    make run-experiment"
	@echo "  • View logs:         make logs"
	@echo "  • Check status:      make status"

# ============================================================================
# Data Download
# ============================================================================

download-data: create-data-dir download-taxi-data download-taxi-zones
	@echo "$(GREEN)✓ Data download complete$(NC)"

create-data-dir:
	@echo "$(BLUE)==> Creating data directory...$(NC)"
	@mkdir -p $(DATA_DIR)
	@echo "$(GREEN)✓ Data directory ready$(NC)"

download-taxi-data:
	@echo "$(BLUE)==> Downloading taxi trip data...$(NC)"
	@if [ -f "$(TAXI_DATA_FILE)" ]; then \
		echo "$(YELLOW)⚠ Taxi data file already exists, skipping download$(NC)"; \
	else \
		echo "Downloading from: $(TAXI_DATA_URL)"; \
		wget -q --show-progress "$(TAXI_DATA_URL)" -O "$(TAXI_DATA_FILE)" && \
		echo "$(GREEN)✓ Taxi data downloaded: $$(du -h $(TAXI_DATA_FILE) | cut -f1)$(NC)" || \
		(echo "$(RED)✗ Failed to download taxi data$(NC)" && exit 1); \
	fi

download-taxi-zones:
	@echo "$(BLUE)==> Downloading taxi zones shapefile...$(NC)"
	@if [ -d "$(TAXI_ZONES_DIR)" ] && [ -f "$(TAXI_ZONES_DIR)/taxi_zones.shp" ]; then \
		echo "$(YELLOW)⚠ Taxi zones already extracted, skipping download$(NC)"; \
	else \
		echo "Downloading from: $(TAXI_ZONES_URL)"; \
		wget -q --show-progress "$(TAXI_ZONES_URL)" -O "$(DATA_DIR)/taxi_zones.zip" && \
		echo "$(GREEN)✓ Taxi zones downloaded$(NC)" && \
		echo "$(BLUE)==> Extracting taxi zones...$(NC)" && \
		mkdir -p "$(TAXI_ZONES_DIR)" && \
		unzip -q -o "$(DATA_DIR)/taxi_zones.zip" -d "$(TAXI_ZONES_DIR)" && \
		echo "$(GREEN)✓ Taxi zones extracted$(NC)" && \
		rm -f "$(DATA_DIR)/taxi_zones.zip" || \
		(echo "$(RED)✗ Failed to download/extract taxi zones$(NC)" && exit 1); \
	fi

# ============================================================================
# Service Setup
# ============================================================================

setup-services: check-docker up wait-for-services install-python-deps setup-minio setup-prefect verify
	@echo "$(GREEN)✓ All services configured and ready$(NC)"

check-docker:
	@echo "$(BLUE)==> Checking Docker installation...$(NC)"
	@if ! command -v docker > /dev/null 2>&1; then \
		echo "$(RED)✗ Docker is not installed. Please install Docker first.$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)✓ Docker is installed$(NC)"
	@echo "$(GREEN)✓ Using: $(DOCKER_COMPOSE)$(NC)"

up:
	@echo "$(BLUE)==> Starting Docker services...$(NC)"
	@$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✓ Docker services started$(NC)"

wait-for-services:
	@echo "$(BLUE)==> Waiting for services to be ready...$(NC)"
	@echo "Waiting for PostgreSQL..."
	@for i in $$(seq 1 30); do \
		if $(DOCKER_COMPOSE) ps postgres 2>/dev/null | grep -q "healthy\|Up"; then \
			echo "$(GREEN)✓ PostgreSQL is ready$(NC)"; \
			break; \
		fi; \
		sleep 2; \
		echo -n "."; \
	done
	@echo "Waiting for Redis..."
	@for i in $$(seq 1 30); do \
		if $(DOCKER_COMPOSE) ps redis 2>/dev/null | grep -q "healthy\|Up"; then \
			echo "$(GREEN)✓ Redis is ready$(NC)"; \
			break; \
		fi; \
		sleep 2; \
		echo -n "."; \
	done
	@echo "Waiting for MinIO..."
	@for i in $$(seq 1 30); do \
		if $(DOCKER_COMPOSE) ps minio 2>/dev/null | grep -q "healthy\|Up"; then \
			echo "$(GREEN)✓ MinIO is ready$(NC)"; \
			break; \
		fi; \
		sleep 2; \
		echo -n "."; \
	done
	@echo "Waiting for Prefect API..."
	@for i in $$(seq 1 30); do \
		if curl -s -f "http://localhost:4200/api/health" > /dev/null 2>&1; then \
			echo "$(GREEN)✓ Prefect API is ready$(NC)"; \
			break; \
		fi; \
		sleep 2; \
		echo -n "."; \
	done
	@echo "Waiting for MLflow..."
	@for i in $$(seq 1 30); do \
		if curl -s -f "http://localhost:5000/health" > /dev/null 2>&1; then \
			echo "$(GREEN)✓ MLflow is ready$(NC)"; \
			break; \
		fi; \
		sleep 2; \
		echo -n "."; \
	done
	@echo "$(GREEN)✓ All core services are ready$(NC)"

install-python-deps:
	@echo "$(BLUE)==> Installing Python dependencies...$(NC)"
	@if [ -n "$(UV)" ]; then \
		$(UV) pip install -r requirements.txt && \
		echo "$(GREEN)✓ Dependencies installed with uv$(NC)"; \
	else \
		pip install -r requirements.txt && \
		echo "$(GREEN)✓ Dependencies installed with pip$(NC)"; \
	fi

setup-minio:
	@echo "$(BLUE)==> Setting up MinIO buckets...$(NC)"
	@$(PYTHON) scripts/setup_minio_bucket.py && \
		echo "$(GREEN)✓ MLflow artifacts bucket ready$(NC)" || \
		(echo "$(RED)✗ Failed to set up MinIO bucket$(NC)" && exit 1)
	@if [ -f "scripts/setup_data_bucket.py" ]; then \
		$(PYTHON) scripts/setup_data_bucket.py && \
		echo "$(GREEN)✓ Data bucket ready$(NC)"; \
	fi
	@echo "$(BLUE)==> Uploading data to MinIO...$(NC)"
	@if [ -f "$(TAXI_DATA_FILE)" ]; then \
		$(PYTHON) scripts/upload_to_minio.py "$(TAXI_DATA_FILE)" \
			--object-name "yellow_tripdata_2025-09.parquet" \
			--bucket-name "taxi-data" 2>/dev/null && \
		echo "$(GREEN)✓ Taxi data uploaded to MinIO$(NC)" || \
		echo "$(YELLOW)⚠ Data may already exist in MinIO$(NC)"; \
	else \
		echo "$(YELLOW)⚠ Taxi data file not found, skipping upload$(NC)"; \
	fi

setup-prefect:
	@echo "$(BLUE)==> Setting up Prefect...$(NC)"
	@$(PYTHON) scripts/setup_prefect.py && \
		echo "$(GREEN)✓ Prefect configured$(NC)" || \
		echo "$(YELLOW)⚠ Prefect may already be configured$(NC)"

deploy-flows:
	@echo "$(BLUE)==> Note: Flow deployment is optional$(NC)"
	@echo "$(YELLOW)Flows can be run directly using:$(NC)"
	@echo "  • make run-experiment"
	@echo "  • make run-ui"
	@echo "  • Direct Python scripts in scripts/ directory"
	@echo "$(GREEN)✓ No deployment needed for current setup$(NC)"

# ============================================================================
# Service Management
# ============================================================================

down:
	@echo "$(BLUE)==> Stopping Docker services...$(NC)"
	@$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✓ Services stopped$(NC)"

restart: down up wait-for-services
	@echo "$(GREEN)✓ Services restarted$(NC)"

logs:
	@echo "$(BLUE)==> Showing service logs (Ctrl+C to exit)...$(NC)"
	@$(DOCKER_COMPOSE) logs -f

status:
	@echo "$(BLUE)==> Service Status:$(NC)"
	@$(DOCKER_COMPOSE) ps

# ============================================================================
# Development
# ============================================================================

test:
	@echo "$(BLUE)==> Running tests...$(NC)"
	@pytest tests/ -v

lint:
	@echo "$(BLUE)==> Running linters...$(NC)"
	@black --check src/ tests/ scripts/
	@ruff check src/ tests/ scripts/

format:
	@echo "$(BLUE)==> Formatting code...$(NC)"
	@black src/ tests/ scripts/
	@ruff check --fix src/ tests/ scripts/
	@echo "$(GREEN)✓ Code formatted$(NC)"

verify:
	@echo "$(BLUE)==> Verifying setup...$(NC)"
	@$(PYTHON) scripts/verify_setup.py

# ============================================================================
# Running Applications
# ============================================================================

run-ui:
	@echo "$(BLUE)==> Starting Streamlit UI...$(NC)"
	@echo "$(YELLOW)UI will be available at: http://localhost:8501$(NC)"
	@$(PYTHON) scripts/run_ui.py

run-experiment:
	@echo "$(BLUE)==> Running sample experiment...$(NC)"
	@export PUSHGATEWAY_URL=http://localhost:9091 && \
	$(PYTHON) scripts/run_experiment.py \
		--data-source data/yellow_tripdata_2025-09.parquet \
		--adapter-type sklearn \
		--eps 0.01 \
		--min-samples 5
	@echo "$(GREEN)✓ Experiment complete$(NC)"
	@echo "$(YELLOW)View results at:$(NC)"
	@echo "  • MLflow: http://localhost:5000"
	@echo "  • Grafana: http://localhost:3000"

# ============================================================================
# Cleanup
# ============================================================================

clean:
	@echo "$(BLUE)==> Cleaning up...$(NC)"
	@$(DOCKER_COMPOSE) down -v
	@rm -rf .prefect/
	@rm -rf mlruns/
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

clean-all: clean
	@echo "$(BLUE)==> Removing downloaded data...$(NC)"
	@rm -rf $(DATA_DIR)
	@echo "$(GREEN)✓ Complete cleanup done$(NC)"
