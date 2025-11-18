# Troubleshooting Guide

## Common Issues and Solutions

### Services Not Starting

#### Docker Compose Issues
```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs <service-name>

# Restart services
docker-compose restart <service-name>

# Rebuild and restart
docker-compose up -d --build
```

#### Port Conflicts
```bash
# Check if ports are in use
lsof -i :4200  # Prefect
lsof -i :5000  # MLflow
lsof -i :3000  # Grafana
lsof -i :9090  # Prometheus

# Change ports in docker-compose.yml if needed
```

### Prefect Issues

#### Flows Not Appearing in UI
- **Check Prefect server is running**: `docker-compose ps prefect-server`
- **Verify API URL**: `prefect config view`
- **Check agent is connected**: Prefect UI → Agents
- **Review flow registration**: Check flow decorator

#### Flow Execution Fails
- **Check task logs**: Prefect UI → Flow Runs → Task Logs
- **Verify dependencies**: Ensure all packages installed
- **Check data sources**: Verify MinIO/local files accessible
- **Review error messages**: Check exception details

#### Version Mismatch
```bash
# Check versions
prefect version
docker-compose exec prefect-server prefect version

# Update if needed
pip install --upgrade prefect
```

### MLflow Issues

#### MLflow Not Starting
- **Check PostgreSQL**: `docker-compose ps postgres`
- **Verify database exists**: Check `mlflow` database
- **Review logs**: `docker-compose logs mlflow`
- **Check connection string**: Verify in docker-compose.yml

#### Artifacts Not Uploading
- **Check MinIO**: `docker-compose ps minio`
- **Verify credentials**: Check AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
- **Check bucket exists**: Verify `mlflow-artifacts` bucket
- **Review network**: Ensure MLflow can reach MinIO

#### Experiments Not Appearing
- **Check tracking URI**: Verify `MLFLOW_TRACKING_URI`
- **Verify experiment name**: Check experiment exists
- **Review logging code**: Ensure `mlflow.start_run()` is called
- **Check permissions**: Verify database permissions

### MinIO Issues

#### Cannot Connect to MinIO
- **Check service status**: `docker-compose ps minio`
- **Verify endpoint**: Check `MINIO_ENDPOINT` setting
- **Test connection**: `curl http://localhost:9000/minio/health/live`
- **Check credentials**: Verify access key and secret key

#### Upload Fails
- **Check bucket exists**: Use `setup_minio_bucket.py`
- **Verify permissions**: Check bucket policies
- **Review file size**: Check for size limits
- **Check network**: Ensure connectivity

### Monitoring Issues

#### Grafana Not Starting
- **Check logs**: `docker-compose logs grafana`
- **Verify datasources**: Check provisioning files
- **Check permissions**: Verify file permissions
- **Review configuration**: Check datasource URLs

#### No Metrics in Grafana
- **Set PUSHGATEWAY_URL**: `export PUSHGATEWAY_URL=http://localhost:9091`
- **Generate metrics**: Run experiments or test script
- **Wait for scraping**: Allow 20-30 seconds
- **Check time range**: Must include experiment time
- **Verify Prometheus**: Check metrics exist in Prometheus

#### Prometheus No Data
- **Check targets**: http://localhost:9090/targets
- **Verify scraping**: Check target status is "up"
- **Review configuration**: Check prometheus.yml
- **Check network**: Ensure connectivity to targets

#### Pushgateway Not Receiving Metrics
- **Check service**: `docker-compose ps pushgateway`
- **Verify URL**: Check `PUSHGATEWAY_URL` environment variable
- **Test endpoint**: `curl http://localhost:9091/metrics`
- **Review code**: Check metrics pushing code

### Data Pipeline Issues

#### Data Loading Fails
- **Check MinIO**: Verify object exists
- **Check local file**: Verify file path if using local
- **Review permissions**: Check file/object permissions
- **Verify format**: Check file is valid parquet

#### Preprocessing Errors
- **Check data format**: Verify required columns exist
- **Review coordinate extraction**: Check coordinate columns
- **Verify location IDs**: Check if location ID mapping exists
- **Check data quality**: Review validation errors

### Evaluation Issues

#### Metrics Not Calculating
- **Check data**: Verify input data is valid
- **Review labels**: Ensure clustering produced labels
- **Verify metrics code**: Check evaluation module
- **Check dependencies**: Ensure scipy, sklearn installed

#### Statistical Analysis Fails
- **Check sample size**: Ensure sufficient data
- **Review distributions**: Check for normal distribution
- **Verify test assumptions**: Check test requirements
- **Review error messages**: Check specific errors

## Debugging Steps

### 1. Check Service Health
```bash
# All services
docker-compose ps

# Specific service
docker-compose ps <service-name>

# Health checks
curl http://localhost:4200/api/health  # Prefect
curl http://localhost:5000/health       # MLflow
curl http://localhost:3000/api/health   # Grafana
```

### 2. Review Logs
```bash
# All logs
docker-compose logs

# Specific service
docker-compose logs <service-name>

# Follow logs
docker-compose logs -f <service-name>

# Last N lines
docker-compose logs --tail=100 <service-name>
```

### 3. Verify Configuration
```bash
# Check environment variables
env | grep -E "(PREFECT|MLFLOW|MINIO|POSTGRES)"

# Verify config file
python -c "from src.config import settings; print(settings)"

# Check docker-compose
docker-compose config
```

### 4. Test Connectivity
```bash
# Test internal connectivity
docker-compose exec <service> ping <other-service>

# Test external endpoints
curl http://localhost:4200/api/health
curl http://localhost:5000/health
curl http://localhost:3000/api/health
```

### 5. Reset Services
```bash
# Stop all services
docker-compose down

# Remove volumes (WARNING: deletes data)
docker-compose down -v

# Restart services
docker-compose up -d

# Rebuild services
docker-compose up -d --build
```

## Getting Help

### Check Documentation
- [README.md](../README.md)
- [Quick Start Guide](QUICKSTART.md)
- Service-specific guides in `docs/services/`

### Review Logs
- Service logs: `docker-compose logs`
- Application logs: Check Prefect UI
- System logs: Check monitoring dashboards

### Common Solutions
1. Restart services
2. Check configuration
3. Verify dependencies
4. Review error messages
5. Check documentation

## Prevention

### Best Practices
1. **Regular Backups**: Backup databases and data
2. **Health Checks**: Monitor service health
3. **Logging**: Enable comprehensive logging
4. **Testing**: Test workflows before production
5. **Documentation**: Keep documentation updated

### Monitoring
- Set up alerts for critical failures
- Monitor resource usage
- Track error rates
- Review logs regularly

