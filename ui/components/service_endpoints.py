"""Service endpoints display component"""

import streamlit as st
from src.config import settings


def get_service_endpoints():
    """Get service endpoint information"""
    return {
        "Prefect UI": {
            "url": "http://localhost:4200",
            "api_url": settings.prefect_api_url,
            "status": "Check manually",
        },
        "MLflow UI": {
            "url": settings.mlflow_tracking_uri,
            "api_url": f"{settings.mlflow_tracking_uri}/api",
            "status": "Check manually",
        },
        "PostgreSQL": {
            "host": settings.postgres_host,
            "port": settings.postgres_port,
            "database": settings.postgres_db,
            "url": f"postgresql://{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}",
            "status": "Check manually",
        },
        "MinIO Console": {
            "url": f"http://{settings.minio_endpoint.replace(':9000', ':9001')}",
            "api_url": f"http://{settings.minio_endpoint}",
            "bucket": settings.minio_bucket_name,
            "status": "Check manually",
        },
        "Grafana": {
            "url": "http://localhost:3000",
            "status": "Check manually",
        },
        "Prometheus": {
            "url": "http://localhost:9090",
            "status": "Check manually",
        },
        "Jaeger UI": {
            "url": "http://localhost:16686",
            "status": "Check manually",
        },
    }


def render_service_endpoints_tab():
    """Render the service endpoints tab"""
    st.header("Service Endpoints & Configuration")
    
    endpoints = get_service_endpoints()
    
    for service_name, info in endpoints.items():
        with st.expander(f"🔗 {service_name}", expanded=False):
            st.markdown(f"**Service:** {service_name}")
            
            if "url" in info:
                st.markdown(f"**URL:** [{info['url']}]({info['url']})")
            
            if "api_url" in info:
                st.markdown(f"**API URL:** `{info['api_url']}`")
            
            for key, value in info.items():
                if key not in ["url", "api_url", "status"]:
                    st.markdown(f"**{key.replace('_', ' ').title()}:** `{value}`")
            
            st.markdown(f"**Status:** {info.get('status', 'Unknown')}")
    
    st.markdown("---")
    st.subheader("Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Prefect")
        st.json({
            "API URL": settings.prefect_api_url,
        })
    
    with col2:
        st.markdown("### MLflow")
        st.json({
            "Tracking URI": settings.mlflow_tracking_uri,
            "S3 Endpoint": settings.mlflow_s3_endpoint_url,
            "Experiment": settings.experiment_name,
        })
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("### PostgreSQL")
        st.json({
            "Host": settings.postgres_host,
            "Port": settings.postgres_port,
            "Database": settings.postgres_db,
        })
    
    with col4:
        st.markdown("### MinIO")
        st.json({
            "Endpoint": settings.minio_endpoint,
            "Bucket": settings.minio_bucket_name,
        })

