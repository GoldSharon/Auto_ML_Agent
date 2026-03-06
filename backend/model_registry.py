from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge, Lasso
from sklearn.svm import SVC, SVR
from sklearn.ensemble import (
    RandomForestClassifier, RandomForestRegressor,
    GradientBoostingClassifier, GradientBoostingRegressor
)
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.neural_network import MLPClassifier, MLPRegressor
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.base import BaseEstimator, ClassifierMixin, RegressorMixin
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb
from catboost import CatBoostClassifier, CatBoostRegressor
import logging
import json
import os
from pathlib import Path

import optuna
from optuna.samplers import TPESampler
from sklearn.model_selection import cross_val_score
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    r2_score,
    mean_absolute_error,
    mean_squared_error,
    root_mean_squared_error,
    median_absolute_error,
    explained_variance_score,
    silhouette_score,
    calinski_harabasz_score,
    davies_bouldin_score,
    make_scorer
)

from typing import Union, Dict, Any, Tuple
from core.models import Hardware, InputConfiguration, LearningType, MLType
import pandas as pd
import numpy as np
from joblib import Parallel, delayed
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from tqdm import tqdm
import sys
import time

logger = logging.getLogger(__name__)

# Suppress Optuna's verbose logging
optuna.logging.set_verbosity(optuna.logging.WARNING)

# Get number of available CPU cores
N_CORES = multiprocessing.cpu_count()
logger.info(f"Detected {N_CORES} CPU cores available")


# ============================================================================
# PYTORCH GPU MLP — sklearn-compatible wrapper
# ============================================================================

class _MLPNet(nn.Module):
    """Internal PyTorch network used by both classifier and regressor wrappers."""

    def __init__(self, input_dim, output_dim, hidden_layers, activation, dropout):
        super().__init__()
        act_map = {
            "relu": nn.ReLU(),
            "tanh": nn.Tanh(),
            "sigmoid": nn.Sigmoid(),
        }
        act_fn = act_map.get(activation, nn.ReLU())

        layers = []
        prev = input_dim
        for h in hidden_layers:
            layers += [nn.Linear(prev, h), act_fn, nn.Dropout(dropout)]
            prev = h
        layers.append(nn.Linear(prev, output_dim))
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)


class TorchMLPRegressor(BaseEstimator, RegressorMixin):
    """
    GPU-accelerated MLP regressor with a sklearn-compatible API.

    Parameters
    ----------
    hidden_layers : tuple  — sizes of hidden layers
    activation    : str    — "relu", "tanh", or "sigmoid"
    dropout       : float  — dropout probability
    lr            : float  — learning rate
    batch_size    : int    — mini-batch size
    max_iter      : int    — training epochs
    random_state  : int    — seed for reproducibility
    """

    def __init__(self, hidden_layers=(128, 64), activation="relu",
                 dropout=0.2, lr=1e-3, batch_size=256,
                 max_iter=100, random_state=42):
        self.hidden_layers = hidden_layers
        self.activation = activation
        self.dropout = dropout
        self.lr = lr
        self.batch_size = batch_size
        self.max_iter = max_iter
        self.random_state = random_state

    def fit(self, X, y):
        torch.manual_seed(self.random_state)
        self.device_ = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        X_t = torch.tensor(np.array(X), dtype=torch.float32)
        y_t = torch.tensor(np.array(y), dtype=torch.float32).unsqueeze(1)

        dataset = TensorDataset(X_t, y_t)
        loader  = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)

        self.model_ = _MLPNet(
            input_dim=X_t.shape[1],
            output_dim=1,
            hidden_layers=self.hidden_layers,
            activation=self.activation,
            dropout=self.dropout,
        ).to(self.device_)

        optimizer = torch.optim.Adam(self.model_.parameters(), lr=self.lr)
        loss_fn   = nn.MSELoss()

        self.model_.train()
        for _ in range(self.max_iter):
            for xb, yb in loader:
                xb, yb = xb.to(self.device_), yb.to(self.device_)
                optimizer.zero_grad()
                loss_fn(self.model_(xb), yb).backward()
                optimizer.step()
        return self

    def predict(self, X):
        self.model_.eval()
        X_t = torch.tensor(np.array(X), dtype=torch.float32).to(self.device_)
        with torch.no_grad():
            preds = self.model_(X_t).squeeze(1).cpu().numpy()
        return preds

    def score(self, X, y):
        from sklearn.metrics import r2_score as _r2
        return _r2(y, self.predict(X))


