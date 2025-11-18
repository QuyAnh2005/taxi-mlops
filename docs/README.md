# Documentation Index

## Overview

This directory contains comprehensive documentation for the Taxi MLOps platform, organized by category.

## Documentation Structure

```
docs/
├── README.md (this file)
├── guides/              # Getting started and user guides
├── architecture/        # System architecture and design
├── services/           # Service-specific documentation
├── workflows/          # Prefect workflow guides
└── demo/              # Demo and presentation materials
```

## Quick Links

### Getting Started
- [Quick Start Guide](guides/QUICKSTART.md) - Get up and running
- [Prefect Quick Start](guides/QUICKSTART_PREFECT.md) - Prefect setup
- [Monitoring Quick Start](guides/QUICKSTART_MONITORING.md) - Monitoring setup

### User Guides
- [Prefect Workflows](workflows/PREFECT_WORKFLOWS.md) - Complete workflow guide
- [Evaluation Framework](guides/EVALUATION.md) - Experiment evaluation
- [Troubleshooting](guides/TROUBLESHOOTING.md) - Common issues and solutions

### Architecture
- [System Architecture](architecture/ARCHITECTURE.md) - High-level design
- [Project Overview](guides/PROJECT_OVERVIEW.md) - Project structure

### Services
- [Prefect Usage](services/PREFECT_USAGE.md) - Prefect configuration
- [MLflow Usage](services/MLFLOW_USAGE.md) - Experiment tracking
- [MinIO Usage](services/MINIO_USAGE.md) - Data storage
- [Monitoring Guide](services/MONITORING.md) - Observability stack
- [Configuration](services/CONFIGURATION.md) - System configuration

### Demo & Presentation
- [Demo Guide](demo/DEMO_GUIDE.md) - Demo preparation
- [Presentation Materials](demo/PRESENTATION.md) - Slides and talking points

### Reference
- [Changelog](guides/CHANGELOG.md) - Project history
- [Project Report](guides/PROJECT_REPORT.md) - Final project report

## Documentation by Topic

### Installation & Setup
1. [Quick Start Guide](guides/QUICKSTART.md)
2. [Configuration Guide](services/CONFIGURATION.md)
3. [Deployment Guide](guides/DEPLOYMENT.md)

### Usage
1. [Prefect Workflows](workflows/PREFECT_WORKFLOWS.md)
2. [MinIO Usage](services/MINIO_USAGE.md)
3. [Monitoring Guide](services/MONITORING.md)

### Architecture
1. [System Architecture](architecture/ARCHITECTURE.md)
2. [Project Overview](guides/PROJECT_OVERVIEW.md)

### Services
1. [Prefect Usage](services/PREFECT_USAGE.md)
2. [MLflow Usage](services/MLFLOW_USAGE.md)
3. [Monitoring Stack](services/MONITORING.md)

### Development
1. [Troubleshooting](guides/TROUBLESHOOTING.md)
2. [Project Report](guides/PROJECT_REPORT.md)

## Contributing to Documentation

When adding or updating documentation:

1. **Place files in appropriate directories**
2. **Follow existing naming conventions**
3. **Update this index**
4. **Include examples and code snippets**
5. **Keep documentation up-to-date**

## Documentation Standards

- **Format**: Markdown (.md)
- **Style**: Clear, concise, with examples
- **Structure**: Table of contents for long documents
- **Code**: Include executable examples
- **Links**: Use relative paths

## Finding Documentation

### By Task
- **Setting up**: See `guides/QUICKSTART*.md`
- **Using workflows**: See `workflows/PREFECT_WORKFLOWS.md`
- **Configuring services**: See `services/` directory
- **Understanding architecture**: See `architecture/ARCHITECTURE.md`

### By Service
- **Prefect**: `services/PREFECT_USAGE.md`, `workflows/PREFECT_WORKFLOWS.md`
- **MLflow**: `services/MLFLOW_USAGE.md`
- **MinIO**: `services/MINIO_USAGE.md`
- **Monitoring**: `services/MONITORING.md`

### By Audience
- **New Users**: Start with `guides/QUICKSTART.md`
- **Developers**: See `architecture/` and `workflows/`
- **Operators**: See `services/` and `guides/DEPLOYMENT.md`
- **Presenters**: See `demo/` directory

