"""Map visualization component for displaying DBSCAN clusters with improved colors"""

import numpy as np
import folium
from folium.plugins import MarkerCluster
import matplotlib.colors as mcolors


def get_distinct_colors(n_colors):
    """
    Generate highly distinct colors for clusters
    Uses a combination of predefined distinct colors and interpolation
    """
    # Predefined highly distinct colors (from ColorBrewer and custom)
    base_colors = [
        '#e6194b',  # Red
        '#3cb44b',  # Green
        '#ffe119',  # Yellow
        '#4363d8',  # Blue
        '#f58231',  # Orange
        '#911eb4',  # Purple
        '#46f0f0',  # Cyan
        '#f032e6',  # Magenta
        '#bcf60c',  # Lime
        '#fabebe',  # Pink
        '#008080',  # Teal
        '#e6beff',  # Lavender
        '#9a6324',  # Brown
        '#fffac8',  # Beige
        '#800000',  # Maroon
        '#aaffc3',  # Mint
        '#808000',  # Olive
        '#ffd8b1',  # Apricot
        '#000075',  # Navy
        '#808080',  # Grey
        '#ff6b6b',  # Coral
        '#4ecdc4',  # Turquoise
        '#45b7d1',  # Sky Blue
        '#f9ca24',  # Golden
        '#6c5ce7',  # Indigo
        '#fd79a8',  # Hot Pink
        '#fdcb6e',  # Mustard
        '#00b894',  # Mint Green
        '#d63031',  # Dark Red
        '#0984e3',  # Royal Blue
    ]

    if n_colors <= len(base_colors):
        return base_colors[:n_colors]
    else:
        # If we need more colors, cycle through the base colors
        # and adjust brightness/saturation
        colors = []
        for i in range(n_colors):
            base_idx = i % len(base_colors)
            color = base_colors[base_idx]

            # For repeated colors, adjust brightness
            if i >= len(base_colors):
                # Convert to RGB, adjust, convert back
                rgb = mcolors.hex2color(color)
                # Darken by 30%
                rgb = tuple(max(0, c * 0.7) for c in rgb)
                color = mcolors.rgb2hex(rgb)

            colors.append(color)
        return colors


