"""
DataPrepAgent - Automated Data Preprocessing Agent (FIXED)
Supports: Classification, Regression, Clustering, Association Rules (Apriori)
Features: Proper fit/transform separation, prediction mode, no data leakage

CRITICAL FIXES:
1. transform() never drops rows
2. Separate transform_target() method
3. Prediction mode auto-detection
4. Safe feature engineering (no exec())
5. Proper separation of concerns
6. EXECUTION ORDER FIX: Feature engineering BEFORE outlier handling (prevents column mismatch)
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple, Literal
import json
import warnings
import os

from feature_engine.imputation import MeanMedianImputer, CategoricalImputer
from feature_engine.encoding import OneHotEncoder, CountFrequencyEncoder
from feature_engine.outliers import Winsorizer
from feature_engine.selection import DropConstantFeatures, DropDuplicateFeatures, DropCorrelatedFeatures
from feature_engine.transformation import LogTransformer, YeoJohnsonTransformer
from feature_engine.wrappers import SklearnTransformerWrapper
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from core.models import InputConfiguration, LearningType, MLType

warnings.filterwarnings('ignore')


class FeatureEngineeringEngine:
    """Safe feature engineering without exec()."""
    
    ALLOWED_OPERATIONS = {
        'divide': lambda df, a, b: df[a] / df[b].replace(0, np.nan),
        'multiply': lambda df, a, b: df[a] * df[b],
        'add': lambda df, a, b: df[a] + df[b],
        'subtract': lambda df, a, b: df[a] - df[b],
    }
    
    @staticmethod
    def create_feature(df: pd.DataFrame, config: Dict) -> pd.Series:
        """
        Safely create engineered features.
        
        Args:
            df: Input DataFrame
            config: Feature configuration with operation and source columns
            
        Returns:
            New feature as pandas Series
        """
        operation = config.get('operation')
        source_cols = config['source_columns']
        
        if operation not in FeatureEngineeringEngine.ALLOWED_OPERATIONS:
            raise ValueError(f"Operation '{operation}' not allowed. Use: {list(FeatureEngineeringEngine.ALLOWED_OPERATIONS.keys())}")
        
        if not all(col in df.columns for col in source_cols):
            missing = [col for col in source_cols if col not in df.columns]
            raise ValueError(f"Missing columns: {missing}")
        
        if len(source_cols) != 2:
            raise ValueError(f"Operations require exactly 2 columns, got {len(source_cols)}")
        
        result = FeatureEngineeringEngine.ALLOWED_OPERATIONS[operation](df, source_cols[0], source_cols[1])
        
        # Clean up inf and extreme values
        result = result.replace([np.inf, -np.inf], np.nan)
        
        return result


class TargetProcessor:
    """Handles all target variable preprocessing."""
    
    def __init__(self, learning_type: LearningType, verbose: bool = True):
        self.learning_type = learning_type
        self.verbose = verbose
        self.encoder = None
        self.winsorizer = None
        self.label_mapping = {}
        self._is_fitted = False
        
    def fit_transform(self, target: pd.Series, feature_indices: pd.Index) -> Tuple[pd.Series, pd.Index]:
        """
        Fit and transform target (TRAINING ONLY).
        May drop rows with missing/invalid targets.
        
        Returns:
            (transformed_target, valid_indices)
        """
        if self.verbose:
            print(f"\n[Target Preprocessing] Fitting and transforming target...")
        
        target = target.copy()
        original_len = len(target)
        
        # Remove missing values (ONLY during training)
        valid_mask = target.notna()
        target = target[valid_mask]
        valid_indices = feature_indices[valid_mask]
        
        dropped = original_len - len(target)
        if dropped > 0 and self.verbose:
            print(f"  • Removed {dropped} rows with missing target")
        
        # Classification: Encode categorical target
        if self.learning_type == LearningType.CLASSIFICATION:
            if target.dtype == 'object' or target.dtype.name == 'category':
                from sklearn.preprocessing import LabelEncoder
                self.encoder = LabelEncoder()
                target = pd.Series(
                    self.encoder.fit_transform(target),
                    index=target.index,
                    name=target.name
                )
                self.label_mapping = dict(enumerate(self.encoder.classes_))
                if self.verbose:
                    print(f"  • Encoded categorical target: {len(self.label_mapping)} classes")
        
        # Regression: Handle outliers
        elif self.learning_type == LearningType.REGRESSION:
            # Convert to numeric
            if target.dtype == 'object':
                target = pd.to_numeric(target, errors='coerce')
                valid_mask = target.notna()
                invalid_count = (~valid_mask).sum()
                
                if invalid_count > 0:
                    target = target[valid_mask]
                    valid_indices = valid_indices[valid_mask]
                    if self.verbose:
                        print(f"  • Removed {invalid_count} non-numeric target values")
            
            # Check for extreme outliers
            Q1 = target.quantile(0.25)
            Q3 = target.quantile(0.75)
            IQR = Q3 - Q1
            extreme_outliers = ((target < (Q1 - 3*IQR)) | (target > (Q3 + 3*IQR))).sum()
            
            if extreme_outliers > 0:
                if self.verbose:
                    print(f"  ⚠ Found {extreme_outliers} extreme outliers in target")
                
                # Apply winsorization
                target_df = pd.DataFrame({target.name or 'target': target})
                self.winsorizer = Winsorizer(
                    capping_method='iqr',
                    tail='both',
                    fold=3.0,
                    variables=[target.name or 'target']
                )
                target_transformed = self.winsorizer.fit_transform(target_df)
                target = target_transformed[target.name or 'target']
                
                if self.verbose:
                    print(f"  • Winsorized target (3×IQR method)")
                    print(f"  • Target range: [{target.min():.2f}, {target.max():.2f}]")

        
        self._is_fitted = True
        
        if self.verbose:
            print(f"  ✓ Target shape: {target.shape}")
            print(f"  ✓ Target dtype: {target.dtype}")
        
        return target, valid_indices
    
    def transform_target(self, target: pd.Series) -> pd.Series:
        """
        Transform target for validation/test (NEVER drops rows).
        
        For missing values:
        - Returns NaN (caller handles metrics filtering)
        - Never changes row count
        """
        if not self._is_fitted:
            raise ValueError("TargetProcessor must be fitted first")
        
        target = target.copy()
        
        # Classification: Encode (unknown labels → -1)
        if self.learning_type == LearningType.CLASSIFICATION and self.encoder is not None:
            try:
                # Handle unknown labels
                known_mask = target.isin(self.encoder.classes_)
                encoded = np.full(len(target), -1, dtype=int)
                encoded[known_mask] = self.encoder.transform(target[known_mask])
                
                target = pd.Series(encoded, index=target.index, name=target.name)
                
                unknown_count = (~known_mask).sum()
                if unknown_count > 0 and self.verbose:
                    print(f"  ⚠ {unknown_count} unknown labels encoded as -1")
                    
            except Exception as e:
                if self.verbose:
                    print(f"  ⚠ Encoding failed: {e}")
        
        # Regression: Convert and winsorize (preserving NaN)
        elif self.learning_type == LearningType.REGRESSION:
            if target.dtype == 'object':
                target = pd.to_numeric(target, errors='coerce')
            
            # Apply winsorization if fitted (NaN preserved)
            if self.winsorizer is not None:
                target_df = pd.DataFrame({target.name or 'target': target})
                target_transformed = self.winsorizer.transform(target_df)
                target = target_transformed[target.name or 'target']
        
        return target
    
    def inverse_transform(self, y_pred: np.ndarray) -> np.ndarray:
        """Inverse transform predictions."""
        if self.learning_type == LearningType.CLASSIFICATION and self.encoder is not None:
            # Filter out -1 (unknown) before inverse transform
            mask = y_pred != -1
            result = np.full(len(y_pred), 'UNKNOWN', dtype=object)
            result[mask] = self.encoder.inverse_transform(y_pred[mask])
            return result
        
        return y_pred


class DataPrepAgent:
    """
    Automated data preprocessing agent with proper fit/transform separation.
    
    Key Features:
    - Prediction mode auto-detection
    - Never drops rows in transform()
    - Separate target processing
    - Safe feature engineering (no exec())
    - FIXED: Feature engineering BEFORE outlier handling
    """

    def __init__(self, ipc: InputConfiguration, df: pd.DataFrame):
        """Initialize DataPrepAgent."""
        
        self.feature_df = df.drop(columns=[ipc.index_column], errors="ignore").copy()
        self.ml_type = ipc.ml_type
        self.learning_type = ipc.learning_type
        self.verbose = True
        
        # Target handling
        self.target_column_name = ipc.target_column
        if ipc.target_column and ipc.target_column in df.columns:
            self.original_target = df[ipc.target_column].copy()
            self.feature_df = self.feature_df.drop(columns=[ipc.target_column])
        else:
            self.original_target = None
        
        # Store original data
        self.original_df = self.feature_df.copy()
        
        # Transformers
        self.transformers = {}
        self.preprocessing_report = {}
        
        # Target processor
        self.target_processor = None
        if self.learning_type in [LearningType.REGRESSION, LearningType.CLASSIFICATION]:
            self.target_processor = TargetProcessor(self.learning_type, self.verbose)
        
        # Feature engineering storage (safe operations only)
        self.feature_engineering_configs = []
        
        # Fit status
        self._is_fitted = False
        
        if self.verbose:
            print(f"DataPrepAgent initialized:")
            print(f"  • Features shape: {self.feature_df.shape}")
            print(f"  • ML type: {self.ml_type.value}")
            print(f"  • Task type: {self.learning_type.value}")
            print(f"  • Has target: {self.original_target is not None}")

    def fit_transform(self, preprocessing_config: Dict) -> Tuple[pd.DataFrame, Optional[pd.Series]]:
        """
        Fit transformers on TRAINING data and apply transformations.
        MAY drop rows (e.g., missing target).
        
        NOTE: Feature engineering executes BEFORE outlier handling to ensure
        engineered features also receive outlier treatment. This prevents
        column count mismatches in transform().
        
        Returns:
            (preprocessed_features, preprocessed_target)
        """
        if self.verbose:
            print("\n" + "="*70)
            print(f"FITTING AND TRANSFORMING DATA - {self.learning_type.value}")
            print("="*70)
        
        self._validate_config(preprocessing_config)
        
        # Step -1: Preprocess target (may drop rows)
        target = None
        valid_indices = self.feature_df.index
        
        if self.target_processor and self.original_target is not None:
            target, valid_indices = self.target_processor.fit_transform(
                self.original_target, 
                self.feature_df.index
            )
            # Align features with valid target indices
            self.feature_df = self.feature_df.loc[valid_indices]
        
        # Step 0: Drop columns
        self._step_0_drop_columns(preprocessing_config)
        
        # Step 1: Handle missing values
        self._step_1_fit_transform_missing(preprocessing_config)
        
        # CRITICAL: Execute feature engineering BEFORE outliers
        # This ensures winsorizer is fitted on ALL columns (original + engineered)
        if self.learning_type != LearningType.APRIORI:
            self._step_3_feature_engineering(preprocessing_config)
        
        # Step 2: Handle outliers (AFTER feature engineering)
        if self.learning_type != LearningType.APRIORI:
            self._step_2_fit_transform_outliers(preprocessing_config)
        
        # Step 4: Encode categorical
        self._step_4_fit_transform_categorical(preprocessing_config)
        
        # Step 5: Transform features
        if self.learning_type in [LearningType.REGRESSION, LearningType.CLASSIFICATION]:
            self._step_5_fit_transform_features(preprocessing_config)
        
        # Step 6: Scale features
        if self.learning_type in [LearningType.REGRESSION, LearningType.CLASSIFICATION, LearningType.CLUSTERING]:
            self._step_6_fit_transform_scale(preprocessing_config)
        
        # Step 7: Feature selection
        self._step_7_fit_transform_feature_selection(preprocessing_config)
        
        # Step 8: Association-specific
        if self.learning_type == LearningType.APRIORI:
            self._step_8_association_preprocessing(preprocessing_config)

        self.feature_df = self._sanitize_column_names(self.feature_df)
        
        self._is_fitted = True
        self._generate_report(preprocessing_config, target)
        
        if self.verbose:
            print("\n" + "="*70)
            print("FIT_TRANSFORM COMPLETE")
            print("="*70)
            print(f"Final shape: {self.feature_df.shape}")
            if target is not None:
                print(f"Target shape: {target.shape}")
        
        return self.feature_df, target

    def transform(self, new_df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform new data (validation/test/production).
        
        CRITICAL RULES:
        - NEVER drops rows
        - NEVER modifies target
        - Steps must match fit_transform() order EXACTLY
        - Feature engineering BEFORE outlier handling (prevents column mismatch)
        
        Args:
            new_df: New features DataFrame
            
        Returns:
            Transformed features (same row count as input)
        """
        if not self._is_fitted:
            raise ValueError("Agent must be fitted first. Call fit_transform() on training data.")
        
        if self.verbose:
            print("\n" + "="*70)
            print(f"TRANSFORMING NEW DATA (PREDICTION MODE)")
            print("="*70)
            print(f"Input shape: {new_df.shape}")
        
        df = new_df.copy()
        
        # Remove target column if present
        if self.target_column_name and self.target_column_name in df.columns:
            df = df.drop(columns=[self.target_column_name])
        
        original_index = df.index
        original_len = len(df)
        
        # ==========================================
        # CRITICAL: MUST MATCH FIT_TRANSFORM ORDER
        # ==========================================
        
        # Step 0: Drop columns
        if 'dropped_columns' in self.transformers:
            cols = [col for col in self.transformers['dropped_columns'] if col in df.columns]
            if cols:
                df = df.drop(columns=cols)
        
        # Step 1: Imputation (handles NaN, doesn't drop rows)
        for key in ['numeric_imputer', 'categorical_imputer']:
            if key in self.transformers:
                try:
                    df = self.transformers[key].transform(df)
                except Exception as e:
                    if self.verbose:
                        print(f"  ⚠ {key} failed: {e}")
        
        # ==========================================
        # CRITICAL FIX: Feature engineering BEFORE outlier handling
        # This matches fit_transform() order and prevents column mismatch
        # ==========================================
        
        # Step 2: Feature engineering (BEFORE winsorization)
        if self.verbose and self.feature_engineering_configs:
            print(f"  • Applying {len(self.feature_engineering_configs)} feature engineering rules...")
        
        for config in self.feature_engineering_configs:
            try:
                new_feature = config['new_feature']
                if all(col in df.columns for col in config['source_columns']):
                    result = FeatureEngineeringEngine.create_feature(df, config)
                    # Handle inf/nan from division
                    result = result.replace([np.inf, -np.inf], np.nan)
                    df[new_feature] = result
                    if self.verbose:
                        print(f"    → Created: {new_feature}")
                else:
                    missing = [col for col in config['source_columns'] if col not in df.columns]
                    if self.verbose:
                        print(f"    ⚠ Skipped {new_feature}: missing {missing}")
            except Exception as e:
                if self.verbose:
                    print(f"  ⚠ Feature engineering failed for {config['new_feature']}: {e}")
        
        # CRITICAL: Fill NaN from feature engineering BEFORE transformations
        if df.isnull().any().any():
            nan_cols = df.columns[df.isnull().any()].tolist()
            if self.verbose:
                print(f"  • Imputing {len(nan_cols)} columns after feature engineering...")
            
            for col in nan_cols:
                if df[col].isnull().any():
                    # Use fitted imputer value if available
                    fill_value = None
                    
                    if 'numeric_imputer' in self.transformers:
                        imputer = self.transformers['numeric_imputer']
                        if hasattr(imputer, 'imputer_dict_') and col in imputer.imputer_dict_:
                            fill_value = imputer.imputer_dict_[col]
                    
                    # Fallback: median for numeric, mode for categorical
                    if fill_value is None:
                        if pd.api.types.is_numeric_dtype(df[col]):
                            fill_value = df[col].median()
                            if pd.isna(fill_value):
                                fill_value = 0
                        else:
                            fill_value = 'missing'
                    
                    df[col] = df[col].fillna(fill_value)
                    if self.verbose:
                        print(f"    → Filled {col} with {fill_value}")
        
        # Step 3: Outlier handling (AFTER feature engineering)
        if 'winsorizer' in self.transformers:
            try:
                df = self.transformers['winsorizer'].transform(df)
                if self.verbose:
                    print(f"  ✓ Winsorizer applied")
            except Exception as e:
                if self.verbose:
                    print(f"  ⚠ Winsorizer failed: {e}")


        
        # Step 4: Encoding (AFTER feature engineering)
        for key in ['onehot_encoder', 'frequency_encoder']:
            if key in self.transformers:
                try:
                    df = self.transformers[key].transform(df)
                except Exception as e:
                    if self.verbose:
                        print(f"  ⚠ {key} failed: {e}")
        
        # Step 5: Transformations (log, yeo-johnson)
        for key in ['log_transformer', 'yeo_johnson_transformer']:
            if key in self.transformers:
                try:
                    df = self.transformers[key].transform(df)
                except Exception as e:
                    if self.verbose:
                        print(f"  ⚠ {key} failed: {e}")
        
        # Step 6: Scaling
        if 'scaler' in self.transformers:
            try:
                df = self.transformers['scaler'].transform(df)
            except Exception as e:
                if self.verbose:
                    print(f"  ⚠ Scaler failed: {e}")
        
        # Step 7: Feature selection
        for key in ['constant_dropper', 'duplicate_dropper', 'correlation_dropper']:
            if key in self.transformers:
                try:
                    df = self.transformers[key].transform(df)
                except Exception as e:
                    if self.verbose:
                        print(f"  ⚠ {key} failed: {e}")
        
        # FINAL SAFETY: Check for any remaining NaN
        if df.isnull().any().any():
            nan_counts = df.isnull().sum()
            nan_cols = nan_counts[nan_counts > 0]
            
            if self.verbose:
                print(f"  ⚠ Found {len(nan_cols)} columns with NaN after all transformations")
            
            for col in nan_cols.index:
                if df[col].isnull().any():
                    if pd.api.types.is_numeric_dtype(df[col]):
                        fill_value = 0
                    else:
                        fill_value = 'missing'
                    
                    df[col] = df[col].fillna(fill_value)
                    if self.verbose:
                        print(f"    → Emergency fill {col} with {fill_value}")
        
        # CRITICAL CHECK: Row count must match
        if len(df) != original_len:
            raise RuntimeError(
                f"FATAL: transform() changed row count! "
                f"Input: {original_len}, Output: {len(df)}. "
                f"This violates the ML contract."
            )
        
        # Final verification
        if df.isnull().any().any():
            raise RuntimeError(
                f"FATAL: NaN values still present after all transformations!\n"
                f"Columns with NaN: {df.columns[df.isnull().any()].tolist()}"
            )
        
        if self.verbose:
            print(f"  ✓ Output shape: {df.shape} (rows preserved)")
            print(f"  ✓ No NaN values remaining")
        
        return df
    
    def transform_target(self, target: pd.Series) -> pd.Series:
        """
        Transform target variable (validation/test only).
        NEVER drops rows - returns NaN for invalid values.
        
        Args:
            target: Target variable
            
        Returns:
            Transformed target (same length as input)
        """
        if not self._is_fitted:
            raise ValueError("Agent must be fitted first")
        
        if self.target_processor is None:
            raise ValueError("No target processor available (unsupervised learning?)")
        
        original_len = len(target)
        transformed = self.target_processor.transform_target(target)
        
        # Verify no row dropping
        if len(transformed) != original_len:
            raise RuntimeError(
                f"FATAL: transform_target() changed row count! "
                f"Input: {original_len}, Output: {len(transformed)}"
            )
        
        return transformed
    
    def inverse_transform_target(self, y_pred: np.ndarray) -> np.ndarray:
        """Inverse transform predictions."""
        if self.target_processor is None:
            return y_pred
        return self.target_processor.inverse_transform(y_pred)

    # ---------------------------
    # Preprocessing Steps
    # ---------------------------

    def _validate_config(self, config: Dict):
        """Validate preprocessing configuration."""
        required_keys = ['columns_to_drop', 'columns_to_keep', 'pipeline_recommendation']
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required key in config: {key}")

    def _step_0_drop_columns(self, config: Dict):
        """Drop unnecessary columns."""
        columns_to_drop = config['columns_to_drop']['column_list']
        existing_cols = [col for col in columns_to_drop if col in self.feature_df.columns]
        
        if existing_cols:
            if self.verbose:
                print(f"\n[Step 0] Dropping {len(existing_cols)} columns...")
            self.feature_df = self.feature_df.drop(columns=existing_cols)
            self.transformers['dropped_columns'] = existing_cols

    def _step_1_fit_transform_missing(self, config: Dict):
        """Fit and transform missing value imputation."""
        pipeline = config['pipeline_recommendation']
        missing_config = pipeline.get('step_1_missing_values', {})
        
        if self.verbose:
            print(f"\n[Step 1] Handling missing values...")
        
        if self.learning_type == LearningType.APRIORI:
            # Apriori: Fill categorical with 'missing'
            categorical_cols = self.feature_df.select_dtypes(include=['object', 'category']).columns.tolist()
            for col in categorical_cols:
                if self.feature_df[col].isnull().any():
                    self.feature_df[col] = self.feature_df[col].fillna('missing')
            
            # Numeric: median imputation
            numeric_cols = self.feature_df.select_dtypes(include=[np.number]).columns.tolist()
            numeric_missing = [col for col in numeric_cols if self.feature_df[col].isnull().any()]
            if numeric_missing:
                imputer = MeanMedianImputer(imputation_method='median', variables=numeric_missing)
                self.feature_df[numeric_missing] = imputer.fit_transform(self.feature_df[numeric_missing])
                self.transformers['numeric_imputer'] = imputer
        else:
            # Numeric imputation
            numeric_cols = self.feature_df.select_dtypes(include=[np.number]).columns.tolist()
            numeric_missing = [col for col in numeric_cols if self.feature_df[col].isnull().any()]
            
            if numeric_missing:
                strategy = missing_config.get('numeric_strategy',
                                             'median' if self.learning_type == LearningType.CLUSTERING else 'mean')
                imputer = MeanMedianImputer(imputation_method=strategy, variables=numeric_missing)
                self.feature_df[numeric_missing] = imputer.fit_transform(self.feature_df[numeric_missing])
                self.transformers['numeric_imputer'] = imputer
                if self.verbose:
                    print(f"  • Imputed {len(numeric_missing)} numeric columns ({strategy})")
            
            # Categorical imputation
            categorical_cols = self.feature_df.select_dtypes(include=['object', 'category']).columns.tolist()
            categorical_missing = [col for col in categorical_cols if self.feature_df[col].isnull().any()]
            
            if categorical_missing:
                imputer = CategoricalImputer(imputation_method='frequent', variables=categorical_missing)
                self.feature_df[categorical_missing] = imputer.fit_transform(self.feature_df[categorical_missing])
                self.transformers['categorical_imputer'] = imputer
                if self.verbose:
                    print(f"  • Imputed {len(categorical_missing)} categorical columns")

    def _step_2_fit_transform_outliers(self, config: Dict):
        """
        Fit and transform outlier handling.
        
        CRITICAL FIX: Only fit winsorizer on NUMERIC columns that exist at this point.
        This prevents column mismatch errors during transform().
        """
        pipeline = config['pipeline_recommendation']
        outlier_config = pipeline.get('step_2_outliers', {})
        method = outlier_config.get('method', 'winsorize')
        
        # Get columns from config
        config_columns = outlier_config.get('columns_affected', [])
        
        # CRITICAL: Filter to only NUMERIC columns that ACTUALLY EXIST
        numeric_cols = self.feature_df.select_dtypes(include=[np.number]).columns.tolist()
        columns = [col for col in config_columns if col in numeric_cols]
        
        if not columns:
            if self.verbose:
                print(f"\n[Step 2] No numeric columns to winsorize")
            return
        
        if self.verbose:
            print(f"\n[Step 2] Handling outliers ({method})...")
        
        if method == 'winsorize':
            params = outlier_config.get('parameters', {})
            capping_method = params.get('capping_method', 'iqr')
            fold = params.get('fold', 1.5)
            
            if self.learning_type == LearningType.CLUSTERING:
                fold = max(fold, 2.0)
            
            # Fit winsorizer ONLY on numeric columns
            winsorizer = Winsorizer(
                capping_method=capping_method, 
                tail='both', 
                fold=fold, 
                variables=columns
            )
            self.feature_df[columns] = winsorizer.fit_transform(self.feature_df[columns])
            self.transformers['winsorizer'] = winsorizer
            
            if self.verbose:
                print(f"  • Winsorized {len(columns)} numeric columns")
                # Show which columns were winsorized
                original_cols = [c for c in columns if c in self.original_df.columns]
                engineered_cols = [c for c in columns if c not in self.original_df.columns]
                if original_cols and engineered_cols:
                    print(f"    - Original: {len(original_cols)} columns")
                    print(f"    - Engineered: {len(engineered_cols)} columns")

    def _step_3_feature_engineering(self, config: Dict):
        """Create new features using SAFE operations."""
        suggestions = config.get('feature_engineering_suggestions', [])
        if not suggestions:
            return
        
        if self.verbose:
            print(f"\n[Step 3] Feature engineering (safe mode)...")
        
        for feat_config in suggestions:
            new_feature = feat_config['new_feature']
            source_cols = feat_config['source_columns']
            transformation = feat_config.get('transformation', [])
            
            if not all(col in self.feature_df.columns for col in source_cols):
                continue
            
            # Parse transformation to extract operation
            operation = self._parse_operation_from_code(transformation, source_cols)
            
            if operation:
                safe_config = {
                    'new_feature': new_feature,
                    'source_columns': source_cols,
                    'operation': operation
                }
                
                try:
                    self.feature_df[new_feature] = FeatureEngineeringEngine.create_feature(
                        self.feature_df, 
                        safe_config
                    )
                    self.feature_engineering_configs.append(safe_config)
                    if self.verbose:
                        print(f"  • Created: {new_feature}")
                except Exception as e:
                    if self.verbose:
                        print(f"  ⚠ Failed: {new_feature} - {e}")
    
    def _parse_operation_from_code(self, transformation: list, source_cols: list) -> Optional[str]:
        """Parse operation from code strings (safe extraction)."""
        if not transformation or len(source_cols) != 2:
            return None
        
        code = ' '.join(transformation).lower()
        
        if '/' in code:
            return 'divide'
        elif '*' in code:
            return 'multiply'
        elif '+' in code:
            return 'add'
        elif '-' in code:
            return 'subtract'
        
        return None

    def _step_4_fit_transform_categorical(self, config: Dict):
        """Fit and transform categorical encoding."""
        pipeline = config['pipeline_recommendation']
        encoding_config = pipeline.get('step_3_encoding', {})
        
        if self.verbose:
            print(f"\n[Step 4] Encoding categorical variables...")
        
        if self.learning_type == LearningType.APRIORI:
            categorical_cols = self.feature_df.select_dtypes(include=['object', 'category']).columns.tolist()
            for col in categorical_cols:
                self.feature_df[col] = self.feature_df[col].astype(str)
        else:
            # One-hot encoding
            onehot_cols = [col for col in encoding_config.get('onehot_columns', []) if col in self.feature_df.columns]
            if onehot_cols:
                for col in onehot_cols:
                    self.feature_df[col] = self.feature_df[col].astype(str).replace('nan', 'missing')
                
                drop_last = self.learning_type == LearningType.CLUSTERING
                encoder = OneHotEncoder(variables=onehot_cols, drop_last=drop_last)
                self.feature_df = encoder.fit_transform(self.feature_df)
                self.transformers['onehot_encoder'] = encoder
                if self.verbose:
                    print(f"  • One-hot encoded {len(onehot_cols)} columns")
            
            # Frequency encoding
            frequency_cols = [col for col in encoding_config.get('frequency_columns', []) if col in self.feature_df.columns]
            if frequency_cols:
                for col in frequency_cols:
                    self.feature_df[col] = self.feature_df[col].astype(str)
                
                encoder = CountFrequencyEncoder(variables=frequency_cols, encoding_method='frequency')
                self.feature_df = encoder.fit_transform(self.feature_df)
                self.transformers['frequency_encoder'] = encoder
                if self.verbose:
                    print(f"  • Frequency encoded {len(frequency_cols)} columns")

    def _step_5_fit_transform_features(self, config: Dict):
        """Fit and transform feature transformations."""
        pipeline = config['pipeline_recommendation']
        transform_config = pipeline.get('step_4_transformation', {})
        
        if self.verbose:
            print(f"\n[Step 5] Transforming features...")
        
        # Log transformation
        log_cols = [col for col in transform_config.get('log_transform', []) if col in self.feature_df.columns]
        if log_cols:
            numeric_log_cols = [col for col in log_cols if pd.api.types.is_numeric_dtype(self.feature_df[col])]
            
            if numeric_log_cols:
                try:
                    for col in numeric_log_cols:
                        if (self.feature_df[col] <= 0).any():
                            min_val = self.feature_df[col].min()
                            self.feature_df[col] = self.feature_df[col] - min_val + 1
                    
                    transformer = LogTransformer(variables=numeric_log_cols)
                    self.feature_df = transformer.fit_transform(self.feature_df)
                    self.transformers['log_transformer'] = transformer
                    if self.verbose:
                        print(f"  • Log transformed {len(numeric_log_cols)} column(s)")
                except Exception as e:
                    if self.verbose:
                        print(f"  ⚠ Log transformation failed: {e}")
        
        # Yeo-Johnson transformation
        yeo_cols = [col for col in transform_config.get('yeo_johnson', []) if col in self.feature_df.columns]
        if yeo_cols:
            numeric_yeo_cols = [col for col in yeo_cols if pd.api.types.is_numeric_dtype(self.feature_df[col])]
            
            if numeric_yeo_cols:
                try:
                    transformer = YeoJohnsonTransformer(variables=numeric_yeo_cols)
                    self.feature_df = transformer.fit_transform(self.feature_df)
                    self.transformers['yeo_johnson_transformer'] = transformer
                    if self.verbose:
                        print(f"  • Yeo-Johnson transformed {len(numeric_yeo_cols)} column(s)")
                except Exception as e:
                    if self.verbose:
                        print(f"  ⚠ Yeo-Johnson transformation failed: {e}")

    def _step_6_fit_transform_scale(self, config: Dict):
        """Fit and transform feature scaling."""
        pipeline = config['pipeline_recommendation']
        scaling_config = pipeline.get('step_5_scaling', {})
        
        # Prevent scaling for Apriori
        if self.learning_type == LearningType.APRIORI:
            return
        
        method = scaling_config.get('method', 'standard')
        columns = [col for col in scaling_config.get('columns', []) if col in self.feature_df.columns]
        
        if not columns and self.learning_type == LearningType.CLUSTERING:
            columns = self.feature_df.select_dtypes(include=[np.number]).columns.tolist()
        
        if not columns:
            return
        
        if self.verbose:
            print(f"\n[Step 6] Scaling features ({method})...")
        
        scaler_map = {
            'standard': StandardScaler(),
            'minmax': MinMaxScaler(),
            'robust': RobustScaler()
        }
        scaler = scaler_map.get(method, StandardScaler())
        
        wrapper = SklearnTransformerWrapper(transformer=scaler, variables=columns)
        self.feature_df = wrapper.fit_transform(self.feature_df)
        self.transformers['scaler'] = wrapper
        if self.verbose:
            print(f"  • Scaled {len(columns)} columns")

    def _step_7_fit_transform_feature_selection(self, config: Dict):
        """Fit and transform feature selection."""
        pipeline = config['pipeline_recommendation']
        selection_config = pipeline.get('step_6_feature_selection', {})
        
        if self.verbose:
            print(f"\n[Step 7] Feature selection...")
        
        n_features = len(self.feature_df.columns)
        if n_features < 2:
            if self.verbose:
                print(f"  ⚠ Skipping (only {n_features} feature(s))")
            return
        
        # Drop constant features
        if selection_config.get('drop_constant', True):
            tol = 0.98 if self.learning_type == LearningType.CLUSTERING else 0.99
            try:
                selector = DropConstantFeatures(tol=tol)
                self.feature_df = selector.fit_transform(self.feature_df)
                self.transformers['constant_dropper'] = selector
                
                if hasattr(selector, 'features_to_drop_') and selector.features_to_drop_:
                    if self.verbose:
                        print(f"  • Dropped {len(selector.features_to_drop_)} constant feature(s)")
            except Exception as e:
                if self.verbose:
                    print(f"  ⚠ Constant dropper failed: {e}")
        
        if len(self.feature_df.columns) < 2:
            return
        
        # Drop duplicate features
        try:
            selector = DropDuplicateFeatures()
            self.feature_df = selector.fit_transform(self.feature_df)
            self.transformers['duplicate_dropper'] = selector
            
            if hasattr(selector, 'features_to_drop_') and selector.features_to_drop_:
                if self.verbose:
                    print(f"  • Dropped {len(selector.features_to_drop_)} duplicate feature(s)")
        except Exception as e:
            if self.verbose:
                print(f"  ⚠ Duplicate dropper failed: {e}")

    def _step_8_association_preprocessing(self, config: Dict):
        """Association rule mining preprocessing."""
        if self.learning_type != LearningType.APRIORI:
            return
        
        if self.verbose:
            print(f"\n[Step 8] Association preprocessing...")
        
        pipeline = config['pipeline_recommendation']
        assoc_config = pipeline.get('step_7_association', {})
        
        for col in self.feature_df.columns:
            if self.feature_df[col].dtype != 'object':
                if col in assoc_config.get('binning_columns', []):
                    n_bins = assoc_config.get('n_bins', 5)
                    self.feature_df[col] = pd.qcut(
                        self.feature_df[col], 
                        q=n_bins,
                        labels=[f'{col}_bin_{i}' for i in range(n_bins)],
                        duplicates='drop'
                    )
                else:
                    self.feature_df[col] = self.feature_df[col].astype(str)
        
        min_support = assoc_config.get('min_support', 0.01)
        for col in self.feature_df.columns:
            value_counts = self.feature_df[col].value_counts(normalize=True)
            low_support = value_counts[value_counts < min_support].index
            if len(low_support) > 0:
                self.feature_df[col] = self.feature_df[col].replace(low_support, 'other')

    def _sanitize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Sanitize column names for XGBoost compatibility."""
        df = df.copy()
        df.columns = [
            str(col).replace('[', '_').replace(']', '_').replace('<', '_').replace('>', '_')
            for col in df.columns
        ]
        return df

    # ---------------------------
    # Reporting
    # ---------------------------

    def _generate_report(self, config: Dict, target: Optional[pd.Series]):
        """Generate preprocessing report."""
        self.preprocessing_report = {
            'learning_type': self.learning_type.value,
            'original_shape': self.original_df.shape,
            'final_shape': self.feature_df.shape,
            'original_columns': self.original_df.columns.tolist(),
            'final_columns': self.feature_df.columns.tolist(),
            'columns_added': list(set(self.feature_df.columns) - set(self.original_df.columns)),
            'columns_removed': list(set(self.original_df.columns) - set(self.feature_df.columns)),
            'transformers_applied': list(self.transformers.keys()),
            'missing_values_before': int(self.original_df.isnull().sum().sum()),
            'missing_values_after': int(self.feature_df.isnull().sum().sum()),
        }
        
        # Target info
        if self.target_processor and target is not None:
            self.preprocessing_report['target_info'] = {
                'original_dtype': str(self.original_target.dtype),
                'final_dtype': str(target.dtype),
                'original_shape': self.original_target.shape,
                'final_shape': target.shape,
                'was_encoded': self.target_processor.encoder is not None,
                'was_winsorized': self.target_processor.winsorizer is not None,
                'label_mapping': self.target_processor.label_mapping if self.target_processor.label_mapping else None,
                'rows_dropped': len(self.original_target) - len(target)
            }

    def get_report(self) -> Dict:
        """Get preprocessing report."""
        return self.preprocessing_report

    def print_report(self):
        """Print formatted report."""
        report = self.preprocessing_report
        print("\n" + "="*70)
        print("PREPROCESSING REPORT")
        print("="*70)
        print(f"Task: {report['learning_type']}")
        print(f"Original: {report['original_shape']}")
        print(f"Final: {report['final_shape']}")
        print(f"Transformers: {', '.join(report['transformers_applied'])}")
        
        if 'target_info' in report:
            print("\nTarget:")
            ti = report['target_info']
            print(f"  • Encoded: {ti['was_encoded']}")
            print(f"  • Winsorized: {ti['was_winsorized']}")
            print(f"  • Rows dropped: {ti['rows_dropped']}")
        print("="*70)

    def get_data(self) -> Tuple[pd.DataFrame, Optional[pd.Series]]:
        """Get preprocessed data."""
        return self.feature_df, None  # Target handled separately

    def is_fitted(self) -> bool:
        """Check if fitted."""
        return self._is_fitted
    
    def save_processed_data(
        self,
        features: pd.DataFrame,
        target: Optional[pd.Series] = None,
        features_filepath: Optional[str] = None,
        target_filepath: Optional[str] = None,
        combined_filepath: Optional[str] = None,
        save_combined: bool = False
    ) -> Dict[str, str]:
        """Save preprocessed data to disk."""
        saved_paths = {}
        
        # Ensure output directories exist
        for filepath in [features_filepath, target_filepath, combined_filepath]:
            if filepath:
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save features
        if features_filepath:
            features.to_csv(features_filepath, index=False)
            saved_paths['features'] = features_filepath
        
        # Save target
        if target is not None and target_filepath:
            target_df = pd.DataFrame(target) if isinstance(target, pd.Series) else target
            target_df.to_csv(target_filepath, index=False)
            saved_paths['target'] = target_filepath
        
        # Save combined
        if save_combined and combined_filepath:
            if target is not None:
                combined = features.copy()
                target_col_name = target.name if hasattr(target, 'name') and target.name else 'target'
                combined[target_col_name] = target.values
                combined.to_csv(combined_filepath, index=False)
                saved_paths['combined'] = combined_filepath
            else:
                features.to_csv(combined_filepath, index=False)
                saved_paths['combined'] = combined_filepath
        
        return saved_paths