# scripts/03_prediction_mapping.py
import sys
import os
# Ensure project root is on sys.path for imports
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
import rasterio
import numpy as np
import pandas as pd
import joblib
from config import *

def create_prediction_map():
    """Create crop prediction map for entire area"""
    
    print("🗺️ Creating prediction map...")
    
    # Load model
    model_path = os.path.join(BASE_DIR, 'models', 'crop_classifier.pkl')
    model = joblib.load(model_path)
    
    # Load NDVI data for prediction
    with rasterio.open(NDVI_2024_PATH) as src:
        ndvi_data = src.read()
        profile = src.profile
        transform = src.transform
        bounds = src.bounds
    
    # Reshape for prediction
    original_shape = ndvi_data[0].shape
    ndvi_flat = ndvi_data.reshape(ndvi_data.shape[0], -1).T
    
    # Create DataFrame with features
    df_pred = pd.DataFrame(ndvi_flat, 
                          columns=[f"NDVI_Band_{i+1}" for i in range(ndvi_data.shape[0])])
    
    # Add engineered features
    df_pred['NDVI_Mean'] = df_pred[['NDVI_Band_1', 'NDVI_Band_2', 'NDVI_Band_3']].mean(axis=1)
    df_pred['NDVI_Std'] = df_pred[['NDVI_Band_1', 'NDVI_Band_2', 'NDVI_Band_3']].std(axis=1)
    df_pred['NDVI_Range'] = df_pred[['NDVI_Band_1', 'NDVI_Band_2', 'NDVI_Band_3']].max(axis=1) - \
                           df_pred[['NDVI_Band_1', 'NDVI_Band_2', 'NDVI_Band_3']].min(axis=1)
    
    # Handle NaN values
    df_pred = df_pred.fillna(0)
    
    # Make predictions
    print("🤖 Making predictions...")
    predictions = model.predict(df_pred)
    
    # Reshape back to original dimensions
    prediction_map = predictions.reshape(original_shape)
    
    # Update profile for output
    profile.update({
        'dtype': rasterio.uint8,
        'count': 1,
        'compress': 'lzw'
    })
    
    # Save prediction map
    output_path = os.path.join(OUTPUT_DIR, 'predictions', 'tumkur_2025_prediction.tif')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(prediction_map.astype(rasterio.uint8), 1)
    
    print(f"💾 Prediction map saved: {output_path}")
    
    # Print class distribution
    unique, counts = np.unique(prediction_map, return_counts=True)
    print("\n📊 Prediction Distribution:")
    for cls, count in zip(unique, counts):
        if cls > 0:  # Skip background
            area_ha = (count * abs(transform[0] * transform[4])) / 10000
            print(f"  {CROP_NAMES.get(cls, f'Class {cls}')}: {count:,} pixels ({area_ha:,.1f} ha)")
    
    return output_path

if __name__ == "__main__":
    prediction_path = create_prediction_map()