class TorchMLPClassifier(BaseEstimator, ClassifierMixin):
    """
    GPU-accelerated MLP classifier with a sklearn-compatible API.

    Parameters
    ----------
    hidden_layers : tuple  — sizes of hidden layers
    activation    : str    — "relu", "tanh", or "sigmoid"
    dropout       : float  — dropout probability
    lr            : float  — learning rate
    batch_size    : int    — mini-batch size
    max_iter      : int    — training epochs
    random_state  : int    — seed for reproducibility
    """

    def __init__(self, hidden_layers=(128, 64), activation="relu",
                 dropout=0.2, lr=1e-3, batch_size=256,
                 max_iter=100, random_state=42):
        self.hidden_layers = hidden_layers
        self.activation = activation
        self.dropout = dropout
        self.lr = lr
        self.batch_size = batch_size
        self.max_iter = max_iter
        self.random_state = random_state

    def fit(self, X, y):
        torch.manual_seed(self.random_state)
        self.device_ = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.le_ = LabelEncoder()
        y_enc = self.le_.fit_transform(y)
        self.classes_ = self.le_.classes_
        n_classes = len(self.classes_)

        X_t = torch.tensor(np.array(X), dtype=torch.float32)
        y_t = torch.tensor(y_enc, dtype=torch.long)

        dataset = TensorDataset(X_t, y_t)
        loader  = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)

        self.model_ = _MLPNet(
            input_dim=X_t.shape[1],
            output_dim=n_classes,
            hidden_layers=self.hidden_layers,
            activation=self.activation,
            dropout=self.dropout,
        ).to(self.device_)

        optimizer = torch.optim.Adam(self.model_.parameters(), lr=self.lr)
        loss_fn   = nn.CrossEntropyLoss()

        self.model_.train()
        for _ in range(self.max_iter):
            for xb, yb in loader:
                xb, yb = xb.to(self.device_), yb.to(self.device_)
                optimizer.zero_grad()
                loss_fn(self.model_(xb), yb).backward()
                optimizer.step()
        return self

    def predict(self, X):
        self.model_.eval()
        X_t = torch.tensor(np.array(X), dtype=torch.float32).to(self.device_)
        with torch.no_grad():
            logits = self.model_(X_t)
            preds  = logits.argmax(dim=1).cpu().numpy()
        return self.le_.inverse_transform(preds)

    def predict_proba(self, X):
        self.model_.eval()
        X_t = torch.tensor(np.array(X), dtype=torch.float32).to(self.device_)
        with torch.no_grad():
            probs = torch.softmax(self.model_(X_t), dim=1).cpu().numpy()
        return probs

    def score(self, X, y):
        from sklearn.metrics import accuracy_score as _acc
        return _acc(y, self.predict(X))


CPU_MODELS = {
    LearningType.CLASSIFICATION: {
        "logistic": LogisticRegression(max_iter=1000),
        "svm": SVC(),
        "rf": RandomForestClassifier(n_jobs=1),
        "gb": GradientBoostingClassifier(),
        "mlp": MLPClassifier(max_iter=500),  # sklearn MLP has no GPU support, kept here
    },

    LearningType.REGRESSION: {
        "linreg": LinearRegression(),
        "ridge": Ridge(),
        "svr": SVR(),
        "lasso": Lasso(),
        "rf": RandomForestRegressor(n_jobs=1),
        "gb": GradientBoostingRegressor(),
        "mlp": MLPRegressor(max_iter=500),  # sklearn MLP has no GPU support, kept here
    },

    LearningType.CLUSTERING: {
        "kmeans": KMeans(n_clusters=3),
        "dbscan": DBSCAN(),
        "agglo": AgglomerativeClustering()
    }
}

