# scripts/06_dashboard.py
import sys
import os
# Ensure project root is on sys.path for imports
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import folium
import geopandas as gpd
import rasterio
import json
from config import *

def create_interactive_map(prediction_path):
    """Create interactive Folium map"""
    
    print("🌐 Creating interactive map...")
    
    # Get bounds from prediction raster
    with rasterio.open(prediction_path) as src:
        bounds = src.bounds
        transform = src.transform
    
    # Calculate center
    center_lat = (bounds.bottom + bounds.top) / 2
    center_lon = (bounds.left + bounds.right) / 2
    
    # Create base map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=10,
        tiles='OpenStreetMap'
    )
    
    # Add satellite imagery
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Satellite',
        overlay=False,
        control=True
    ).add_to(m)
    
    # Add district boundaries if available
    try:
        districts = gpd.read_file(DISTRICTS_SHP)
        
        # Filter for Tumkur district
        tumkur_district = districts[districts['DISTRICT'] == 'TUMKUR']
        
        folium.GeoJson(
            tumkur_district.to_json(),
            name='District Boundaries',
            style_function=lambda x: {
                'fillColor': 'none',
                'color': 'blue',
                'weight': 3,
                'fillOpacity': 0
            },
            tooltip=folium.GeoJsonTooltip(fields=['DISTRICT', 'TALUK'], aliases=['District:', 'Taluk:'])
        ).add_to(m)
    except Exception as e:
        print(f"⚠️ Could not load district boundaries: {e}")
    
    # Add legend
    legend_html = '''
    <div style="position: fixed; 
                top: 10px; left: 50px; width: 200px; height: auto; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
    <p><strong>🌾 Crop Legend</strong></p>
    '''
    
    for cluster_id, crop_name in CROP_NAMES.items():
        color = COLOR_MAP[cluster_id]
        legend_html += f'<p><i style="background:{color}; width:20px; height:20px; display:inline-block; margin-right:5px;"></i> {crop_name}</p>'
    
    legend_html += '</div>'
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Save map
    map_path = os.path.join(OUTPUT_DIR, 'maps', 'interactive_crop_map.html')
    os.makedirs(os.path.dirname(map_path), exist_ok=True)
    m.save(map_path)
    
    print(f"💾 Interactive map saved: {map_path}")
    print("📍 Open the HTML file in your browser to view the interactive map!")
    
    return map_path

if __name__ == "__main__":
    prediction_path = os.path.join(OUTPUT_DIR, 'predictions', 'tumkur_2025_prediction.tif')
    create_interactive_map(prediction_path)