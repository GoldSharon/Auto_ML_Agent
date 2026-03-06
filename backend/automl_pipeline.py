# automl_pipeline.py
from pathlib import Path
from datetime import datetime
from data_pre_processor import canonicalize_columns
import pandas as pd
from core.models import InputConfiguration, ProcessingType, LearningType
from intelligent_data_analyzer import IntelligentDataAnalyzer
from intelligent_data_processor import DataPrepAgent
from sklearn.model_selection import train_test_split
from model_registry import run_train, evaluate
import joblib
import json 
import os
import logging
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def select_best_model(trained_models, evaluation_scores, learning_type):
    """Select best model based on primary metric."""
    metric_map = {
        LearningType.CLASSIFICATION: ('f1', 'max'),
        LearningType.REGRESSION: ('r2', 'max'),
        LearningType.CLUSTERING: ('silhouette', 'max')
    }
    
    primary_metric, direction = metric_map.get(learning_type, ('f1', 'max'))
    
    best_score = float('-inf') if direction == 'max' else float('inf')
    best_model_name = None
    
    for model_name, scores in evaluation_scores.items():
        score = scores.get(primary_metric, float('-inf') if direction == 'max' else float('inf'))
        
        if direction == 'max' and score > best_score:
            best_score = score
            best_model_name = model_name
        elif direction == 'min' and score < best_score:
            best_score = score
            best_model_name = model_name
    
    logger.info(f"Best model: {best_model_name} ({primary_metric}: {best_score:.4f})")
    
    return best_model_name, trained_models[best_model_name]


