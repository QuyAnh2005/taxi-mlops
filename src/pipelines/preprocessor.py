"""Data preprocessing utilities for taxi trip data"""

from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd

from .exceptions import DataValidationError

try:
    import geopandas as gpd
    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False


class TaxiTripPreprocessor:
    """Preprocessor for NYC taxi trip data."""
    
    # Class variable to cache the taxi zone lookup table
    _taxi_zone_lookup: dict[int, tuple[float, float]] | None = None
    _taxi_zone_path: Path | None = None

    @staticmethod
    def extract_coordinates(
        df: pd.DataFrame,
        coordinate_type: str = "pickup",
        use_location_ids: bool = True,
    ) -> np.ndarray:
        """
        Extract coordinates from taxi trip DataFrame.

        This function handles NYC yellow taxi trip data format with location IDs.
        It can extract coordinates from:
        - Actual lat/lon columns if they exist
        - Location IDs (PULocationID/DOLocationID) converted to approximate coordinates

        Args:
            df: DataFrame containing taxi trip data.
            coordinate_type: Type of coordinates to extract. Options:
                - "pickup": Extract pickup coordinates (2D: lat, lon)
                - "dropoff": Extract dropoff coordinates (2D: lat, lon)
                - "both": Extract both (4D: pickup_lat, pickup_lon, dropoff_lat, dropoff_lon)
                Note: For DBSCAN clustering, only use "pickup" or "dropoff" (2D coordinates).
                "both" creates 4D features which are not suitable for spatial clustering.
            use_location_ids: If True and no lat/lon columns exist, use location IDs
                as approximate coordinates. If False, raises error if coordinates not found.

        Returns:
            Array of coordinates.
            - For "pickup" or "dropoff": shape (n_samples, 2) with [lat, lon]
            - For "both": shape (n_samples, 4) with [pickup_lat, pickup_lon, dropoff_lat, dropoff_lon]

        Raises:
            DataValidationError: If coordinate extraction fails.
        """
        coordinate_type = coordinate_type.lower()

        # Check for actual coordinate columns
        has_pickup_lat = any(
            col.lower() in ["pickup_latitude", "pickup_lat", "pulocation_lat"]
            for col in df.columns
        )
        has_pickup_lon = any(
            col.lower() in ["pickup_longitude", "pickup_lon", "pulocation_lon"]
            for col in df.columns
        )
        has_dropoff_lat = any(
            col.lower() in ["dropoff_latitude", "dropoff_lat", "dolocation_lat"]
            for col in df.columns
        )
        has_dropoff_lon = any(
            col.lower() in ["dropoff_longitude", "dropoff_lon", "dolocation_lon"]
            for col in df.columns
        )

        # Extract coordinates based on type
        if coordinate_type == "pickup":
            if has_pickup_lat and has_pickup_lon:
                # Use actual coordinates
                lat_col = next(
                    col
                    for col in df.columns
                    if col.lower() in ["pickup_latitude", "pickup_lat", "pulocation_lat"]
                )
                lon_col = next(
                    col
                    for col in df.columns
                    if col.lower() in ["pickup_longitude", "pickup_lon", "pulocation_lon"]
                )
                coords = df[[lat_col, lon_col]].values
            elif "PULocationID" in df.columns and use_location_ids:
                # Convert location IDs to approximate coordinates
                location_ids = df["PULocationID"].values
                coords = TaxiTripPreprocessor._location_ids_to_coordinates(location_ids, "pickup")
            else:
                raise DataValidationError(
                    "Pickup coordinates not found. Set use_location_ids=True to use location IDs."
                )

        elif coordinate_type == "dropoff":
            if has_dropoff_lat and has_dropoff_lon:
                # Use actual coordinates
                lat_col = next(
                    col
                    for col in df.columns
                    if col.lower() in ["dropoff_latitude", "dropoff_lat", "dolocation_lat"]
                )
                lon_col = next(
                    col
                    for col in df.columns
                    if col.lower() in ["dropoff_longitude", "dropoff_lon", "dolocation_lon"]
                )
                coords = df[[lat_col, lon_col]].values
            elif "DOLocationID" in df.columns and use_location_ids:
                # Convert location IDs to approximate coordinates
                location_ids = df["DOLocationID"].values
                coords = TaxiTripPreprocessor._location_ids_to_coordinates(location_ids, "dropoff")
            else:
                raise DataValidationError(
                    "Dropoff coordinates not found. Set use_location_ids=True to use location IDs."
                )

        elif coordinate_type == "both":
            # Extract both pickup and dropoff coordinates
            coords_list = []

            if has_pickup_lat and has_pickup_lon:
                lat_col = next(
                    col
                    for col in df.columns
                    if col.lower() in ["pickup_latitude", "pickup_lat", "pulocation_lat"]
                )
                lon_col = next(
                    col
                    for col in df.columns
                    if col.lower() in ["pickup_longitude", "pickup_lon", "pulocation_lon"]
                )
                coords_list.extend([df[lat_col].values, df[lon_col].values])
            elif "PULocationID" in df.columns and use_location_ids:
                location_ids = df["PULocationID"].values
                pickup_coords = TaxiTripPreprocessor._location_ids_to_coordinates(
                    location_ids, "pickup"
                )
                coords_list.extend([pickup_coords[:, 0], pickup_coords[:, 1]])
            else:
                raise DataValidationError("Pickup coordinates not found.")

            if has_dropoff_lat and has_dropoff_lon:
                lat_col = next(
                    col
                    for col in df.columns
                    if col.lower() in ["dropoff_latitude", "dropoff_lat", "dolocation_lat"]
                )
                lon_col = next(
                    col
                    for col in df.columns
                    if col.lower() in ["dropoff_longitude", "dropoff_lon", "dolocation_lon"]
                )
                coords_list.extend([df[lat_col].values, df[lon_col].values])
            elif "DOLocationID" in df.columns and use_location_ids:
                location_ids = df["DOLocationID"].values
                dropoff_coords = TaxiTripPreprocessor._location_ids_to_coordinates(
                    location_ids, "dropoff"
                )
                coords_list.extend([dropoff_coords[:, 0], dropoff_coords[:, 1]])
            else:
                raise DataValidationError("Dropoff coordinates not found.")

            coords = np.column_stack(coords_list)

        else:
            raise DataValidationError(
                f"Invalid coordinate_type: {coordinate_type}. Must be 'pickup', 'dropoff', or 'both'."
            )

        # Remove NaN and infinite values
        valid_mask = np.isfinite(coords).all(axis=1)
        coords = coords[valid_mask]

        if len(coords) == 0:
            raise DataValidationError(
                "No valid coordinates found after filtering NaN/infinite values."
            )

        return coords

    @staticmethod
    def _load_taxi_zone_lookup(shapefile_path: str | Path | None = None) -> dict[int, tuple[float, float]]:
        """
        Load taxi zone lookup table from shapefile.

        Args:
            shapefile_path: Path to taxi zones shapefile. If None, tries to find it
                in the project's data/taxi_zones directory.

        Returns:
            Dictionary mapping location ID to (latitude, longitude) tuple.

        Raises:
            DataValidationError: If shapefile cannot be loaded or geopandas is not available.
        """
        if not GEOPANDAS_AVAILABLE:
            raise DataValidationError(
                "geopandas is required to load taxi zone data. "
                "Please install it: pip install geopandas"
            )

        # Use cached lookup if available and path matches
        if TaxiTripPreprocessor._taxi_zone_lookup is not None:
            if shapefile_path is None or (
                TaxiTripPreprocessor._taxi_zone_path is not None
                and Path(shapefile_path).resolve() == TaxiTripPreprocessor._taxi_zone_path.resolve()
            ):
                return TaxiTripPreprocessor._taxi_zone_lookup

        # Determine shapefile path
        if shapefile_path is None:
            # Try to find shapefile relative to project root
            project_root = Path(__file__).parent.parent.parent
            shapefile_path = project_root / "data" / "taxi_zones" / "taxi_zones.shp"
        else:
            shapefile_path = Path(shapefile_path)

        if not shapefile_path.exists():
            raise DataValidationError(
                f"Taxi zone shapefile not found at {shapefile_path}. "
                "Please ensure the shapefile exists or provide the correct path."
            )

        # Load shapefile
        try:
            gdf = gpd.read_file(str(shapefile_path))
        except Exception as e:
            raise DataValidationError(
                f"Failed to load shapefile at {shapefile_path}: {e}"
            ) from e

        # Find LocationID column (prioritize exact match, then case-insensitive)
        location_id_col = None
        # First, try exact match (case-sensitive)
        if 'LocationID' in gdf.columns:
            location_id_col = 'LocationID'
        elif 'locationid' in [col.lower() for col in gdf.columns]:
            # Find case-insensitive match
            for col in gdf.columns:
                if col.lower() == 'locationid':
                    location_id_col = col
                    break
        elif 'location_id' in [col.lower() for col in gdf.columns]:
            for col in gdf.columns:
                if col.lower() == 'location_id':
                    location_id_col = col
                    break

        if location_id_col is None:
            raise DataValidationError(
                f"Could not find LocationID column in shapefile. "
                f"Available columns: {list(gdf.columns)}"
            )
        
        # Verify the column contains numeric data
        if not pd.api.types.is_numeric_dtype(gdf[location_id_col]):
            raise DataValidationError(
                f"LocationID column '{location_id_col}' does not contain numeric data. "
                f"Sample values: {gdf[location_id_col].head().tolist()}"
            )

        # Calculate centroids from geometry
        if 'geometry' not in gdf.columns:
            raise DataValidationError(
                "Shapefile does not contain geometry column."
            )

        # Calculate centroids in the original CRS (more accurate for area calculations)
        # Then transform the centroid points to WGS84 for lat/lon
        original_crs = gdf.crs
        if original_crs is None:
            # If no CRS, calculate directly (assume already in reasonable coordinates)
            centroids = gdf.geometry.centroid
            gdf['lat'] = centroids.y
            gdf['lon'] = centroids.x
        elif original_crs.to_string() == 'EPSG:4326':
            # Already in WGS84, but calculate centroid in a projected CRS for accuracy
            # Project to NY State Plane for centroid calculation, then back to WGS84
            gdf_projected = gdf.to_crs('EPSG:2263')
            centroids_projected = gdf_projected.geometry.centroid
            centroids_wgs84 = centroids_projected.to_crs('EPSG:4326')
            gdf['lat'] = centroids_wgs84.y
            gdf['lon'] = centroids_wgs84.x
        else:
            # Calculate centroid in original CRS, then transform to WGS84
            centroids_original = gdf.geometry.centroid
            centroids_wgs84 = centroids_original.to_crs('EPSG:4326')
            gdf['lat'] = centroids_wgs84.y
            gdf['lon'] = centroids_wgs84.x

        # Create lookup dictionary
        lookup = {}
        for _, row in gdf.iterrows():
            loc_id = int(row[location_id_col])
            lat = float(row['lat'])
            lon = float(row['lon'])
            lookup[loc_id] = (lat, lon)

        # Cache the lookup table
        TaxiTripPreprocessor._taxi_zone_lookup = lookup
        TaxiTripPreprocessor._taxi_zone_path = shapefile_path.resolve()

        return lookup

    @staticmethod
    def _location_ids_to_coordinates(
        location_ids: np.ndarray, location_type: str
    ) -> np.ndarray:
        """
        Convert NYC taxi zone location IDs to exact coordinates from shapefile.

        Uses the actual taxi zone shapefile to get exact zone centroids.
        Falls back to approximation if shapefile is not available.

        Args:
            location_ids: Array of location IDs.
            location_type: Type of location ("pickup" or "dropoff") - not used but kept for compatibility.

        Returns:
            Array of shape (n_samples, 2) with [latitude, longitude].
        """
        # Try to load actual taxi zone data
        try:
            lookup = TaxiTripPreprocessor._load_taxi_zone_lookup()
            
            # Map location IDs to coordinates
            coords = []
            missing_ids = []
            
            for loc_id in location_ids:
                loc_id_int = int(loc_id)
                if loc_id_int in lookup:
                    lat, lon = lookup[loc_id_int]
                    coords.append([lat, lon])
                else:
                    missing_ids.append(loc_id_int)
                    # For missing IDs, use NaN (will be filtered later)
                    coords.append([np.nan, np.nan])
            
            if missing_ids:
                unique_missing = sorted(set(missing_ids))
                print(
                    f"Warning: {len(unique_missing)} location IDs not found in taxi zone data: "
                    f"{unique_missing[:10]}{'...' if len(unique_missing) > 10 else ''}"
                )
            
            coords_array = np.array(coords)
            
            # Filter out NaN values (missing location IDs)
            valid_mask = np.isfinite(coords_array).all(axis=1)
            if not valid_mask.all():
                print(
                    f"Warning: {np.sum(~valid_mask)} coordinates are invalid (missing location IDs) "
                    "and will be filtered out."
                )
            
            return coords_array
            
        except (DataValidationError, ImportError) as e:
            # Fallback to approximation if shapefile loading fails
            print(
                f"Warning: Could not load taxi zone shapefile ({e}). "
                "Falling back to approximate coordinates."
            )
            return TaxiTripPreprocessor._location_ids_to_coordinates_approximate(
                location_ids, location_type
            )

    @staticmethod
    def _location_ids_to_coordinates_approximate(
        location_ids: np.ndarray, location_type: str
    ) -> np.ndarray:
        """
        Convert NYC taxi zone location IDs to approximate coordinates (fallback method).

        This is a simplified approximation used when the shapefile is not available.
        For production use, ensure the taxi zone shapefile is available.

        Args:
            location_ids: Array of location IDs.
            location_type: Type of location ("pickup" or "dropoff").

        Returns:
            Array of shape (n_samples, 2) with [latitude, longitude].
        """
        unique_ids = np.unique(location_ids)
        id_to_lat = {}
        id_to_lon = {}

        # NYC taxi zones are roughly distributed across Manhattan, Brooklyn, Queens, Bronx, Staten Island
        # Create a more realistic distribution based on location ID ranges
        for loc_id in unique_ids:
            # Use deterministic hash for reproducibility
            hash_val = hash(int(loc_id)) % (2**31)

            # Map to NYC coordinate space
            if loc_id <= 68:
                # Manhattan zones
                lat = 40.7 + (hash_val % 100) / 1000.0
                lon = -74.0 + (hash_val % 100) / 1000.0
            elif loc_id <= 150:
                # Brooklyn/Queens zones
                lat = 40.6 + (hash_val % 200) / 1000.0
                lon = -74.0 + (hash_val % 300) / 1000.0
            elif loc_id <= 200:
                # Bronx zones
                lat = 40.8 + (hash_val % 100) / 1000.0
                lon = -73.9 + (hash_val % 200) / 1000.0
            else:
                # Staten Island and other zones
                lat = 40.5 + (hash_val % 200) / 1000.0
                lon = -74.2 + (hash_val % 200) / 1000.0

            id_to_lat[loc_id] = lat
            id_to_lon[loc_id] = lon

        # Map all location IDs to coordinates
        lats = np.array([id_to_lat[loc_id] for loc_id in location_ids])
        lons = np.array([id_to_lon[loc_id] for loc_id in location_ids])

        # Add small deterministic noise based on location ID to avoid exact duplicates
        noise_scale = 0.0005  # ~50 meters
        for i, loc_id in enumerate(location_ids):
            np.random.seed(int(loc_id) + 1000)
            lats[i] += np.random.normal(0, noise_scale)
            lons[i] += np.random.normal(0, noise_scale)

        return np.column_stack([lats, lons])

    @staticmethod
    def filter_valid_coordinates(coords: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Filter out invalid coordinates (NaN, infinite, out of bounds).

        Args:
            coords: Array of coordinates of shape (n_samples, 2) with [lat, lon].

        Returns:
            Tuple of (filtered_coords, valid_mask).
        """
        # Check for NaN and infinite values
        valid_mask = np.isfinite(coords).all(axis=1)

        # Check for reasonable NYC bounds
        # Latitude: 40.4 to 41.0 (NYC area)
        # Longitude: -74.5 to -73.5 (NYC area)
        if coords.shape[1] >= 2:
            lat_mask = (coords[:, 0] >= 40.4) & (coords[:, 0] <= 41.0)
            lon_mask = (coords[:, 1] >= -74.5) & (coords[:, 1] <= -73.5)
            valid_mask = valid_mask & lat_mask & lon_mask

        filtered_coords = coords[valid_mask]

        return filtered_coords, valid_mask

