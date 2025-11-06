# scripts/01_data_preprocessing.py
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
from config import *

def prepare_training_data():
    """Load and prepare training data"""
    print("📊 Step 1: Preparing training data...")
    
    # Check if input file exists
    if not os.path.exists(NDVI_2024_PATH):
        print(f"❌ NDVI file not found: {NDVI_2024_PATH}")
        print("💡 Please add your NDVI TIFF file to the data/raw/ directory")
        return None, None
    
    try:
        # Load NDVI data
        with rasterio.open(NDVI_2024_PATH) as src:
            ndvi_data = src.read()
            profile = src.profile
            
            # For demo purposes, create synthetic clusters
            # In real scenario, you'd have actual cluster data
            height, width = ndvi_data.shape[1], ndvi_data.shape[2]
            clusters = np.random.choice([1, 2, 3, 4], size=(height, width))
        
        print(f"📐 Data dimensions: {ndvi_data.shape}")
        
        # Reshape and create DataFrame
        ndvi_flat = ndvi_data.reshape(ndvi_data.shape[0], -1).T
        df = pd.DataFrame(ndvi_flat, 
                         columns=[f"NDVI_Band_{i+1}" for i in range(ndvi_data.shape[0])])
        
        # Add cluster labels
        df['Cluster'] = clusters.flatten()
        
        # Remove background pixels (cluster = 0)
        df = df[df['Cluster'] > 0]
        
        # Add feature engineering
        df['NDVI_Mean'] = df[['NDVI_Band_1', 'NDVI_Band_2', 'NDVI_Band_3']].mean(axis=1)
        df['NDVI_Std'] = df[['NDVI_Band_1', 'NDVI_Band_2', 'NDVI_Band_3']].std(axis=1)
        df['NDVI_Range'] = df[['NDVI_Band_1', 'NDVI_Band_2', 'NDVI_Band_3']].max(axis=1) - \
                          df[['NDVI_Band_1', 'NDVI_Band_2', 'NDVI_Band_3']].min(axis=1)
        
        # Remove any remaining NaN values
        df = df.dropna()
        
        print(f"✅ Training data prepared: {df.shape[0]} samples, {df.shape[1]} features")
        return df, profile
        
    except Exception as e:
        print(f"❌ Error processing data: {e}")
        return None, None

if __name__ == "__main__":
    df, profile = prepare_training_data()
    if df is not None:
        os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
        df.to_csv(os.path.join(PROCESSED_DATA_DIR, 'training_data.csv'), index=False)
        print("💾 Training data saved to: data/processed/training_data.csv")
    else:
        print("❌ Data preprocessing failed!")