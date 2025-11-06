# scripts/04_district_analysis.py
import sys
import os
# Ensure project root is on sys.path for imports
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
import geopandas as gpd
import rasterio
from rasterio import features
import pandas as pd
import numpy as np
from config import *

def load_administrative_data():
    """Load district and taluk boundaries"""
    
    print("🗺️ Loading administrative boundaries...")
    
    try:
        districts = gpd.read_file(DISTRICTS_SHP)
        taluks = gpd.read_file(TALUKS_SHP)
        print(f"✅ Loaded {len(districts)} districts and {len(taluks)} taluks")
        return districts, taluks
    except Exception as e:
        print(f"❌ Error loading boundaries: {e}")
        # Create dummy data for demonstration
        return None, None

def calculate_zonal_statistics(prediction_path, administrative_gdf, name_column, output_name):
    """Calculate crop areas by administrative boundaries"""
    
    print(f"📊 Calculating zonal statistics for {output_name}...")
    
    with rasterio.open(prediction_path) as src:
        raster_data = src.read(1)
        transform = src.transform
        crs = src.crs
        
        results = []
        
        for idx, row in administrative_gdf.iterrows():
            # Ensure geometries are in same CRS
            geometry = row.geometry
            if geometry is not None:
                # Create mask for current administrative unit
                mask = features.geometry_mask(
                    [geometry],
                    out_shape=raster_data.shape,
                    transform=transform,
                    invert=True
                )
                
                masked_data = raster_data[mask]
                
                if len(masked_data) > 0:
                    unique, counts = np.unique(masked_data, return_counts=True)
                    
                    # Calculate pixel area in hectares
                    pixel_area_ha = abs(transform[0] * transform[4]) / 10000
                    
                    for cluster_id, count in zip(unique, counts):
                        if cluster_id > 0:  # Skip background
                            area_ha = count * pixel_area_ha
                            
                            results.append({
                                'Region_Type': output_name,
                                'Region_Name': row[name_column],
                                'Cluster_ID': cluster_id,
                                'Crop_Type': CROP_NAMES.get(cluster_id, f'Class {cluster_id}'),
                                'Area_ha': area_ha,
                                'Pixel_Count': count,
                                'Percentage': (count / len(masked_data)) * 100
                            })
        
        return pd.DataFrame(results)

def generate_reports(prediction_path):
    """Generate comprehensive reports"""
    
    districts, taluks = load_administrative_data()
    
    if districts is not None:
        # District-wise analysis
        district_stats = calculate_zonal_statistics(
            prediction_path, districts, 'DISTRICT', 'District'
        )
        
        # Taluk-wise analysis
        taluk_stats = calculate_zonal_statistics(
            prediction_path, taluks, 'TALUK', 'Taluk'
        )
        
        # Save reports
        district_stats.to_csv(
            os.path.join(OUTPUT_DIR, 'reports', 'districtwise_crop_area_2025.csv'), 
            index=False
        )
        taluk_stats.to_csv(
            os.path.join(OUTPUT_DIR, 'reports', 'talukwise_crop_area_2025.csv'), 
            index=False
        )
        
        print("📈 Summary Statistics:")
        print(f"📊 Total crop area analyzed: {district_stats['Area_ha'].sum():,.1f} ha")
        
        return district_stats, taluk_stats
    else:
        print("⚠️ Using demo mode - no shapefiles available")
        return None, None

if __name__ == "__main__":
    prediction_path = os.path.join(OUTPUT_DIR, 'predictions', 'tumkur_2025_prediction.tif')
    district_stats, taluk_stats = generate_reports(prediction_path)