GPU_MODELS = {
    LearningType.CLASSIFICATION: {
        "torch_mlp": TorchMLPClassifier(),
        "xgb": xgb.XGBClassifier(tree_method="auto", n_jobs=1),
        "catboost": CatBoostClassifier(task_type="GPU", verbose=False, allow_writing_files=False)
    },

    LearningType.REGRESSION: {
        "torch_mlp": TorchMLPRegressor(),
        "xgb": xgb.XGBRegressor(tree_method="auto", n_jobs=1),
        "catboost": CatBoostRegressor(task_type="GPU", verbose=False, allow_writing_files=False)
    },

    LearningType.CLUSTERING: {}
}

# Parameter whitelist - only these parameters can be passed to models
PARAM_WHITELIST = {
    "logistic": {"C", "penalty", "solver", "max_iter", "class_weight", "random_state"},
    "svm": {"C", "kernel", "gamma", "degree", "coef0", "shrinking", "probability", "cache_size", "class_weight", "random_state"},
    "svr": {"C", "kernel", "gamma", "degree", "epsilon", "coef0", "shrinking", "cache_size"},
    "rf": {"n_estimators", "max_depth", "min_samples_split", "min_samples_leaf", "max_features", 
           "bootstrap", "oob_score", "random_state", "n_jobs"},
    "gb": {"n_estimators", "learning_rate", "max_depth", "min_samples_split", "min_samples_leaf",
           "subsample", "max_features", "random_state"},
    "linreg": {"fit_intercept", "copy_X"},
    "ridge": {"alpha", "fit_intercept", "copy_X", "solver", "random_state"},
    "lasso": {"alpha", "fit_intercept", "max_iter", "tol", "warm_start", "random_state"},
    "mlp": {"hidden_layer_sizes", "activation", "solver", "alpha", "batch_size", "learning_rate",
            "learning_rate_init", "max_iter", "shuffle", "random_state", "tol", "momentum",
            "early_stopping", "validation_fraction"},
    "xgb": {"n_estimators", "max_depth", "learning_rate", "subsample", "colsample_bytree",
            "reg_alpha", "reg_lambda", "min_child_weight", "gamma", "tree_method", "n_jobs", "random_state"},
    "catboost": {"iterations", "depth", "learning_rate", "l2_leaf_reg", "bagging_temperature",
                 "border_count", "task_type", "verbose", "allow_writing_files", "random_state"},
    "kmeans": {"n_clusters", "init", "n_init", "max_iter", "tol", "random_state"},
    "dbscan": {"eps", "min_samples", "metric", "algorithm", "leaf_size"},
    "agglo": {"n_clusters", "linkage", "affinity", "metric"},
    "torch_mlp": {"hidden_layers", "activation", "dropout", "lr", "batch_size", "max_iter", "random_state"},
}


# ============================================================================
# PROGRESS TRACKING UTILITIES
# ============================================================================

class ProgressTracker:
    """Centralized progress tracking for training pipeline."""
    
    def __init__(self):
        self.current_phase = ""
        self.total_models = 0
        self.completed_models = 0
        self.current_model = ""
        self.start_time = None
        
    def start(self, total_models: int):
        """Initialize progress tracking."""
        self.total_models = total_models
        self.completed_models = 0
        self.start_time = time.time()
        
    def update(self, model_name: str, phase: str):
        """Update current progress."""
        self.current_model = model_name
        self.current_phase = phase
        
    def complete_model(self):
        """Mark a model as completed."""
        self.completed_models += 1
        
    def get_progress_percentage(self) -> float:
        """Get overall progress percentage."""
        if self.total_models == 0:
            return 0.0
        return (self.completed_models / self.total_models) * 100
    
    def get_elapsed_time(self) -> str:
        """Get elapsed time as formatted string."""
        if self.start_time is None:
            return "00:00"
        elapsed = time.time() - self.start_time
        mins, secs = divmod(int(elapsed), 60)
        return f"{mins:02d}:{secs:02d}"
    
    def get_eta(self) -> str:
        """Estimate time remaining."""
        if self.start_time is None or self.completed_models == 0:
            return "Unknown"
        elapsed = time.time() - self.start_time
        avg_time_per_model = elapsed / self.completed_models
        remaining_models = self.total_models - self.completed_models
        eta_seconds = avg_time_per_model * remaining_models
        mins, secs = divmod(int(eta_seconds), 60)
        return f"{mins:02d}:{secs:02d}"