def preprocess_train(ipc: InputConfiguration, df: pd.DataFrame):
    """
    Preprocess data, train models, and evaluate.
    
    Args:
        ipc: Input configuration
        df: Raw input DataFrame
        
    Returns:
        dict: {
            'trained_models': dict of trained models,
            'evaluation_scores': dict of evaluation scores,
            'best_model_name': str,
            'best_model': model object,
            'data_prep': DataPrepAgent instance,
            'X_train': preprocessed training features,
            'y_train': preprocessed training target,
            'X_test': preprocessed test features,
            'y_test': preprocessed test target
        }
    """
    logger.info("Starting preprocess_train pipeline")
    logger.info(f"Input shape: {df.shape}")
    
    # Step 1: Analyze data
    logger.info("Step 1: Analyzing data")
    ida = IntelligentDataAnalyzer(ipc)
    report, pre_processing_config = ida.analyze_dataframe(df)

    # Save configs
    preprocess_path = os.path.join(ipc.output_folder, "preprocessing_config.json")
    report_path = os.path.join(ipc.output_folder, "report.json")

    with open(preprocess_path, "w") as f:
        json.dump(pre_processing_config, f, indent=4)

    with open(report_path, "w") as f:
        json.dump(report.to_dict(), f, indent=3)

    logger.info(f"Analysis saved to {report_path}")

    # Step 2: Split data
    logger.info("Step 2: Splitting data")
    stratify = df[ipc.target_column] if ipc.learning_type == LearningType.CLASSIFICATION else None
    
    train_df, test_df = train_test_split(
        df,
        test_size=ipc.test_size,
        random_state=42,
        stratify=stratify
    )
    
    logger.info(f"Train: {train_df.shape}, Test: {test_df.shape}")

    # Step 3: Preprocess training data
    logger.info("Step 3: Preprocessing training data")
    data_prep = DataPrepAgent(ipc, train_df)
    X_train, y_train = data_prep.fit_transform(pre_processing_config)

    # Save training data
    paths_train = data_prep.save_processed_data(
        X_train,
        y_train,
        features_filepath=os.path.join(ipc.output_folder, 'X_train.csv'),
        target_filepath=os.path.join(ipc.output_folder, 'y_train.csv'),
        combined_filepath=os.path.join(ipc.output_folder, 'train_data.csv'),
        save_combined=True
    )
    logger.info(f"Training data saved: {paths_train}")

    # Step 4: Preprocess test data
    logger.info("Step 4: Preprocessing test data")
    X_test = data_prep.transform(test_df)
    y_test = data_prep.transform_target(test_df[ipc.target_column]) if ipc.target_column else None

    # Save test data
    paths_test = data_prep.save_processed_data(
        X_test,
        y_test,
        features_filepath=os.path.join(ipc.output_folder, 'X_test.csv'),
        target_filepath=os.path.join(ipc.output_folder, 'y_test.csv'),
        combined_filepath=os.path.join(ipc.output_folder, 'test_data.csv'),
        save_combined=True
    )
    logger.info(f"Test data saved: {paths_test}")

    # Step 5: Train models
    logger.info("Step 5: Training models")
    trained_models = run_train(ipc, X_train, y_train)
    logger.info(f"Trained {len(trained_models)} models")

    # Step 6: Evaluate on test set
    logger.info("Step 6: Evaluating models on test set")
    
    # Filter out invalid test samples
    if y_test is not None:
        valid_mask = y_test != -1
        X_test_valid = X_test[valid_mask]
        y_test_valid = y_test[valid_mask]
        
        dropped = (~valid_mask).sum()
        if dropped > 0:
            logger.warning(f"Dropped {dropped} test samples with invalid targets")
    else:
        X_test_valid = X_test
        y_test_valid = None
    
    # Evaluate all models
    evaluation_scores = evaluate(trained_models, X_test_valid, y_test_valid, ipc.learning_type)
    
    # Save evaluation results
    eval_path = os.path.join(ipc.output_folder, "evaluation_scores.json")
    with open(eval_path, "w") as f:
        json.dump(evaluation_scores, f, indent=4)
    logger.info(f"Evaluation saved to {eval_path}")

    # Step 7: Select best model
    logger.info("Step 7: Selecting best model")
    best_model_name, best_model = select_best_model(
        trained_models, 
        evaluation_scores, 
        ipc.learning_type
    )

    # Step 8: Save artifacts
    logger.info("Step 8: Saving artifacts")
    
    # Save preprocessing agent
    joblib.dump(data_prep, os.path.join(ipc.output_folder, "data_prep.pkl"))
    
    # Save best model
    joblib.dump(best_model, os.path.join(ipc.output_folder, "best_model.pkl"))
    
    # Save all trained models
    models_dir = os.path.join(ipc.output_folder, "models")
    os.makedirs(models_dir, exist_ok=True)
    for name, model in trained_models.items():
        joblib.dump(model, os.path.join(models_dir, f"{name}_model.pkl"))
    
    # Save configuration
    joblib.dump(ipc, os.path.join(ipc.output_folder, "ipc.pkl"))
    
    # Save preprocessing report
    report_dict = data_prep.get_report()
    with open(os.path.join(ipc.output_folder, "preprocessing_report.json"), "w") as f:
        json.dump(report_dict, f, indent=4)

    logger.info(f"Pipeline complete. All artifacts saved to {ipc.output_folder}")

    return {
        'trained_models': trained_models,
        'evaluation_scores': evaluation_scores,
        'best_model_name': best_model_name,
        'best_model': best_model,
        'data_prep': data_prep,
        'X_train': X_train,
        'y_train': y_train,
        'X_test': X_test,
        'y_test': y_test
    }


