# config.py
import os

# Project paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')
BOUNDARIES_DIR = os.path.join(DATA_DIR, 'boundaries')
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs')

# File paths
NDVI_2024_PATH = os.path.join(RAW_DATA_DIR, '2024_NDVI.tif')
DISTRICTS_SHP = os.path.join(BOUNDARIES_DIR, 'karnataka_districts.shp')
TALUKS_SHP = os.path.join(BOUNDARIES_DIR, 'karnataka_taluks.shp')

# Model parameters
RANDOM_STATE = 42
N_ESTIMATORS = 100
TEST_SIZE = 0.2

# Map settings
CROP_NAMES = {
    1: "Paddy (Rice)",
    2: "Ragi (Finger Millet)", 
    3: "Groundnut / Maize",
    4: "Fallow / Barren Land"
}

COLOR_MAP = {
    1: '#1b9e77',  # Green
    2: '#d95f02',  # Orange
    3: '#7570b3',  # Purple
    4: '#e7298a'   # Pink
}