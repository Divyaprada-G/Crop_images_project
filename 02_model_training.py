# scripts/02_model_training.py
import sys
import os
# Ensure project root is on sys.path for imports
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
import joblib
from config import *

def train_crop_classifier():
    """Train the crop classification model"""
    print("🤖 Step 2: Training crop classification model...")
    
    training_data_path = os.path.join(PROCESSED_DATA_DIR, 'training_data.csv')
    
    if not os.path.exists(training_data_path):
        print(f"❌ Training data not found: {training_data_path}")
        print("💡 Run 01_data_preprocessing.py first!")
        return None, None
    
    try:
        # Load prepared data
        df = pd.read_csv(training_data_path)
        print(f"📊 Loaded {df.shape[0]} training samples")
        
        # Prepare features and target
        feature_columns = ['NDVI_Band_1', 'NDVI_Band_2', 'NDVI_Band_3', 
                          'NDVI_Mean', 'NDVI_Std', 'NDVI_Range']
        
        X = df[feature_columns]
        y = df['Cluster']
        
        print(f"🎯 Classes distribution: {y.value_counts().to_dict()}")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
        )
        
        # Train Random Forest model
        model = RandomForestClassifier(
            n_estimators=N_ESTIMATORS,
            random_state=RANDOM_STATE,
            max_depth=10,
            min_samples_split=5,
            n_jobs=-1
        )
        
        # Cross-validation
        print("📊 Performing cross-validation...")
        cv_scores = cross_val_score(model, X_train, y_train, cv=5)
        print(f"   Cross-validation scores: {cv_scores}")
        print(f"   Mean CV accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
        
        # Train final model
        print("🏋️ Training final model...")
        model.fit(X_train, y_train)
        
        # Performance
        train_score = model.score(X_train, y_train)
        test_score = model.score(X_test, y_test)
        
        print(f"🎯 Training accuracy: {train_score:.3f}")
        print(f"🎯 Test accuracy: {test_score:.3f}")
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': feature_columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\n🔍 Feature Importance:")
        for _, row in feature_importance.iterrows():
            print(f"   {row['feature']}: {row['importance']:.3f}")
        
        return model, feature_columns
        
    except Exception as e:
        print(f"❌ Error training model: {e}")
        return None, None

if __name__ == "__main__":
    model, features = train_crop_classifier()
    if model is not None:
        os.makedirs(os.path.join(BASE_DIR, 'models'), exist_ok=True)
        model_path = os.path.join(BASE_DIR, 'models', 'crop_classifier.pkl')
        joblib.dump(model, model_path)
        print(f"💾 Model saved to: {model_path}")
    else:
        print("❌ Model training failed!")