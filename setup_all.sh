#!/bin/bash
# End-to-end setup script for Taxi MLOps Platform
# This script downloads data, sets up all services, and prepares everything for use
#
# Usage:
#   ./scripts/setup_all.sh
#
# What it does:
#   1. Downloads taxi trip data (yellow_tripdata_2025-09.parquet)
#   2. Downloads and extracts taxi zones shapefile
#   3. Starts all Docker services (PostgreSQL, Redis, MinIO, MLflow, Prefect, etc.)
#   4. Waits for services to be healthy
#   5. Sets up MinIO buckets
#   6. Uploads data to MinIO
#   7. Configures Prefect
#   8. Verifies all services are working
#   9. Displays access URLs and next steps
#
# Prerequisites:
#   - Docker and Docker Compose installed
#   - Python 3.11+ installed
#   - wget and unzip commands available

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# If script is in scripts/, go up one level. If in root, use current dir.
if [[ "$SCRIPT_DIR" == *"/scripts" ]]; then
    PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
else
    PROJECT_ROOT="$SCRIPT_DIR"
fi
DATA_DIR="${PROJECT_ROOT}/data"
TAXI_DATA_URL="https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2025-09.parquet"
TAXI_ZONES_URL="https://d37ci6vzurychx.cloudfront.net/misc/taxi_zones.zip"
TAXI_DATA_FILE="${DATA_DIR}/yellow_tripdata_2025-09.parquet"
TAXI_ZONES_ZIP="${DATA_DIR}/taxi_zones.zip"
TAXI_ZONES_DIR="${DATA_DIR}/taxi_zones"

# Docker Compose command (will be set after checking)
DOCKER_COMPOSE=""