# Global progress tracker
progress_tracker = ProgressTracker()


def print_progress_header():
    """Print a nice header for the training process."""
    print("\n" + "="*80)
    print("🚀 MODEL TRAINING PIPELINE".center(80))
    print("="*80 + "\n")


def print_progress_summary():
    """Print final summary of training."""
    print("\n" + "="*80)
    print("✅ TRAINING COMPLETE".center(80))
    print("="*80)
    print(f"Total time: {progress_tracker.get_elapsed_time()}")
    print(f"Models trained: {progress_tracker.completed_models}/{progress_tracker.total_models}")
    print("="*80 + "\n")


# ============================================================================
# CORE FUNCTIONS
# ============================================================================

def load_hyperparameter_config():
    """Load hyperparameter configuration from JSON file."""
    config_path = Path(__file__).parent / "hyper_parameter_config.json"
    
    if not config_path.exists():
        logger.warning(f"Hyperparameter config not found at {config_path}")
        return {}
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        logger.info(f"Loaded hyperparameter config from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Error loading hyperparameter config: {e}")
        return {}


def filter_params(model_name: str, params: Dict) -> Dict:
    """Filter parameters to only include whitelisted ones for the model."""
    if model_name not in PARAM_WHITELIST:
        logger.warning(f"No parameter whitelist for {model_name}, using all params")
        return params
    
    whitelist = PARAM_WHITELIST[model_name]
    filtered = {k: v for k, v in params.items() if k in whitelist}
    
    # Log if any params were filtered out
    removed = set(params.keys()) - set(filtered.keys())
    if removed:
        logger.debug(f"Filtered out non-whitelisted params for {model_name}: {removed}")
    
    return filtered


def get_model_class(model_name: str, learning_type: LearningType, hardware: Hardware):
    """Get the model class for a given model name."""
    model_map = {
        # Classification
        "logistic": LogisticRegression,
        "svm": (SVC, SVR),
        "rf": (RandomForestClassifier, RandomForestRegressor),
        "gb": (GradientBoostingClassifier, GradientBoostingRegressor),
        # Regression
        "linreg": LinearRegression,
        "ridge": Ridge,
        "lasso": Lasso,
        "svr": SVR,
        # Neural Networks
        "mlp": (MLPClassifier, MLPRegressor),
        "torch_mlp": (TorchMLPClassifier, TorchMLPRegressor),
        # Boosting
        "xgb": (xgb.XGBClassifier, xgb.XGBRegressor),
        "catboost": (CatBoostClassifier, CatBoostRegressor),
        # Clustering
        "kmeans": KMeans,
        "dbscan": DBSCAN,
        "agglo": AgglomerativeClustering
    }
    
    model_class = model_map.get(model_name)
    
    if isinstance(model_class, tuple):
        # Different class for classification vs regression
        if learning_type == LearningType.CLASSIFICATION:
            return model_class[0]
        elif learning_type == LearningType.REGRESSION:
            return model_class[1]
    
    return model_class


