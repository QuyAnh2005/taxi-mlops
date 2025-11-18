"""Results display component"""

import numpy as np
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium
from ui.components.map_visualization import create_map_with_clusters


def render_results_display(result, coordinates, labels):
    """Render experiment results and visualization"""
    # Show experiment info
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Experiment ID", result.get("experiment_id", "N/A")[:8] + "...")
    
    with col2:
        st.metric("Adapter", result.get("adapter_type", "N/A"))
    
    with col3:
        metrics = result.get("metrics", {})
        st.metric("Clusters", metrics.get("n_clusters", 0))
    
    with col4:
        st.metric("Noise Points", metrics.get("n_noise", 0))
    
    # Show parameters and metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Parameters")
        params = result.get("parameters", {})
        st.json(params)
    
    with col2:
        st.subheader("Metrics")
        metrics = result.get("metrics", {})
        st.json(metrics)
    
    # Show map visualization
    if coordinates is not None and labels is not None:
        st.subheader("🗺️ Map Visualization")
        
        show_original = st.checkbox("Show Original Points", value=False)
        
        # Show all points (optimized with marker clustering)
        total_points = len(coordinates)
        coords_to_show = coordinates
        labels_to_show = labels
        
        st.info(
            f"📊 Showing all {total_points:,} points | "
            f"🎨 **Each color** = a different DBSCAN cluster (colors don't mix!) | "
            f"💡 **Numbers** = count of points grouped within same DBSCAN cluster | "
            f"🔍 **Zoom in** to see individual points | "
            f"🎛️ **Use layer control** (top-right) to toggle clusters on/off"
        )
        
        map_obj = create_map_with_clusters(
            coords_to_show, labels_to_show, show_original=show_original
        )
        
        st_folium(map_obj, width=1200, height=600)
        
        # Cluster statistics (using all data, not just displayed)
        st.subheader("📊 Cluster Statistics")
        
        unique_labels = np.unique(labels)
        n_clusters = len(unique_labels) - (1 if -1 in unique_labels else 0)
        n_noise = np.sum(labels == -1)
        
        cluster_stats = []
        for label in unique_labels:
            if label != -1:
                cluster_size = np.sum(labels == label)
                cluster_stats.append({
                    "Cluster": int(label),
                    "Size": int(cluster_size),
                    "Percentage": f"{100 * cluster_size / len(labels):.2f}%",
                })
        
        if cluster_stats:
            st.dataframe(pd.DataFrame(cluster_stats), width='stretch')
    else:
        st.info("Run an experiment to see map visualization")

