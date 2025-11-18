"""Utility functions for the UI"""

import streamlit as st
from src.pipelines import DataLoader, TaxiTripPreprocessor
from src.workflows.experiment_pipeline import experiment_pipeline


def run_experiment_from_ui(
    data_source: str,
    adapter_type: str,
    eps: float,
    min_samples: int,
    max_samples: int,
    use_minio: bool,
    coordinate_type: str = "pickup",
):
    """Run experiment and return results with coordinates and labels"""
    try:
        with st.spinner("Running experiment..."):
            # Load data and extract coordinates (needed for visualization)
            if use_minio:
                df = DataLoader.load_data(data_source)
            else:
                df = DataLoader.load_from_file(data_source)
            
            if max_samples and len(df) > max_samples:
                df = df.sample(max_samples, random_state=42)
            
            # Extract coordinates (only 2D: pickup or dropoff)
            coords = TaxiTripPreprocessor.extract_coordinates(
                df, coordinate_type=coordinate_type, use_location_ids=True
            )
            coords, valid_mask = TaxiTripPreprocessor.filter_valid_coordinates(coords)
            
            # Run clustering to get labels for visualization
            from src.adapters import SklearnAdapter, SklearnParallelAdapter
            
            if adapter_type == "sklearn":
                adapter = SklearnAdapter()
            else:
                adapter = SklearnParallelAdapter()
            
            labels = adapter.fit_predict(coords, eps=eps, min_samples=min_samples)
            
            # Run full experiment pipeline (for logging to MLflow and PostgreSQL)
            # This will run clustering again internally, but that's okay for logging
            result = experiment_pipeline(
                data_source=data_source,
                adapter_type=adapter_type,
                eps=eps,
                min_samples=min_samples,
                coordinate_type=coordinate_type,
                use_location_ids=True,
                max_samples=max_samples,
                use_minio=use_minio,
            )
            
            # Add labels and coordinates to result for visualization
            result["labels"] = labels.tolist()
            
            return {
                "result": result,
                "coordinates": coords,
                "labels": labels,
                "success": True,
            }
    except Exception as e:
        import traceback
        error_msg = f"{str(e)}\n\n{traceback.format_exc()}"
        return {
            "result": None,
            "coordinates": None,
            "labels": None,
            "success": False,
            "error": error_msg,
        }