def create_optuna_objective(model_name: str, model_class, param_config: Dict, 
                           X, y, learning_type: LearningType, hardware: Hardware,
                           trial_pbar: tqdm = None):
    """Create Optuna objective function with progress tracking."""
    
    def objective(trial):
        # Update trial progress bar if provided
        if trial_pbar is not None:
            trial_pbar.set_description(f"[{model_name}] Trial {trial.number + 1}")
            trial_pbar.update(0)  # Just refresh the display
        
        # Build hyperparameters from config
        params = {}
        
        for param_name, param_values in param_config.items():
            if not param_values:
                continue
                
            if isinstance(param_values, list):
                if len(param_values) == 0:
                    continue
                    
                # Check if values are numeric or categorical
                if all(isinstance(v, (int, float)) for v in param_values):
                    # Numeric values
                    if all(isinstance(v, int) for v in param_values):
                        params[param_name] = trial.suggest_int(
                            param_name, min(param_values), max(param_values)
                        )
                    else:
                        params[param_name] = trial.suggest_float(
                            param_name, min(param_values), max(param_values)
                        )
                else:
                    # Categorical values
                    params[param_name] = trial.suggest_categorical(param_name, param_values)
        
        # Add hardware-specific parameters
        if model_name == "catboost":
            params['task_type'] = "GPU" if hardware == Hardware.GPU else "CPU"
            params['verbose'] = False
            params['allow_writing_files'] = False
        elif model_name == "xgb":
            params['tree_method'] = "auto"
            params['n_jobs'] = 1
        elif model_name in ["rf"]:
            params['n_jobs'] = 1
        elif model_name == "logistic":
            params['max_iter'] = params.get('max_iter', 1000)
        elif model_name == "mlp":
            params['max_iter'] = params.get('max_iter', 500)
        elif model_name == "torch_mlp":
            params['max_iter'] = params.get('max_iter', 100)
        
        # Filter params through whitelist
        params = filter_params(model_name, params)
        
        try:
            # Create model with suggested parameters
            model = model_class(**params)
            
            # Evaluate using cross-validation
            if learning_type == LearningType.CLASSIFICATION:
                scoring = 'f1_weighted'
            elif learning_type == LearningType.REGRESSION:
                scoring = 'r2'
            elif learning_type == LearningType.CLUSTERING:
                # For clustering, we'll use silhouette score
                model.fit(X)
                labels = model.labels_ if hasattr(model, 'labels_') else model.predict(X)
                score = silhouette_score(X, labels)
                if trial_pbar is not None:
                    trial_pbar.update(1)
                return score
            
            # Cross-validation for supervised learning
            scores = cross_val_score(model, X, y, cv=3, scoring=scoring, n_jobs=1)
            
            # Update progress
            if trial_pbar is not None:
                trial_pbar.update(1)
            
            return np.mean(scores)
            
        except Exception as e:
            logger.warning(f"Trial failed for {model_name}: {e}")
            if trial_pbar is not None:
                trial_pbar.update(1)
            # Return worst possible score
            return -1e10 if learning_type == LearningType.REGRESSION else 0.0
    
    return objective


def tune_single_model(model_name: str, model_class, param_config: Dict,
                      X, y, learning_type: LearningType, hardware: Hardware,
                      n_trials: int = 5, show_progress: bool = True) -> Tuple[str, Dict, float]:
    """
    Tune hyperparameters for a single model with progress tracking.
    
    Returns:
        Tuple of (model_name, best_params, best_score)
    """
    progress_tracker.update(model_name, "Hyperparameter Tuning")
    
    if not param_config:
        logger.info(f"[{model_name}] No hyperparameter config, using defaults")
        return model_name, {}, 0.0
    
    try:
        # Create study
        study = optuna.create_study(
            direction='maximize',
            sampler=TPESampler(seed=42)
        )
        
        # Create progress bar for trials
        trial_pbar = None
        if show_progress:
            trial_pbar = tqdm(
                total=n_trials,
                desc=f"[{model_name}] Tuning",
                unit="trial",
                leave=False,
                position=1,
                bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'
            )
        
        # Create objective with progress bar
        objective = create_optuna_objective(
            model_name, model_class, param_config, X, y, learning_type, hardware, trial_pbar
        )
        
        # Optimize
        study.optimize(objective, n_trials=n_trials, show_progress_bar=False)
        
        # Close trial progress bar
        if trial_pbar is not None:
            trial_pbar.close()
        
        logger.info(f"✓ [{model_name}] Best score: {study.best_value:.4f}")
        logger.debug(f"  [{model_name}] Best params: {study.best_params}")
        
        return model_name, study.best_params, study.best_value
    
    except Exception as e:
        logger.error(f"✗ [{model_name}] Hyperparameter tuning failed: {e}")
        return model_name, {}, 0.0


