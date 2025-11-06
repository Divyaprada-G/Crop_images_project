# run_pipeline.py
import os
import subprocess
import sys
from datetime import datetime

def create_dummy_data():
    """Create dummy data files for testing if real data isn't available"""
    print("📁 Creating dummy data structure for testing...")
    
    # Create dummy NDVI file (you'll replace this with real data)
    dummy_ndvi_path = "data/raw/2024_NDVI.tif"
    os.makedirs(os.path.dirname(dummy_ndvi_path), exist_ok=True)
    
    # If NDVI file is missing or invalid, create a small synthetic raster
    needs_synthetic = not os.path.exists(dummy_ndvi_path) or os.path.getsize(dummy_ndvi_path) == 0
    if needs_synthetic:
        print("⚠️  Please add your actual NDVI TIFF file to: data/raw/2024_NDVI.tif")
        print("   Creating a small synthetic NDVI raster for demo...")
        try:
            import numpy as np
            import rasterio
            from rasterio.transform import from_origin
            width, height, count = 100, 100, 3
            transform = from_origin(77.0, 13.5, 0.001, 0.001)
            profile = {
                'driver': 'GTiff',
                'dtype': 'float32',
                'width': width,
                'height': height,
                'count': count,
                'crs': 'EPSG:4326',
                'transform': transform,
                'compress': 'lzw'
            }
            data = np.clip(np.random.normal(loc=0.4, scale=0.2, size=(count, height, width)).astype('float32'), -1.0, 1.0)
            with rasterio.open(dummy_ndvi_path, 'w', **profile) as dst:
                dst.write(data)
        except Exception as e:
            print(f"❌ Failed to create synthetic NDVI: {e}")
    
    # Create dummy boundaries directory
    boundaries_dir = "data/boundaries"
    os.makedirs(boundaries_dir, exist_ok=True)
    
    print("✅ Project structure created!")

def run_script(script_name):
    """Run a Python script and capture output"""
    print(f"\n{'='*60}")
    print(f"🚀 RUNNING: {script_name}")
    print(f"{'='*60}")
    
    script_path = os.path.join('scripts', script_name)
    
    if not os.path.exists(script_path):
        print(f"❌ Script not found: {script_path}")
        return False
    
    try:
        # Run the script and capture output in real-time
        result = subprocess.run(
            [sys.executable, script_path], 
            capture_output=True, 
            text=True, 
            cwd='.'  # Run from project root
        )
        
        if result.returncode == 0:
            print(f"✅ {script_name} completed successfully!")
            
            # Print last few lines of output
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                print("📋 Output preview:")
                for line in lines[-5:]:  # Last 5 lines
                    if line.strip():
                        print(f"   {line}")
            
            return True
        else:
            print(f"❌ {script_name} failed with exit code: {result.returncode}")
            if result.stderr:
                print("🔴 Error output:")
                for line in result.stderr.strip().split('\n')[-10:]:  # Last 10 error lines
                    if line.strip():
                        print(f"   {line}")
            return False
            
    except Exception as e:
        print(f"❌ Error running {script_name}: {e}")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'rasterio', 'geopandas', 'numpy', 'pandas', 
        'matplotlib', 'sklearn', 'folium', 'joblib'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"   ❌ {package}")
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {missing_packages}")
        print("   Install them using:")
        print("   pip install " + " ".join(missing_packages))
        return False
    
    print("✅ All dependencies are available!")
    return True

def main():
    """Run the complete pipeline"""
    
    print("🌾 ENHANCED CROP CLASSIFICATION PIPELINE")
    print("=" * 50)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Create project structure
    create_dummy_data()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first!")
        return
    
    # Define the pipeline steps
    scripts = [
        '01_data_preprocessing.py',
        '02_model_training.py', 
        '03_prediction_mapping.py',
        '04_district_analysis.py',
        '05_visualization.py',
        '06_dashboard.py'
    ]
    
    # Track success/failure
    successful_steps = []
    failed_steps = []
    
    # Run each script in sequence
    for script in scripts:
        if run_script(script):
            successful_steps.append(script)
        else:
            failed_steps.append(script)
            print(f"\n🛑 Pipeline stopped due to failure in: {script}")
            break
    
    # Final summary
    print(f"\n{'='*50}")
    print("📊 PIPELINE EXECUTION SUMMARY")
    print(f"{'='*50}")
    print(f"✅ Successful steps: {len(successful_steps)}/{len(scripts)}")
    print(f"❌ Failed steps: {len(failed_steps)}/{len(scripts)}")
    print(f"⏰ Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not failed_steps:
        print(f"\n🎉 PIPELINE COMPLETED SUCCESSFULLY!")
        
        # Show output files
        print("\n📁 OUTPUT FILES GENERATED:")
        output_files = [
            "data/processed/training_data.csv",
            "models/crop_classifier.pkl", 
            "outputs/predictions/tumkur_2025_prediction.tif",
            "outputs/reports/districtwise_crop_area_2025.csv",
            "outputs/maps/enhanced_crop_map_2025.png",
            "outputs/maps/interactive_crop_map.html"
        ]
        
        for output_file in output_files:
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file) / 1024  # KB
                print(f"  ✅ {output_file} ({file_size:.1f} KB)")
            else:
                print(f"  ❌ {output_file} (missing)")
    else:
        print(f"\n💡 TROUBLESHOOTING TIPS:")
        print("   1. Check if your NDVI data file exists: data/raw/2024_NDVI.tif")
        print("   2. Verify all dependencies are installed")
        print("   3. Check the error messages above")
        print("   4. Try running individual scripts to isolate the issue")

if __name__ == "__main__":
    main()