# scripts/05_visualization.py
import sys
import os
# Ensure project root is on sys.path for imports
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
import matplotlib.pyplot as plt
import rasterio
import geopandas as gpd
import numpy as np
import pandas as pd
from config import *

def create_enhanced_map(prediction_path, output_map_path):
    """Create publication-quality crop map"""
    
    print("🎨 Creating enhanced visualization...")
    
    # Load prediction data
    with rasterio.open(prediction_path) as src:
        prediction_data = src.read(1)
        bounds = src.bounds
        extent = [bounds.left, bounds.right, bounds.bottom, bounds.top]
    
    # Create figure
    fig, ax = plt.subplots(1, 1, figsize=(15, 12))
    
    # Create custom colormap
    from matplotlib.colors import ListedColormap
    colors = [COLOR_MAP.get(i, '#FFFFFF') for i in range(1, 5)]
    cmap = ListedColormap(colors)
    
    # Plot prediction data (skip background 0 values)
    plot_data = np.ma.masked_where(prediction_data == 0, prediction_data)
    im = ax.imshow(plot_data, extent=extent, cmap=cmap, alpha=0.8, interpolation='nearest')
    
    # Add grid
    ax.grid(True, alpha=0.3)
    ax.set_axisbelow(True)
    
    # Add scale bar (simplified)
    from matplotlib_scalebar.scalebar import ScaleBar
    ax.add_artist(ScaleBar(1, location='lower left', box_alpha=0.8))
    
    # Create legend
    legend_patches = []
    for cluster_id, crop_name in CROP_NAMES.items():
        legend_patches.append(
            plt.Rectangle((0, 0), 1, 1, fc=COLOR_MAP[cluster_id], label=crop_name)
        )
    
    ax.legend(handles=legend_patches, loc='upper right', framealpha=0.9)
    
    # Labels and title
    ax.set_title('Tumkur District - Crop Classification 2025', fontsize=16, fontweight='bold')
    ax.set_xlabel('Longitude', fontsize=12)
    ax.set_ylabel('Latitude', fontsize=12)
    
    # Add north arrow
    x, y, arrow_length = 0.95, 0.95, 0.1
    ax.annotate('N', xy=(x, y), xytext=(x, y-arrow_length),
                arrowprops=dict(facecolor='black', width=5, headwidth=15),
                ha='center', va='center', fontsize=20,
                xycoords=ax.transAxes)
    
    plt.tight_layout()
    
    # Save high-quality output
    os.makedirs(os.path.dirname(output_map_path), exist_ok=True)
    plt.savefig(output_map_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()
    
    print(f"💾 Map saved: {output_map_path}")

def create_pie_chart(district_stats_path):
    """Create crop distribution pie chart"""
    
    if os.path.exists(district_stats_path):
        df = pd.read_csv(district_stats_path)
        
        # Aggregate by crop type
        crop_summary = df.groupby('Crop_Type')['Area_ha'].sum().sort_values(ascending=False)
        
        # Create pie chart
        plt.figure(figsize=(10, 8))
        colors = [COLOR_MAP.get(i, '#CCCCCC') for i in range(1, len(crop_summary)+1)]
        
        wedges, texts, autotexts = plt.pie(crop_summary.values, 
                                          labels=crop_summary.index,
                                          colors=colors,
                                          autopct='%1.1f%%',
                                          startangle=90)
        
        # Enhance text
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        plt.title('Crop Distribution - Tumkur District 2025', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        pie_chart_path = os.path.join(OUTPUT_DIR, 'maps', 'crop_distribution_pie.png')
        plt.savefig(pie_chart_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"📊 Pie chart saved: {pie_chart_path}")

if __name__ == "__main__":
    prediction_path = os.path.join(OUTPUT_DIR, 'predictions', 'tumkur_2025_prediction.tif')
    output_map_path = os.path.join(OUTPUT_DIR, 'maps', 'enhanced_crop_map_2025.png')
    
    create_enhanced_map(prediction_path, output_map_path)
    
    # Create pie chart if data available
    district_stats_path = os.path.join(OUTPUT_DIR, 'reports', 'districtwise_crop_area_2025.csv')
    create_pie_chart(district_stats_path)