def create_model_with_params(model_name: str, learning_type: LearningType, 
                             hardware: Hardware, best_params: Dict = None):
    """Create model instance with best parameters."""
    model_class = get_model_class(model_name, learning_type, hardware)
    
    if best_params is None:
        best_params = {}
    
    # Add hardware-specific parameters
    if model_name == "catboost":
        best_params['task_type'] = "GPU" if hardware == Hardware.GPU else "CPU"
        best_params['verbose'] = False
        best_params['allow_writing_files'] = False
    elif model_name == "xgb":
        best_params['tree_method'] = "auto"
        best_params['n_jobs'] = 1
    elif model_name in ["rf"]:
        best_params['n_jobs'] = 1
    elif model_name == "logistic":
        if 'max_iter' not in best_params:
            best_params['max_iter'] = 1000
    elif model_name == "mlp":
        if 'max_iter' not in best_params:
            best_params['max_iter'] = 500
    elif model_name == "torch_mlp":
        if 'max_iter' not in best_params:
            best_params['max_iter'] = 100
    
    # Filter params through whitelist
    best_params = filter_params(model_name, best_params)
    
    return model_class(**best_params)


def evaluate(models, X, y, learning_type):
    """Evaluate trained models with progress tracking."""
    scores = {}
    
    # Create progress bar for evaluation
    eval_pbar = tqdm(
        models.items(),
        desc="Evaluating models",
        unit="model",
        position=0,
        leave=True
    )

    for name, model in eval_pbar:
        eval_pbar.set_description(f"Evaluating {name}")
        
        preds = model.predict(X)

        if learning_type == LearningType.CLASSIFICATION:
            scores[name] = {
                "accuracy": accuracy_score(y, preds),
                "precision": precision_score(y, preds, average="weighted", zero_division=0),
                "recall": recall_score(y, preds, average="weighted", zero_division=0),
                "f1": f1_score(y, preds, average="weighted", zero_division=0),
                "confusion_matrix": confusion_matrix(y, preds).tolist()
            }

            # Optional ROC-AUC (only if binary)
            if len(set(y)) == 2 and hasattr(model, "predict_proba"):
                try:
                    probs = model.predict_proba(X)[:, 1]
                    scores[name]["roc_auc"] = roc_auc_score(y, probs)
                except:
                    pass

        elif learning_type == LearningType.REGRESSION:
            scores[name] = {
                "r2": r2_score(y, preds),
                "mae": mean_absolute_error(y, preds),
                "mse": mean_squared_error(y, preds),
                "rmse": root_mean_squared_error(y, preds),
                "explained_variance": explained_variance_score(y, preds)
            }

        elif learning_type == LearningType.CLUSTERING:
            scores[name] = {
                "silhouette": silhouette_score(X, preds),
                "calinski_harabasz": calinski_harabasz_score(X, preds),
                "davies_bouldin": davies_bouldin_score(X, preds)
            }

    eval_pbar.close()
    return scores


