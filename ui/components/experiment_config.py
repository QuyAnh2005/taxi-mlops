"""Experiment configuration sidebar component"""

import json
import streamlit as st
from src.storage import PostgresClient


def render_experiment_config_sidebar():
    """Render the experiment configuration sidebar"""
    st.header("⚙️ Experiment Configuration")
    
    data_source = st.text_input(
        "Data Source",
        value="data/yellow_tripdata_2025-09.parquet",
        help="Path to data file or MinIO object name",
    )
    
    use_minio = st.checkbox("Use MinIO", value=False)
    
    adapter_type = st.selectbox(
        "Adapter Type",
        ["sklearn", "sklearn_parallel"],
        index=0,
    )
    
    coordinate_type = st.selectbox(
        "Coordinate Type",
        ["pickup", "dropoff"],
        index=0,
        help="Type of coordinates to extract. Only 2D coordinates (pickup or dropoff) are used for clustering.",
    )
    
    eps = st.slider(
        "EPS (neighborhood radius)",
        min_value=0.001,
        max_value=1.0,
        value=0.01,
        step=0.001,
        format="%.3f",
    )
    
    min_samples = st.slider(
        "Min Samples",
        min_value=2,
        max_value=50,
        value=5,
    )
    
    max_samples = st.number_input(
        "Max Samples (0 = all)",
        min_value=0,
        max_value=100000,
        value=5000,
        step=100,
    )
    
    if max_samples == 0:
        max_samples = None
    
    run_button = st.button("🚀 Run Experiment", type="primary", use_container_width=False)
    
    st.markdown("---")
    st.subheader("📊 Load Previous Experiment")
    
    # Load from PostgreSQL
    try:
        postgres_client = PostgresClient()
        experiments = postgres_client.list_experiments()
        
        if experiments:
            experiment_ids = [exp["experiment_id"] for exp in experiments[:20]]  # Limit to 20
            selected_exp_id = st.selectbox(
                "Select Experiment ID",
                [""] + experiment_ids,
            )
            
            if selected_exp_id and st.button("Load Experiment"):
                exp_data = postgres_client.get_experiment(selected_exp_id)
                if exp_data:
                    # Parse JSON fields
                    if isinstance(exp_data.get("parameters"), str):
                        exp_data["parameters"] = json.loads(exp_data["parameters"])
                    if isinstance(exp_data.get("metrics"), str):
                        exp_data["metrics"] = json.loads(exp_data["metrics"])
                    
                    st.session_state.experiment_results = exp_data
                    st.success(f"Loaded experiment: {selected_exp_id}")
                    st.json({
                        "Experiment ID": exp_data["experiment_id"],
                        "Adapter Type": exp_data["adapter_type"],
                        "Parameters": exp_data["parameters"],
                        "Metrics": exp_data["metrics"],
                    })
                    
                    # Note: We can't load coordinates/labels from database
                    # User needs to run a new experiment to see map
                    st.info("⚠️ Note: Map visualization requires running a new experiment with the same parameters.")
        else:
            st.info("No experiments found in database")
    except Exception as e:
        st.warning(f"Could not load experiments: {e}")
    
    return {
        "data_source": data_source,
        "use_minio": use_minio,
        "adapter_type": adapter_type,
        "coordinate_type": coordinate_type,
        "eps": eps,
        "min_samples": min_samples,
        "max_samples": max_samples,
        "run_button": run_button,
    }