# Functions
print_step() {
    echo -e "\n${BLUE}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

wait_for_service() {
    local service_name=$1
    local url=$2
    local max_attempts=30
    local attempt=1
    
    print_step "Waiting for ${service_name} to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            print_success "${service_name} is ready!"
            return 0
        fi
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "${service_name} did not become ready after $((max_attempts * 2)) seconds"
    return 1
}

wait_for_docker_service() {
    local service_name=$1
    local max_attempts=60
    local attempt=1
    
    print_step "Waiting for Docker service ${service_name} to be healthy..."
    
    while [ $attempt -le $max_attempts ]; do
        # Use the docker compose command (set globally)
        # Try with -f flag first, then without
        if [ -n "$DOCKER_COMPOSE" ]; then
            if $DOCKER_COMPOSE -f docker-compose.yml ps "$service_name" 2>/dev/null | grep -q "healthy\|Up"; then
                print_success "${service_name} is healthy!"
                return 0
            elif $DOCKER_COMPOSE ps "$service_name" 2>/dev/null | grep -q "healthy\|Up"; then
                print_success "${service_name} is healthy!"
                return 0
            fi
        fi
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "${service_name} did not become healthy after $((max_attempts * 2)) seconds"
    return 1
}

# Main script
echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Taxi MLOps Platform - End-to-End Setup Script        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Change to project root and verify
cd "$PROJECT_ROOT"
if [ ! -f "docker-compose.yml" ]; then
    print_error "docker-compose.yml not found in $PROJECT_ROOT"
    print_error "Please run this script from the project root directory"
    exit 1
fi
print_success "Found docker-compose.yml in $PROJECT_ROOT"

# Step 1: Create data directory
print_step "Creating data directory..."
mkdir -p "$DATA_DIR"
print_success "Data directory ready"

# Step 2: Download taxi data
print_step "Downloading taxi trip data..."
if [ -f "$TAXI_DATA_FILE" ]; then
    print_warning "Taxi data file already exists, skipping download"
else
    echo "Downloading from: $TAXI_DATA_URL"
    wget -q --show-progress "$TAXI_DATA_URL" -O "$TAXI_DATA_FILE"
    if [ $? -eq 0 ]; then
        print_success "Taxi data downloaded: $(du -h "$TAXI_DATA_FILE" | cut -f1)"
    else
        print_error "Failed to download taxi data"
        exit 1
    fi
fi

# Step 3: Download and extract taxi zones
print_step "Downloading taxi zones shapefile..."
if [ -d "$TAXI_ZONES_DIR" ] && [ -f "${TAXI_ZONES_DIR}/taxi_zones.shp" ]; then
    print_warning "Taxi zones already extracted, skipping download"
else
    echo "Downloading from: $TAXI_ZONES_URL"
    wget -q --show-progress "$TAXI_ZONES_URL" -O "$TAXI_ZONES_ZIP"
    if [ $? -eq 0 ]; then
        print_success "Taxi zones downloaded"
        
        print_step "Extracting taxi zones..."
        unzip -q -o "$TAXI_ZONES_ZIP" -d "$TAXI_ZONES_DIR"
        if [ $? -eq 0 ]; then
            print_success "Taxi zones extracted to $TAXI_ZONES_DIR"
            # Clean up zip file
            rm -f "$TAXI_ZONES_ZIP"
        else
            print_error "Failed to extract taxi zones"
            exit 1
        fi
    else
        print_error "Failed to download taxi zones"
        exit 1
    fi
fi

# Step 4: Check Docker and Docker Compose
print_step "Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi
print_success "Docker is installed"

# Determine docker compose command
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
    print_success "Using 'docker compose' (newer version)"
elif command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
    print_success "Using 'docker-compose' (legacy version)"
else
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Step 5: Start Docker services
print_step "Starting Docker services..."
# Ensure we're in the project root (already done above, but double-check)
cd "$PROJECT_ROOT" || {
    print_error "Failed to change to project root: $PROJECT_ROOT"
    exit 1
}

# Verify docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    print_error "docker-compose.yml not found in $PROJECT_ROOT"
    print_error "Current directory: $(pwd)"
    exit 1
fi

# Start services - try different approaches
print_step "Starting Docker services with $DOCKER_COMPOSE..."
if $DOCKER_COMPOSE -f "$PROJECT_ROOT/docker-compose.yml" up -d; then
    print_success "Docker services started"
elif cd "$PROJECT_ROOT" && $DOCKER_COMPOSE up -d; then
    # Fallback: ensure we're in the right directory and try without -f
    print_success "Docker services started"
else
    print_error "Failed to start Docker services"
    print_error "Current directory: $(pwd)"
    print_error "docker-compose.yml path: $PROJECT_ROOT/docker-compose.yml"
    print_error "File exists: $([ -f "$PROJECT_ROOT/docker-compose.yml" ] && echo 'yes' || echo 'no')"
    print_error "Docker compose command: $DOCKER_COMPOSE"
    print_warning "Try running manually: cd $PROJECT_ROOT && $DOCKER_COMPOSE up -d"
    exit 1
fi

# Step 6: Wait for services to be ready
print_step "Waiting for services to be healthy..."

wait_for_docker_service "postgres"
wait_for_docker_service "redis"
wait_for_docker_service "minio"

# Wait for HTTP services
wait_for_service "Prefect API" "http://localhost:4200/api/health"
wait_for_service "MLflow" "http://localhost:5000/health"
wait_for_service "MinIO" "http://localhost:9000/minio/health/live"

print_success "All core services are ready!"

# Step 7: Check Python environment
print_step "Checking Python environment..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    exit 1
fi

# Check if virtual environment exists or create one
if [ ! -d ".venv" ]; then
    print_warning "Virtual environment not found, creating one..."
    # Install uv
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Create virtual environment
    uv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies if needed
print_step "Checking Python dependencies..."
if ! python3 -c "import streamlit" &> /dev/null; then
    print_step "Installing Python dependencies..."
    if command -v uv &> /dev/null; then
        uv pip install -r requirements.txt
    else
        pip install -r requirements.txt
    fi
    print_success "Dependencies installed"
else
    print_success "Dependencies already installed"
fi

# Step 8: Set up MinIO buckets
print_step "Setting up MinIO buckets..."
python3 scripts/setup_minio_bucket.py
if [ $? -eq 0 ]; then
    print_success "MinIO bucket ready"
else
    print_error "Failed to set up MinIO bucket"
    exit 1
fi

# Check if data bucket script exists
if [ -f "scripts/setup_data_bucket.py" ]; then
    python3 scripts/setup_data_bucket.py
    if [ $? -eq 0 ]; then
        print_success "Data bucket ready"
    fi
fi

# Step 9: Upload data to MinIO
print_step "Uploading data to MinIO..."
if [ -f "$TAXI_DATA_FILE" ]; then
    python3 scripts/upload_to_minio.py "$TAXI_DATA_FILE" \
        --object-name "yellow_tripdata_2025-09.parquet" \
        --bucket-name "taxi-data" 2>/dev/null || \
    python3 scripts/upload_to_minio.py "$TAXI_DATA_FILE" \
        --object-name "yellow_tripdata_2025-09.parquet"
    
    if [ $? -eq 0 ]; then
        print_success "Taxi data uploaded to MinIO"
    else
        print_warning "Failed to upload to MinIO (may already exist or bucket name differs)"
    fi
fi

# Step 10: Set up Prefect
print_step "Setting up Prefect..."
python3 scripts/setup_prefect.py
if [ $? -eq 0 ]; then
    print_success "Prefect configured"
else
    print_warning "Prefect setup had issues (may already be configured)"
fi

# Deploy flows for UI
print_step "Deploying flows for UI..."
python3 scripts/deploy_flows_for_ui.py
if [ $? -eq 0 ]; then
    print_success "Flows deployed for UI"
else
    print_warning "Failed to deploy flows for UI"
fi

# Step 11: Verify setup
print_step "Verifying setup..."
python3 scripts/verify_setup.py
VERIFY_EXIT=$?

# Step 12: Display summary
echo -e "\n${GREEN}╔════════════════════════════════════════════════════════════╗"
echo "║                    Setup Complete!                        ║"
echo "╚════════════════════════════════════════════════════════════╝${NC}\n"

echo -e "${BLUE}📊 Service Access URLs:${NC}"
echo "  • Prefect UI:        http://localhost:4200"
echo "  • MLflow UI:         http://localhost:5000"
echo "  • Grafana:           http://localhost:3000 (admin/admin)"
echo "  • Prometheus:        http://localhost:9090"
echo "  • Jaeger UI:         http://localhost:16686"
echo "  • MinIO Console:     http://localhost:9001 (minioadmin/minioadmin)"
echo "  • Alertmanager:      http://localhost:9093"

echo -e "\n${BLUE}🚀 Next Steps:${NC}"
echo "  1. Access the UI:"
echo "     python scripts/run_ui.py"
echo ""
echo "  2. Or run an experiment:"
echo "     python scripts/run_experiment.py \\"
echo "       --data-source data/yellow_tripdata_2025-09.parquet \\"
echo "       --adapter-type sklearn \\"
echo "       --eps 0.01 \\"
echo "       --min-samples 5"
echo ""
echo "  3. View services:"
echo "     $DOCKER_COMPOSE ps"

if [ $VERIFY_EXIT -ne 0 ]; then
    echo -e "\n${YELLOW}⚠ Warning: Some services may not be fully ready yet.${NC}"
    echo "   Wait a few more seconds and run: python scripts/verify_setup.py"
fi

echo -e "\n${GREEN}✓ Setup script completed!${NC}\n"

exit $VERIFY_EXIT