def train_with_tuning_parallel(models_dict, X, y, learning_type, hardware, ipc: InputConfiguration):
    """
    Train models with hyperparameter tuning using THREAD-LEVEL parallelization.
    Includes comprehensive progress tracking.
    """
    trained = {}
    best_params_dict = {}
    
    # Load hyperparameter config
    hp_config = load_hyperparameter_config()
    
    # Calculate number of parallel jobs
    max_workers = min(N_CORES, len(models_dict))
    
    # Initialize progress tracker
    progress_tracker.start(len(models_dict))
    
    # Prepare tuning tasks
    tuning_tasks = []
    for name, model in models_dict.items():
        param_config = hp_config.get(name, {})
        model_class = get_model_class(name, learning_type, hardware)
        tuning_tasks.append((name, model_class, param_config, X, y, learning_type, hardware))
    
    print_progress_header()
    print(f"📊 Training Configuration:")
    print(f"   • Hardware: {hardware.value}")
    print(f"   • Learning Type: {learning_type.value}")
    print(f"   • Total Models: {len(tuning_tasks)}")
    print(f"   • Parallel Workers: {max_workers}")
    print(f"   • Hyperparameter Tuning: Enabled (30 trials per model)")
    print()
    
    results = []
    
    # Create main progress bar
    main_pbar = tqdm(
        total=len(tuning_tasks),
        desc="Overall Progress",
        unit="model",
        position=0,
        bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'
    )
    
    # Use ThreadPoolExecutor with progress tracking
    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_model = {
                executor.submit(
                    tune_single_model,
                    name, model_class, param_config, X, y, learning_type, hardware, 5, True
                ): name
                for name, model_class, param_config, X, y, learning_type, hardware in tuning_tasks
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_model, timeout=3600):
                model_name = future_to_model[future]
                try:
                    result = future.result(timeout=60)
                    results.append(result)
                    
                    # Update progress
                    progress_tracker.complete_model()
                    main_pbar.update(1)
                    main_pbar.set_description(
                        f"Overall Progress [Last: {model_name}] "
                        f"[ETA: {progress_tracker.get_eta()}]"
                    )
                    
                except Exception as e:
                    logger.error(f"✗ [{model_name}] Hyperparameter tuning failed: {e}")
                    results.append((model_name, {}, 0.0))
                    progress_tracker.complete_model()
                    main_pbar.update(1)
        
        main_pbar.close()
        print("\n✅ Hyperparameter tuning complete!")
        
    except Exception as e:
        main_pbar.close()
        logger.error(f"ThreadPoolExecutor failed: {e}")
        logger.warning("Falling back to sequential execution...")
        
        # Fallback: sequential execution
        fallback_pbar = tqdm(
            tuning_tasks,
            desc="Sequential Training",
            unit="model",
            position=0
        )
        
        for name, model_class, param_config, X, y, learning_type, hardware in fallback_pbar:
            fallback_pbar.set_description(f"Training {name}")
            try:
                result = tune_single_model(
                    name, model_class, param_config, X, y, learning_type, hardware, 5, True
                )
                results.append(result)
                progress_tracker.complete_model()
            except Exception as e2:
                logger.error(f"✗ [{name}] Sequential tuning failed: {e2}")
                results.append((name, {}, 0.0))
                progress_tracker.complete_model()
        
        fallback_pbar.close()
    
    # Train final models with progress
    print("\n🔨 Training final models with optimized parameters...")
    
    final_pbar = tqdm(
        results,
        desc="Final Training",
        unit="model",
        position=0
    )
    
    for model_name, best_params, best_score in final_pbar:
        final_pbar.set_description(f"Training {model_name}")
        
        try:
            # Create model with best parameters
            tuned_model = create_model_with_params(model_name, learning_type, hardware, best_params)
            
            # Train final model
            if y is not None:
                tuned_model.fit(X, y)
            else:
                tuned_model.fit(X)
            
            trained[model_name] = tuned_model
            best_params_dict[model_name] = best_params
            
        except Exception as e:
            logger.error(f"✗ {model_name} final training failed: {e}")
    
    final_pbar.close()
    
    # Save best parameters
    if ipc.output_folder:
        params_path = os.path.join(ipc.output_folder, "best_hyperparameters.json")
        with open(params_path, 'w') as f:
            json.dump(best_params_dict, f, indent=4)
        print(f"\n💾 Best hyperparameters saved to: {params_path}")
    
    print_progress_summary()
    
    return trained