def train(ipc: InputConfiguration, df: pd.DataFrame):
    """
    Train models on raw data with basic preprocessing.
    
    This mode performs:
    1. Basic preprocessing (categorical encoding, missing value removal)
    2. Train-test split
    3. Model training
    4. Evaluation
    
    Args:
        ipc: Input configuration
        df: Raw DataFrame (should contain both features and target)
        
    Returns:
        dict: {
            'trained_models': dict of trained models,
            'evaluation_scores': dict of evaluation scores,
            'best_model_name': str,
            'best_model': model object
        }
    """
    logger.info("Starting TRAINING_ONLY pipeline with basic preprocessing")
    logger.info(f"Input shape: {df.shape}")
    
    # Step 1: Basic preprocessing
    logger.info("Step 1: Basic preprocessing")
    
    # Separate features and target
    if ipc.target_column and ipc.target_column in df.columns:
        X = df.drop(columns=[ipc.target_column])
        y = df[ipc.target_column]
    else:
        raise ValueError("Target column required for TRAINING_ONLY mode")
    
    # Remove rows with missing target values
    valid_mask = y.notna()
    X = X[valid_mask]
    y = y[valid_mask]
    logger.info(f"Removed {(~valid_mask).sum()} rows with missing target values")
    
    # Handle categorical variables - convert to numeric using one-hot encoding
    categorical_cols = X.select_dtypes(include=['object', 'category']).columns.tolist()
    if categorical_cols:
        logger.info(f"Converting {len(categorical_cols)} categorical columns")
        X = pd.get_dummies(X, columns=categorical_cols, drop_first=True)
    
    # Handle missing values in features - simple median/mode imputation
    numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    for col in numeric_cols:
        if X[col].isnull().any():
            X[col].fillna(X[col].median(), inplace=True)
    
    # Remove any remaining rows with NaN values
    valid_mask = X.notna().all(axis=1)
    X = X[valid_mask]
    y = y[valid_mask]
    logger.info(f"Removed {(~valid_mask).sum()} rows with missing feature values")
    logger.info(f"Preprocessed data shape: {X.shape}")
    
    # Step 2: Train-test split
    logger.info("Step 2: Train-test split")
    stratify = y if ipc.learning_type == LearningType.CLASSIFICATION else None
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=ipc.test_size,
        random_state=42,
        stratify=stratify
    )
    logger.info(f"Train: {X_train.shape}, Test: {X_test.shape}")
    
    # Save preprocessed data
    os.makedirs(ipc.output_folder, exist_ok=True)
    X_train.to_csv(os.path.join(ipc.output_folder, 'X_train.csv'), index=False)
    pd.DataFrame(y_train).to_csv(os.path.join(ipc.output_folder, 'y_train.csv'), index=False)
    X_test.to_csv(os.path.join(ipc.output_folder, 'X_test.csv'), index=False)
    pd.DataFrame(y_test).to_csv(os.path.join(ipc.output_folder, 'y_test.csv'), index=False)
    logger.info("Preprocessed data saved")
    
    # Step 3: Train models
    logger.info("Step 3: Training models")
    trained_models = run_train(ipc, X_train, y_train)
    logger.info(f"Trained {len(trained_models)} models")
    
    # Step 4: Evaluate models
    logger.info("Step 4: Evaluating models")
    evaluation_scores = evaluate(trained_models, X_test, y_test, ipc.learning_type)
    
    # Save evaluation results
    eval_path = os.path.join(ipc.output_folder, "evaluation_scores.json")
    with open(eval_path, "w") as f:
        json.dump(evaluation_scores, f, indent=4)
    logger.info(f"Evaluation saved to {eval_path}")
    
    # Step 5: Select best model
    logger.info("Step 5: Selecting best model")
    best_model_name, best_model = select_best_model(
        trained_models, 
        evaluation_scores, 
        ipc.learning_type
    )
    
    # Step 6: Save artifacts
    logger.info("Step 6: Saving artifacts")
    
    # Save best model
    joblib.dump(best_model, os.path.join(ipc.output_folder, "best_model.pkl"))
    
    # Save all trained models
    models_dir = os.path.join(ipc.output_folder, "models")
    os.makedirs(models_dir, exist_ok=True)
    for name, model in trained_models.items():
        joblib.dump(model, os.path.join(models_dir, f"{name}_model.pkl"))
    
    # Save configuration
    joblib.dump(ipc, os.path.join(ipc.output_folder, "ipc.pkl"))
    
    logger.info(f"Training complete. All artifacts saved to {ipc.output_folder}")
    
    return {
        'trained_models': trained_models,
        'evaluation_scores': evaluation_scores,
        'best_model_name': best_model_name,
        'best_model': best_model,
        'X_train': X_train,
        'y_train': y_train,
        'X_test': X_test,
        'y_test': y_test
    }
