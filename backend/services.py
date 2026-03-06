from pathlib import Path
from datetime import datetime
from data_pre_processor import canonicalize_columns
from dataclasses import asdict
import pandas as pd
from core.models import InputConfiguration, ProcessingType
from intelligent_data_analyzer import IntelligentDataAnalyzer
from intelligent_data_processor import DataPrepAgent
from sklearn.model_selection import train_test_split
from automl_pipeline import preprocess_train, train
import joblib
import json 
import os
from core.models import LearningType,ProcessingType


def folder_check():
    BASE_DIR = Path(__file__).parent
    output_folder = BASE_DIR / "Output"
    output_folder.mkdir(parents=True, exist_ok=True)
    return output_folder


def create_new_project_folder(name: str):
    output_folder = folder_check()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"{name}_{timestamp}"
    project_dir = output_folder / folder_name
    project_dir.mkdir(exist_ok=True)
    return str(project_dir)  # Convert Path to string


def restore_session(output_folder: str):
    """Restore saved session."""
    ipc = joblib.load(os.path.join(output_folder, "ipc.pkl"))  # Fixed: use parameter, not ipc.output_folder
    data_prep = joblib.load(os.path.join(output_folder, "data_prep.pkl"))
    best_model = joblib.load(os.path.join(output_folder, "best_model.pkl"))
    return ipc, data_prep, best_model


def predict_new_data(df: pd.DataFrame, output_folder: str):
    """Make predictions on new data."""
    # Load artifacts
    ipc, data_prep, model = restore_session(output_folder)

    # Transform raw features
    X_processed = data_prep.transform(df)

    # Predict
    y_pred = model.predict(X_processed)

    # Inverse transform to original format
    y_final = data_prep.inverse_transform_target(y_pred)

    # Create results DataFrame
    results = df.copy()
    results['prediction'] = y_final
    
    # Save predictions
    pred_path = os.path.join(output_folder, "predictions.csv")
    results.to_csv(pred_path, index=False)

    return results


def run_automl(df: pd.DataFrame, ipc: InputConfiguration):
    """Main AutoML entry point."""
    
    # Canonicalize column names
    df, col_map = canonicalize_columns(df)

    print(df.columns)
    
    if ipc.processing_type == ProcessingType.PREPROCESS_TRAIN:
        # Full pipeline: preprocess + train + evaluate
        result = preprocess_train(ipc, df)
        return result  # Returns dict with trained_models, evaluation_scores, etc.
    
    elif ipc.processing_type == ProcessingType.TRAINING_ONLY:
        # Train only on preprocessed data
        result = train(ipc, df)
        return result  # Returns dict with trained_models, evaluation_scores, etc.
    
    else:
        raise ValueError(f"Unknown processing type: {ipc.processing_type}")