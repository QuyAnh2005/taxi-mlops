"""Streamlit UI for Taxi MLOps Platform"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
from ui.components.service_endpoints import render_service_endpoints_tab
from ui.components.experiment_config import render_experiment_config_sidebar
from ui.components.results_display import render_results_display
from ui.utils import run_experiment_from_ui

# Page configuration
st.set_page_config(
    page_title="Taxi MLOps Dashboard",
    page_icon="🚕",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if "experiment_results" not in st.session_state:
    st.session_state.experiment_results = None
if "coordinates" not in st.session_state:
    st.session_state.coordinates = None
if "labels" not in st.session_state:
    st.session_state.labels = None


def main():
    st.title("🚕 Taxi MLOps Dashboard")
    st.markdown("---")
    
    # Create tabs
    tab1, tab2 = st.tabs(["📡 Service Endpoints", "🗺️ Experiment Results"])
    
    with tab1:
        render_service_endpoints_tab()
    
    with tab2:
        st.header("Experiment Results & Visualization")
        
        # Sidebar for experiment configuration
        with st.sidebar:
            config = render_experiment_config_sidebar()
        
        # Main content area
        if config["run_button"]:
            result = run_experiment_from_ui(
                data_source=config["data_source"],
                adapter_type=config["adapter_type"],
                eps=config["eps"],
                min_samples=config["min_samples"],
                max_samples=config["max_samples"],
                use_minio=config["use_minio"],
                coordinate_type=config["coordinate_type"],
            )
            
            if result["success"]:
                st.session_state.experiment_results = result["result"]
                st.session_state.coordinates = result["coordinates"]
                st.session_state.labels = result["labels"]
                st.success("✅ Experiment completed successfully!")
            else:
                st.error(f"❌ Experiment failed: {result.get('error', 'Unknown error')}")
        
        # Display results
        if st.session_state.experiment_results is not None:
            render_results_display(
                st.session_state.experiment_results,
                st.session_state.coordinates,
                st.session_state.labels,
            )
        else:
            st.info("👈 Configure and run an experiment from the sidebar to see results")


if __name__ == "__main__":
    main()