def train_with_tuning(models_dict, X, y, learning_type, hardware, ipc: InputConfiguration):
    """
    Sequential training with hyperparameter tuning (legacy mode).
    Includes progress tracking.
    """
    logger.warning("Using sequential training mode.")
    trained = {}
    best_params_dict = {}
    
    # Load hyperparameter config
    hp_config = load_hyperparameter_config()
    
    # Initialize progress
    progress_tracker.start(len(models_dict))
    print_progress_header()
    
    # Create progress bar
    model_pbar = tqdm(
        models_dict.items(),
        desc="Training Models",
        unit="model",
        position=0
    )
    
    for name, model in model_pbar:
        model_pbar.set_description(f"Training {name}")
        
        try:
            # Get hyperparameter config for this model
            param_config = hp_config.get(name, {})
            model_class = get_model_class(name, learning_type, hardware)
            
            # Tune hyperparameters
            _, best_params, _ = tune_single_model(
                name, model_class, param_config, X, y, learning_type, hardware, n_trials=30, show_progress=True
            )
            
            # Create model with best parameters
            tuned_model = create_model_with_params(name, learning_type, hardware, best_params)
            
            # Train final model
            if y is not None:
                tuned_model.fit(X, y)
            else:
                tuned_model.fit(X)
            
            trained[name] = tuned_model
            best_params_dict[name] = best_params
            progress_tracker.complete_model()
            
        except Exception as e:
            logger.error(f"✗ {name} training failed: {e}")
            progress_tracker.complete_model()
    
    model_pbar.close()
    
    # Save best parameters
    if ipc.output_folder:
        params_path = os.path.join(ipc.output_folder, "best_hyperparameters.json")
        with open(params_path, 'w') as f:
            json.dump(best_params_dict, f, indent=4)
        print(f"\n💾 Best hyperparameters saved to: {params_path}")
    
    print_progress_summary()
    
    return trained


def train_without_tuning(models_dict, X, y):
    """Train models with default parameters (no tuning) with progress tracking."""
    trained = {}
    
    print_progress_header()
    print("⚠️  Training with default parameters (no hyperparameter tuning)\n")
    
    # Create progress bar
    pbar = tqdm(
        models_dict.items(),
        desc="Training Models",
        unit="model"
    )
    
    for name, model in pbar:
        pbar.set_description(f"Training {name}")
        try:
            if y is not None:
                model.fit(X, y)
            else:
                model.fit(X)
            trained[name] = model
        except Exception as e:
            logger.error(f"✗ {name} training failed: {e}")
    
    pbar.close()
    print("\n✅ Training complete!\n")
    
    return trained


def train_cpu(models, X, y, ipc: InputConfiguration):
    """Train CPU models."""
    if ipc.hyper_parameter_tuning:
        return train_with_tuning_parallel(models, X, y, ipc.learning_type, Hardware.CPU, ipc)
    else:
        return train_without_tuning(models, X, y)


def train_gpu(models, X, y, ipc: InputConfiguration):
    """Train GPU models."""
    if ipc.hyper_parameter_tuning:
        return train_with_tuning_parallel(models, X, y, ipc.learning_type, Hardware.GPU, ipc)
    else:
        return train_without_tuning(models, X, y)


def run_train(ipc: InputConfiguration, X: pd.DataFrame, y=None): 
    """Train all models with comprehensive progress tracking."""
    
    cpu_models = CPU_MODELS[ipc.learning_type].copy()
    trained_cpu = train_cpu(cpu_models, X, y, ipc)

    # Only run GPU models if GPU hardware is requested
    if ipc.acceleration_hardware == Hardware.GPU:
        gpu_models = GPU_MODELS[ipc.learning_type].copy()
        trained_gpu = train_gpu(gpu_models, X, y, ipc)
        return {**trained_cpu, **trained_gpu}

    return trained_cpu