def create_map_with_clusters(coords: np.ndarray, labels: np.ndarray, show_original: bool = False):
    """Create a Folium map showing clustered points with distinct colors and clear outlines"""
    # Calculate center of all points
    center_lat = np.mean(coords[:, 0])
    center_lon = np.mean(coords[:, 1])

    # Create base map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,  # Slightly zoomed out to see more clusters
        tiles="OpenStreetMap",
        prefer_canvas=True,  # Better performance
    )

    # Get unique cluster labels
    unique_labels = np.unique(labels)
    n_clusters = len(unique_labels) - (1 if -1 in unique_labels else 0)

    # Get distinct colors for clusters
    cluster_colors = get_distinct_colors(n_clusters)

    # Create color map
    color_map = {}
    cluster_idx = 0
    for label in sorted(unique_labels):
        if label == -1:
            color_map[label] = "#808080"  # Medium gray for noise (more visible)
        else:
            color_map[label] = cluster_colors[cluster_idx % len(cluster_colors)]
            cluster_idx += 1

    # Create a FeatureGroup for each DBSCAN cluster
    cluster_groups = {}
    for label in unique_labels:
        if label != -1:
            cluster_groups[label] = folium.FeatureGroup(
                name=f"Cluster {label} ({np.sum(labels == label)} points)",
                overlay=True,
                control=True,
                show=True,
            )

    # Create a separate group for noise points
    noise_count = np.sum(labels == -1)
    if -1 in unique_labels and noise_count > 0:
        noise_group = folium.FeatureGroup(
            name=f"Noise Points ({noise_count})",
            overlay=True,
            control=True,
            show=True,
        )

    # Add points to their respective groups
    # Use larger markers with thicker borders for better visibility
    for i, (lat, lon) in enumerate(coords):
        label = labels[i]
        fill_color = color_map.get(label, "#000000")

        if label == -1:
            # Noise points - smaller, gray, with distinctive X pattern
            marker = folium.CircleMarker(
                location=[lat, lon],
                radius=3,  # Smaller than clusters
                color='#404040',  # Dark gray border
                fill=True,
                fillColor='#808080',  # Medium gray fill
                fillOpacity=0.6,
                weight=1.5,  # Thinner border than clusters
                popup=f"<b>Noise Point</b><br>Index: {i}",
            )
            marker.add_to(noise_group)
        else:
            # Cluster points - larger with thick contrasting borders
            # Use white border for dark colors, black for light colors
            rgb = mcolors.hex2color(fill_color)
            brightness = (rgb[0] * 299 + rgb[1] * 587 + rgb[2] * 114) / 1000
            border_color = '#ffffff' if brightness < 0.5 else '#000000'

            marker = folium.CircleMarker(
                location=[lat, lon],
                radius=6,  # Larger markers
                color=border_color,  # Contrasting border
                fill=True,
                fillColor=fill_color,
                fillOpacity=0.85,  # More opaque
                weight=2.5,  # Thick border
                popup=f"<b>Cluster {label}</b><br>Point: {i}<br>Color: {fill_color}",
            )
            marker.add_to(cluster_groups[label])

    # Add all groups to the map
    for group in cluster_groups.values():
        group.add_to(m)

    if -1 in unique_labels and noise_count > 0:
        noise_group.add_to(m)

    # Add layer control - collapsed by default to avoid clutter
    folium.LayerControl(position='topright', collapsed=True).add_to(m)

    # Create compact legend with color samples - positioned on bottom-left to avoid layer control
    # Show top 8 clusters by size
    cluster_sizes = [(label, np.sum(labels == label)) for label in unique_labels if label != -1]
    cluster_sizes.sort(key=lambda x: x[1], reverse=True)
    top_clusters = cluster_sizes[:8]

    legend_items = []
    for label, count in top_clusters:
        color = color_map[label]
        legend_items.append(
            f'<div style="margin: 2px 0; display: flex; align-items: center;">'
            f'<span style="display:inline-block; width:16px; height:16px; '
            f'background-color:{color}; border:2px solid #000; border-radius:50%; '
            f'margin-right:6px; flex-shrink:0;"></span>'
            f'<span style="font-size:11px;"><b>C{label}</b>: {count} pts</span>'
            f'</div>'
        )

    if n_clusters > 8:
        legend_items.append(f'<div style="margin: 2px 0; font-size:10px; font-style: italic; color:#666;">+ {n_clusters - 8} more clusters</div>')

    legend_html = f"""
    <div style="position: fixed;
                bottom: 20px; left: 20px; width: 240px; max-height: 350px;
                background-color: rgba(255, 255, 255, 0.96); z-index:9999;
                font-size:12px; border:2px solid #2c3e50; border-radius:6px;
                padding: 12px; box-shadow: 0 3px 10px rgba(0,0,0,0.25);
                overflow-y: auto;">
        <div style="display: flex; align-items: center; margin-bottom: 8px; border-bottom: 2px solid #3498db; padding-bottom: 6px;">
            <span style="font-size: 18px; margin-right: 6px;">🗺️</span>
            <h4 style="margin: 0; color: #2c3e50; font-size: 14px;">DBSCAN Clusters</h4>
        </div>
        <div style="margin: 8px 0; padding: 6px; background-color: #f8f9fa; border-radius: 4px;">
            <div style="display: flex; justify-content: space-between; margin: 2px 0;">
                <span style="font-size:11px;"><b>📊 Clusters:</b></span>
                <span style="color: #3498db; font-weight: bold; font-size:12px;">{n_clusters}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin: 2px 0; align-items: center;">
                <span style="font-size:11px;">
                    <span style="display:inline-block; width:12px; height:12px; background-color:#808080; border:1px solid #404040; border-radius:50%; margin-right:4px; vertical-align:middle;"></span>
                    <b>Noise:</b>
                </span>
                <span style="color: #e74c3c; font-weight: bold; font-size:12px;">{noise_count}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin: 2px 0;">
                <span style="font-size:11px;"><b>📍 Points:</b></span>
                <span style="color: #27ae60; font-weight: bold; font-size:12px;">{len(labels):,}</span>
            </div>
        </div>
        <div style="margin: 8px 0;">
            <div style="font-size:11px; font-weight:bold; color: #34495e; margin-bottom: 4px;">Top Clusters:</div>
            {''.join(legend_items)}
        </div>
        <div style="font-size:10px; color: #7f8c8d; margin-top: 8px; padding-top: 6px; border-top: 1px solid #ddd;">
            <b>💡 Tips:</b> Click layer icon (↗️) to toggle clusters
        </div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    return m
