# AutoML Platform - Complete Module & Tech Stack Documentation

## Executive Summary

This is a **professional-grade AutoML system** built with a modern tech stack that combines:
- **Frontend:** Next.js 16 + React 19 + TypeScript + Tailwind CSS
- **Backend:** FastAPI + Python 3.10+ with WebSocket real-time updates
- **ML Pipeline:** 15+ algorithms with automatic preprocessing and hyperparameter tuning
- **LLM Integration:** Google Gemini 2.0 Flash for intelligent data analysis
- **Storage:** JSON file system with joblib model serialization

---

## Part 1: Complete Tech Stack

### Backend Technologies

```
┌─────────────────────────────────────────────────────────┐
│ Backend Technology Stack                                │
├─────────────────────────────────────────────────────────┤
│ Language:              Python 3.10+                     │
│ API Framework:         FastAPI 0.104.1                  │
│ ASGI Server:          Uvicorn 0.24.0                   │
│ HTTP Client:          Requests 2.31+                   │
│ Async Support:        AsyncIO (Python native)          │
├─────────────────────────────────────────────────────────┤
│ ML & Data Processing:                                   │
│ ├─ Scikit-learn 1.3.2 (8+ algorithms)                  │
│ ├─ XGBoost 2.0.3 (gradient boosting)                   │
│ ├─ CatBoost 1.2.2 (categorical boosting)               │
│ ├─ Optuna 3.14.0 (hyperparameter tuning)               │
│ ├─ Pandas 2.1.3 (data manipulation)                    │
│ ├─ NumPy 1.26.2 (numerical computing)                  │
│ ├─ Feature-Engine 1.6.1 (feature engineering)          │
│ ├─ PyTorch 2.1.1 (neural networks)                     │
│ ├─ Chardet 5.2.0 (encoding detection)                  │
│ └─ Tqdm 4.66.1 (progress bars)                         │
├─────────────────────────────────────────────────────────┤
│ LLM & AI:                                               │
│ └─ Google Generative AI 0.4.0 (Gemini API)             │
├─────────────────────────────────────────────────────────┤
│ File Handling:                                          │
│ ├─ Openpyxl 3.11.0 (Excel files)                       │
│ ├─ JSON (native Python)                                │
│ ├─ CSV (pandas native)                                 │
│ ├─ XML (pandas native)                                 │
│ └─ Parquet (pandas native)                             │
├─────────────────────────────────────────────────────────┤
│ Configuration & Serialization:                          │
│ ├─ Pydantic 2.5.0 (data validation)                    │
│ ├─ Joblib 1.3.2 (model persistence)                    │
│ ├─ Python-dotenv 1.0.0 (env variables)                 │
│ └─ Python-multipart 0.0.6 (file uploads)               │
└─────────────────────────────────────────────────────────┘
```

### Frontend Technologies

```
┌─────────────────────────────────────────────────────────┐
│ Frontend Technology Stack                               │
├─────────────────────────────────────────────────────────┤
│ Framework:            Next.js 16                        │
│ React:               19.2 (Canary - latest)            │
│ Language:            TypeScript 5.3+                   │
│ Build Tool:          Turbopack (stable in Next.js 16)  │
├─────────────────────────────────────────────────────────┤
│ Styling:                                                │
│ ├─ Tailwind CSS 3.4+ (utility-first CSS)               │
│ ├─ Tailwind CSS Forms (form styling)                   │
│ ├─ Tailwind CSS Typography (text styling)              │
│ └─ CSS Modules (custom styles)                         │
├─────────────────────────────────────────────────────────┤
│ UI Components:                                          │
│ ├─ Shadcn/ui (35+ components)                          │
│ │  ├─ Card, Button, Input, Select                      │
│ │  ├─ Dialog, Toast, Progress                          │
│ │  ├─ Form, Textarea, Checkbox                         │
│ │  └─ ... and 25+ more                                 │
│ ├─ Lucide Icons (300+ icons)                           │
│ └─ Radix UI (headless components base)                 │
├─────────────────────────────────────────────────────────┤
│ HTTP & Real-time:                                       │
│ ├─ Fetch API (native browser)                          │
│ ├─ WebSocket API (native browser)                      │
│ └─ FormData (file uploads)                             │
├─────────────────────────────────────────────────────────┤
│ Routing:                                                │
│ ├─ Next.js App Router (file-based routing)             │
│ ├─ Dynamic Routes ([param])                            │
│ ├─ API Routes (/api/*)                                 │
│ └─ Layout Nesting                                      │
├─────────────────────────────────────────────────────────┤
│ State Management:                                       │
│ ├─ React Hooks (useState, useEffect, useRef)           │
│ ├─ Context API (optional)                              │
│ └─ Browser LocalStorage (session data)                 │
├─────────────────────────────────────────────────────────┤
│ Build & Deploy:                                         │
│ ├─ Node.js 18+ (runtime)                               │
│ ├─ npm/yarn (package manager)                          │
│ └─ Vercel (recommended deployment)                     │
└─────────────────────────────────────────────────────────┘
```

### Infrastructure & DevOps

```
┌─────────────────────────────────────────────────────────┐
│ Infrastructure Technologies                             │
├─────────────────────────────────────────────────────────┤
│ Containerization:                                       │
│ ├─ Docker (container runtime)                          │
│ └─ Docker Compose 3.9 (orchestration)                  │
├─────────────────────────────────────────────────────────┤
│ Runtime:                                                │
│ ├─ Python 3.10+ (backend)                              │
│ ├─ Node.js 18+ (frontend)                              │
│ ├─ NVIDIA CUDA (GPU support, optional)                 │
│ └─ cuDNN (deep learning acceleration)                  │
├─────────────────────────────────────────────────────────┤
│ Deployment Targets:                                     │
│ ├─ Vercel (Next.js frontend)                           │
│ ├─ Railway/Render (FastAPI backend)                    │
│ ├─ Docker (containerized)                              │
│ └─ Heroku (alternative)                                │
└─────────────────────────────────────────────────────────┘
```

---

## Part 2: Backend Modules (9 Core Modules)

### Module 1: main.py - FastAPI Application Server

**Location:** `backend/main.py`  
**Size:** ~500 LOC  
**Python Version:** 3.10+

**Responsibilities:**
- Create FastAPI application instance
- Define all REST API endpoints
- Manage WebSocket connections
- Handle CORS (Cross-Origin Resource Sharing)
- Coordinate ML pipeline execution
- Broadcast training progress updates

**Key Dependencies:**
```python
from fastapi import FastAPI, WebSocket, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from pathlib import Path
```

**Main Classes:**

```python
class ConnectionManager:
    """Manages WebSocket connections per project"""
    - active_connections: dict[str, WebSocket]
    - project_status: dict[str, dict]
    - Methods:
      * connect(websocket, project_name)
      * disconnect(project_name)
      * broadcast(project_name, message)
      * get_project_status(project_name)
      * update_project_status(project_name, status)
```

**Endpoints Provided (14 total):**

| HTTP Method | Endpoint | Purpose | Returns |
|------------|----------|---------|---------|
| GET | `/api/health` | System status | GPU info, CPU count |
| GET | `/api/env-status` | LLM config status | Config status |
| POST | `/api/setup-llm` | Configure LLM | Success message |
| POST | `/api/upload` | Upload CSV | File path, metadata |
| POST | `/api/analyze` | Analyze data | Analysis report |
| POST | `/api/train` | Start training | Project ID, status |
| GET | `/api/projects` | List all projects | Project list |
| GET | `/api/project/{name}` | Get project details | Project metadata |
| GET | `/api/project/{name}/report` | Full report | Complete analysis |
| GET | `/api/project/{name}/files` | List files | File list |
| POST | `/api/predict/{name}` | Make predictions | Results CSV |
| GET | `/api/project/{name}/download` | Download scores | Evaluation JSON |
| DELETE | `/api/project/{name}` | Delete project | Success status |
| WS | `/ws/{project}` | WebSocket updates | Real-time messages |

**Key Functions:**

```python
async def run_training_pipeline(project_name, config):
    """Main training orchestration (background task)"""
    # 1. Load data
    # 2. Run intelligent analysis
    # 3. Preprocess (if enabled)
    # 4. Train models in parallel
    # 5. Evaluate all models
    # 6. Save results
    # 7. Broadcast completion via WebSocket
```

---

### Module 2: intelligent_data_analyzer.py - LLM Data Analysis

**Location:** `backend/intelligent_data_analyzer.py`  
**Size:** ~400 LOC  
**Purpose:** Analyze data using Google Gemini AI  
**Technology:** Google Generative AI API

**Responsibilities:**
- Examine dataset structure and quality
- Detect data types and distributions
- Identify missing values and outliers
- Recommend preprocessing strategies
- Suggest feature engineering approaches
- Use LLM to understand domain patterns

**Key Class:**

```python
class IntelligentDataAnalyzer:
    def __init__(self, llm_model_name: str, llm_api_key: str):
        self.model = genai.GenerativeModel(llm_model_name)
    
    Methods:
    - analyze_dataset(df) → analysis_dict
    - generate_preprocessing_prompt(analysis) → str
    - suggest_features(df) → list[dict]
    - detect_data_quality() → quality_report
    - identify_patterns() → patterns_list
```

**Analysis Report Includes:**

```python
{
    "dataset_overview": {
        "shape": (15000, 23),
        "total_cells": 345000,
        "memory_usage_mb": 12.5
    },
    "column_analysis": {
        "numeric_features": 15,
        "categorical_features": 8,
        "datetime_features": 0,
        "columns": [...]
    },
    "data_quality": {
        "missing_percent": 2.1,
        "duplicates": 45,
        "outliers_detected": True
    },
    "statistical_summary": {
        "mean": {...},
        "std": {...},
        "min": {...},
        "max": {...}
    },
    "preprocessing_recommendations": [
        "Impute 'age' with median",
        "Scale 'income' with StandardScaler",
        "One-hot encode 'category'",
        ...
    ],
    "feature_engineering_suggestions": [
        "Create 'age_income_ratio'",
        "Add 'tenure_squared'",
        ...
    ]
}
```

**LLM Prompts Used:**

```python
ANALYZE_DATASET = """
Analyze this dataset:
- Shape: {rows} rows, {cols} columns
- Missing: {missing}%
- Data types: {dtypes}

Provide:
1. Data quality assessment
2. Feature meanings
3. Potential preprocessing steps
4. Feature engineering ideas
"""

FEATURE_ENGINEERING = """
Dataset characteristics: {stats}

Suggest 5-10 engineered features:
1. Ratios between columns
2. Interaction terms
3. Domain-specific features
"""
```

---

### Module 3: intelligent_data_processor.py - Feature Engineering Agent

**Location:** `backend/intelligent_data_processor.py`  
**Size:** ~600 LOC  
**Purpose:** Automated data preprocessing and feature engineering  
**Technologies:** Pandas, Scikit-learn, Feature-Engine

**Responsibilities:**
- Handle missing values (imputation)
- Encode categorical variables
- Engineer new features
- Handle outliers
- Scale/normalize features
- Remove low-variance features
- Apply feature selection

**Key Classes:**

```python
class TargetProcessor:
    """Handles target variable preparation"""
    - prepare_target(df, config) → y, encoding_info
    - handle_multiclass(y) → y_encoded
    - handle_regression(y) → y

class FeatureEngineeringEngine:
    """Creates derived features"""
    - create_features(df, suggestions) → new_features
    - add_polynomial_features(df) → df_with_poly
    - create_interactions(df) → df_with_interactions
    - add_domain_features(df, domain_knowledge) → df_enhanced

class DataPreprocessor:
    """Main preprocessing pipeline"""
    - impute_missing(df, strategy='mean') → df
    - encode_categorical(df, method='onehot') → df
    - scale_features(df, scaler='standard') → df, scaler
    - handle_outliers(df, method='winsorize') → df
    - remove_constants(df) → df
    - select_features(df, method='variance') → df, selected_cols
```

**Preprocessing Pipeline:**

```
Raw Data
  ↓
1. Canonicalize column names
  ↓
2. Separate target from features
  ↓
3. Handle missing values
  ├─ Numeric: mean/median/KNN
  └─ Categorical: mode/most_frequent
  ↓
4. Feature Engineering
  ├─ Create derived features
  ├─ Interactions (col1 * col2)
  ├─ Ratios (col1 / col2)
  └─ Polynomial (col² , √col)
  ↓
5. Encode Categorical Variables
  ├─ One-hot encoding (< 10 categories)
  ├─ Label encoding (> 10 categories)
  └─ Frequency encoding
  ↓
6. Handle Outliers
  ├─ Winsorization (clip at percentiles)
  └─ IQR method
  ↓
7. Scale/Normalize Features
  ├─ StandardScaler (mean=0, std=1)
  ├─ MinMaxScaler (0-1 range)
  └─ RobustScaler (resistant to outliers)
  ↓
8. Remove Low-Variance Features
  ├─ Constant features (1 unique value)
  └─ Quasi-constant (>99% same value)
  ↓
9. Feature Selection
  ├─ Correlation-based (remove duplicates)
  ├─ Variance threshold
  └─ Keep top N features
  ↓
Preprocessed Data Ready for Training
```

**Supported Imputation Strategies:**

| Strategy | Numeric | Categorical |
|----------|---------|-------------|
| mean | ✓ | ✗ |
| median | ✓ | ✗ |
| mode | ✓ | ✓ |
| most_frequent | ✓ | ✓ |
| KNN | ✓ | ✓ |
| forward_fill | ✓ | ✓ |
| backward_fill | ✓ | ✓ |

---

### Module 4: automl_pipeline.py - Training Orchestration

**Location:** `backend/automl_pipeline.py`  
**Size:** ~300 LOC  
**Purpose:** Orchestrate entire ML workflow  
**Technologies:** Scikit-learn, Pandas

**Responsibilities:**
- Coordinate data loading and preprocessing
- Manage train/test split
- Invoke model training
- Orchestrate hyperparameter tuning
- Collect and store results
- Save models and preprocessors

**Key Functions:**

```python
def preprocess_train(df: pd.DataFrame, config: InputConfiguration) -> dict:
    """
    Full pipeline: Analyze → Preprocess → Train → Evaluate
    
    Returns:
    {
        "trained_models": {...},
        "preprocessor": fitted_preprocessor,
        "evaluation_scores": {...},
        "best_model_name": "xgb",
        "X_train": processed_X_train,
        "X_test": processed_X_test,
        "y_train": y_train,
        "y_test": y_test,
        "feature_names": [...]
    }
    """

def train_only(df: pd.DataFrame, config: InputConfiguration) -> dict:
    """
    Skip preprocessing, train on raw data
    - Split data 80/20
    - Train models
    - Return results
    """

def load_and_prepare_data(df: pd.DataFrame, config: InputConfiguration):
    """
    Split data into train/test
    - Handle stratification for classification
    - Ensure reproducibility (random_state=42)
    - Return X_train, X_test, y_train, y_test
    """
```

**Data Split Logic:**

```python
from sklearn.model_selection import train_test_split, StratifiedShuffleSplit

# Regression or clustering
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42
)

# Classification (stratified)
splitter = StratifiedShuffleSplit(
    n_splits=1,
    test_size=0.2,
    random_state=42
)
```

---

### Module 5: model_registry.py - Model Training & Evaluation

**Location:** `backend/model_registry.py`  
**Size:** ~800 LOC  
**Purpose:** Train multiple models, tune, and evaluate  
**Technologies:** Scikit-learn, XGBoost, CatBoost, Optuna, concurrent.futures

**Responsibilities:**
- Train 8+ algorithms in parallel
- Perform hyperparameter tuning with Optuna
- Calculate comprehensive evaluation metrics
- Compare model performances
- Select best model
- Save all model artifacts

**Key Classes:**

```python
class ProgressTracker:
    """Track training progress"""
    - __init__(total_models)
    - update(increment=1)
    - get_progress() → int (0-100)

class ModelTrainer:
    """Train multiple models"""
    
    def train_classification_models(X_train, y_train, config):
        """Train 8 classification algorithms"""
        Returns: {model_name: fitted_model, ...}
    
    def train_regression_models(X_train, y_train, config):
        """Train 8 regression algorithms"""
    
    def train_clustering_models(X, config):
        """Train clustering algorithms"""
    
    def hyperparameter_tuning(X_train, y_train, model_class, config):
        """Bayesian optimization with Optuna"""
        Returns: best_params, best_score

class ModelEvaluator:
    """Evaluate model performance"""
    
    def evaluate_classification(y_true, y_pred, y_proba=None):
        """Calculate classification metrics"""
    
    def evaluate_regression(y_true, y_pred):
        """Calculate regression metrics"""
    
    def evaluate_clustering(X, labels):
        """Calculate clustering metrics"""
```

**Classification Algorithms Trained:**

```python
Models = [
    ('logistic', LogisticRegression(max_iter=1000)),
    ('svm', SVC(kernel='rbf', probability=True)),
    ('rf', RandomForestClassifier(n_estimators=100, n_jobs=-1)),
    ('gb', GradientBoostingClassifier(n_estimators=100)),
    ('xgb', XGBClassifier(n_estimators=100, tree_method='hist')),
    ('catboost', CatBoostClassifier(iterations=100, verbose=0)),
    ('mlp', MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=500)),
    ('dt', DecisionTreeClassifier(max_depth=10))
]
```

**Regression Algorithms Trained:**

```python
Models = [
    ('linear', LinearRegression()),
    ('ridge', Ridge(alpha=1.0)),
    ('lasso', Lasso(alpha=0.1)),
    ('svr', SVR(kernel='rbf')),
    ('rf', RandomForestRegressor(n_estimators=100)),
    ('gb', GradientBoostingRegressor(n_estimators=100)),
    ('xgb', XGBRegressor(n_estimators=100)),
    ('catboost', CatBoostRegressor(iterations=100, verbose=0)),
    ('mlp', MLPRegressor(hidden_layer_sizes=(100, 50)))
]
```

**Classification Metrics Calculated:**

```python
{
    "accuracy": accuracy_score(y_true, y_pred),
    "precision": precision_score(y_true, y_pred, average='weighted'),
    "recall": recall_score(y_true, y_pred, average='weighted'),
    "f1": f1_score(y_true, y_pred, average='weighted'),
    "roc_auc": roc_auc_score(y_true, y_proba, multi_class='ovr'),
    "confusion_matrix": confusion_matrix(y_true, y_pred),
    "classification_report": classification_report(y_true, y_pred)
}
```

**Regression Metrics Calculated:**

```python
{
    "r2": r2_score(y_true, y_pred),
    "mae": mean_absolute_error(y_true, y_pred),
    "mse": mean_squared_error(y_true, y_pred),
    "rmse": np.sqrt(mean_squared_error(y_true, y_pred)),
    "explained_variance": explained_variance_score(y_true, y_pred),
    "mean_absolute_percentage_error": mean_absolute_percentage_error(y_true, y_pred)
}
```

**Clustering Metrics Calculated:**

```python
{
    "silhouette_score": silhouette_score(X, labels),
    "calinski_harabasz_score": calinski_harabasz_score(X, labels),
    "davies_bouldin_score": davies_bouldin_score(X, labels)
}
```

**Parallel Training:**

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

with ThreadPoolExecutor(max_workers=8) as executor:
    futures = {
        executor.submit(train_model, model_class, X_train, y_train): name
        for name, model_class in models.items()
    }
    
    results = {}
    for future in as_completed(futures):
        model_name = futures[future]
        results[model_name] = future.result()
```

**Hyperparameter Tuning with Optuna:**

```python
import optuna

def objective(trial, X_train, y_train, model_class):
    # Define search space
    params = {
        'n_estimators': trial.suggest_int('n_estimators', 50, 300),
        'max_depth': trial.suggest_int('max_depth', 3, 15),
        'learning_rate': trial.suggest_float('learning_rate', 0.001, 0.3),
        'subsample': trial.suggest_float('subsample', 0.6, 1.0)
    }
    
    # Train and evaluate
    model = model_class(**params)
    model.fit(X_train, y_train)
    score = cross_val_score(model, X_train, y_train, cv=5).mean()
    
    return score

# Run optimization
study = optuna.create_study(direction='maximize')
study.optimize(objective, n_trials=30)
best_params = study.best_params
```

---

### Module 6: cognitive_engine.py - LLM Interface

**Location:** `backend/cognitive_engine.py`  
**Size:** ~200 LOC  
**Purpose:** Interface with Google Gemini AI  
**Technology:** google-generativeai==0.4.0

**Responsibilities:**
- Send requests to Google Gemini API
- Parse LLM responses
- Generate intelligent insights
- Create feature suggestions
- Handle API errors gracefully

**Key Class:**

```python
class CognitiveEngine:
    def __init__(self, model_name: str, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
    
    Methods:
    - analyze_data(dataset_info: dict) → analysis_dict
    - generate_insights(analysis: dict) → str
    - suggest_features(dataset_info: dict) → list[dict]
    - handle_errors(error: Exception) → str
    - chat(prompt: str) → response: str
```

**LLM Configuration:**

```python
LLM_MODEL_NAME = "gemini-2.0-flash"
LLM_API_KEY = os.getenv("LLM_API_KEY")

genai.configure(api_key=LLM_API_KEY)
model = genai.GenerativeModel(LLM_MODEL_NAME)
```

**API Capabilities:**

- **Max Tokens:** 2,000
- **Temperature:** 0.7 (balanced creativity)
- **Timeout:** 30 seconds
- **Rate Limits:** 15 requests per minute (free tier)

---

### Module 7: file_handler.py - File I/O Operations

**Location:** `backend/file_handler.py`  
**Size:** ~250 LOC  
**Purpose:** Handle file uploads and data loading  
**Technologies:** Pandas, Chardet, Openpyxl

**Responsibilities:**
- Detect file format automatically
- Parse various file types
- Validate file integrity
- Clean up temporary files
- Handle encoding issues

**Supported Formats:**

```python
def open_file(file_path: str) -> pd.DataFrame:
    """Auto-detect and parse file"""
    
    Supported:
    - .csv (Comma-Separated Values)
    - .json (JSON)
    - .xlsx, .xls (Excel)
    - .xml (XML)
    - .parquet (Parquet columnar)
    - .tsv (Tab-Separated)
    - .txt (Plain text with delimiters)
    
    Returns: pandas DataFrame
```

**File Format Detection:**

```python
def detect_file_format(file_path: str) -> str:
    """Detect format from extension or content"""
    
    # 1. Check file extension
    # 2. If ambiguous, read first bytes
    # 3. Return format type
```

**Encoding Handling:**

```python
import chardet

# Auto-detect encoding
with open(file_path, 'rb') as f:
    result = chardet.detect(f.read())
    encoding = result['encoding']

# Read with detected encoding
df = pd.read_csv(file_path, encoding=encoding)
```

---

### Module 8: data_pre_processor.py - Column Standardization

**Location:** `backend/data_pre_processor.py`  
**Size:** ~100 LOC  
**Purpose:** Standardize column names  
**Technology:** Pandas

**Responsibilities:**
- Convert column names to lowercase
- Replace spaces with underscores
- Remove special characters
- Handle duplicate column names
- Ensure valid Python identifiers

**Key Function:**

```python
def canonicalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize column names
    
    Example transformations:
    - "Customer Name" → "customer_name"
    - "Sales $$$" → "sales"
    - "2024 Revenue" → "revenue_2024"
    - "Age (years)" → "age_years"
    """
```

---

### Module 9: services.py - Service Layer

**Location:** `backend/services.py`  
**Size:** ~400 LOC  
**Purpose:** High-level business logic  
**Technology:** Pandas, Joblib

**Responsibilities:**
- Create project directories
- Save/load projects
- Run complete AutoML pipeline
- Handle predictions
- Manage project lifecycle

**Key Functions:**

```python
def create_new_project_folder(project_name: str) -> Path:
    """Create project directory structure"""
    Returns: Path to project folder

def run_automl(df: pd.DataFrame, config: InputConfiguration) -> dict:
    """Execute complete AutoML pipeline"""
    Returns: results dict with models, scores, etc.

def restore_session(project_name: str) -> dict:
    """Load previously trained project"""
    Returns: loaded models and preprocessor

def predict_new_data(df: pd.DataFrame, project_folder: str) -> pd.DataFrame:
    """Apply trained model to new data"""
    Returns: predictions DataFrame

def save_project(project_name: str, results: dict, config: InputConfiguration):
    """Save all project artifacts"""
    Saves: models, preprocessor, metadata, scores

def get_project_metadata(project_name: str) -> dict:
    """Retrieve project information"""
    Returns: metadata dict
```

**Project Directory Structure:**

```
projects/
└── churn_prediction_20250207_143022/
    ├── metadata.json              # Config & results
    ├── best_model.pkl             # Best trained model
    ├── data_prep.pkl              # Preprocessor
    ├── ipc.pkl                    # Input config
    ├── evaluation_scores.json      # All metrics
    ├── preprocessing_config.json   # LLM recommendations
    ├── report.json                # Data analysis
    ├── X_train.csv                # Training features
    ├── y_train.csv                # Training labels
    ├── X_test.csv                 # Test features
    ├── y_test.csv                 # Test labels
    ├── train_data.csv             # Full training set
    ├── test_data.csv              # Full test set
    └── models/                    # All trained models
        ├── logistic_model.pkl
        ├── svm_model.pkl
        ├── rf_model.pkl
        ├── gb_model.pkl
        ├── xgb_model.pkl
        ├── catboost_model.pkl
        ├── mlp_model.pkl
        └── dt_model.pkl
```

### Module 10: core/models.py - Data Models

**Location:** `backend/core/models.py`  
**Size:** ~150 LOC  
**Purpose:** Pydantic data validation models  
**Technology:** Pydantic 2.5+

**Key Classes:**

```python
class MLType(str, Enum):
    SUPERVISED = "supervised"
    UNSUPERVISED = "unsupervised"

class LearningType(str, Enum):
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"

class ProcessingType(str, Enum):
    PREPROCESS_TRAIN = "preprocess_train"
    TRAIN_ONLY = "train_only"

class Hardware(str, Enum):
    CPU = "cpu"
    GPU = "gpu"

class InputConfiguration(BaseModel):
    project_name: str
    file_name: str
    ml_type: MLType
    learning_type: LearningType
    processing_type: ProcessingType
    llm_name: str
    target_column: Optional[str] = None
    index_column: Optional[str] = None
    output_folder: Optional[str] = None
    acceleration_hardware: Hardware = Hardware.CPU
    test_size: Optional[float] = 0.2
    hyper_parameter_tuning: bool = False
```

### Module 11: prompts.py - LLM Prompts

**Location:** `backend/prompts.py`  
**Size:** ~150 LOC  
**Purpose:** Store LLM prompt templates  
**Technology:** Python strings with formatting

**Key Prompts:**

```python
ANALYZE_DATASET = """
Analyze this dataset and provide insights:
[Dataset info]
Provide:
1. Data quality assessment
2. Feature analysis
3. Preprocessing recommendations
4. Feature engineering ideas
"""

SUGGEST_FEATURES = """
Based on these dataset characteristics:
[Stats]
Suggest 5-10 feature engineering ideas
"""

ERROR_EXPLANATION = """
Convert this error into user-friendly explanation:
[Error message]
"""
```

---

## Part 3: Frontend Modules (7 Pages)

### Frontend Technologies Summary

```
┌─────────────────────────────────────────┐
│ Next.js 16 Frontend Stack               │
├─────────────────────────────────────────┤
│ Framework:    Next.js 16                │
│ React:        19.2 (Canary)             │
│ TypeScript:   5.3+                      │
│ CSS:          Tailwind 3.4+ + Shadcn   │
│ Icons:        Lucide (300+)             │
│ HTTP:         Fetch API (native)        │
│ WebSocket:    Native WebSocket API      │
│ State:        React Hooks               │
│ Build:        Turbopack (stable)        │
└─────────────────────────────────────────┘
```

### Frontend Pages

#### Page 1: Home (app/page.tsx)

**Purpose:** Dashboard and system overview  
**Components:** Card, Button, Badge, Icons  
**State:** healthStatus, envStatus  
**APIs Called:** /api/health, /api/env-status

```typescript
// Key displays:
- GPU/CPU status
- LLM configuration status
- Quick start button
- Feature highlights
```

#### Page 2: Setup (app/setup/page.tsx)

**Purpose:** LLM configuration  
**Components:** Form, Input, Button  
**State:** modelName, apiKey  
**APIs Called:** /api/setup-llm

```typescript
// Functionality:
- Enter LLM model name
- Paste API key
- Save to backend .env
- Validate configuration
```

#### Page 3: Train (app/train/page.tsx)

**Purpose:** 3-step training wizard  
**Components:** Card, Input, Select, Button, Progress  
**State:** step, file, formConfig, analysis

```typescript
// Step 1: File Upload
- Drag-drop or click
- API: POST /api/upload
- Display file metadata

// Step 2: Configuration
- Select ML Type
- Select Learning Type
- Enter target column
- Choose preprocessing mode
- Enable hyperparameter tuning

// Step 3: Review
- Display configuration
- Confirm and submit
- API: POST /api/train
- Redirect to training dashboard
```

#### Page 4: Training Dashboard (app/training/[project]/page.tsx)

**Purpose:** Real-time training progress  
**Components:** Progress, Card, Button, Logs  
**State:** progress, status, logs, result, error  
**Connection:** WebSocket to `/ws/{project}`

```typescript
// Real-time displays:
- Progress bar (0-100%)
- Status messages
- Live training logs
- Error handling
- Results display when complete

// WebSocket handling:
- Connect to ws://localhost:8000/ws/{project}
- Parse messages (status/complete/error)
- Update UI in real-time
```

#### Page 5: Projects (app/projects/page.tsx)

**Purpose:** View all trained projects  
**Components:** Table, Button, Dialog  
**State:** projects, selectedProject

```typescript
// Features:
- List all projects
- Show creation date, status, best model
- Click to view details
- Delete project button
- Sort/filter options
- API: GET /api/projects
```

#### Page 6: Project Details (app/project-details/[project]/page.tsx)

**Purpose:** View project results  
**Components:** Card, Table, Button, Tabs  
**State:** projectData, selectedTab

```typescript
// Displays:
- Project configuration
- All model metrics
- Best model performance
- Feature importance (if available)
- Download evaluation scores
- Link to predictions page
- API: GET /api/project/{name}/report
```

#### Page 7: Predictions (app/predict/[project]/page.tsx)

**Purpose:** Make batch predictions  
**Components:** Form, Input, Table, Button  
**State:** csvData, predictions, isLoading

```typescript
// Workflow:
1. Upload CSV with same features
2. API: POST /api/predict/{project}
3. Display predictions table
4. Download predictions CSV
5. Show model used and confidence scores
```

---

## Part 4: Core Architecture Decisions

### Why These Technologies?

| Technology | Why Chosen |
|-----------|-----------|
| **FastAPI** | Modern, fast, built-in WebSocket, automatic API docs |
| **Next.js 16** | Latest App Router, Server Components, best DX |
| **React 19** | Latest features, better performance |
| **TypeScript** | Type safety, better IDE support, fewer bugs |
| **Tailwind CSS** | Utility-first, highly customizable, fast |
| **Scikit-learn** | Most popular ML library, stable, well-documented |
| **XGBoost/CatBoost** | State-of-art gradient boosting |
| **Optuna** | Best-in-class hyperparameter optimization |
| **Google Gemini** | Fast, capable LLM with free tier |
| **Joblib** | Best for model serialization in Python |

### Design Patterns Used

1. **Factory Pattern** - Model creation (model_registry.py)
2. **Pipeline Pattern** - Data processing (automl_pipeline.py)
3. **Observer Pattern** - WebSocket broadcasts (ConnectionManager)
4. **Strategy Pattern** - Different preprocessing strategies
5. **Singleton Pattern** - LLM client instance
6. **Async/Await** - Non-blocking operations
7. **Thread Pool** - Parallel model training

### Performance Optimizations

```
Backend:
- Parallel model training (8 threads)
- Async WebSocket updates
- Batch predictions
- Joblib model compression
- In-memory caching

Frontend:
- Code splitting (per-page)
- Image optimization
- Lazy component loading
- Efficient state management
- Minimal re-renders
```

---

## Part 5: Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ USER INTERFACE (Next.js)                                    │
└────────────────┬────────────────────────────────────────────┘
                 │
         ┌───────┴────────┐
         │                │
    Upload File      WebSocket Connection
    (multipart)       (ws://...)
         │                │
┌────────┴────────────────┴─────────────────────────────────┐
│ FASTAPI REST API (main.py)                                │
│ ┌──────────────────────────────────────────────────────┐ │
│ │ /api/upload → Save temp file                        │ │
│ │ /api/analyze → Run IntelligentDataAnalyzer          │ │
│ │ /api/train → Start async training                   │ │
│ │ /ws/{project} → Broadcast updates                   │ │
│ └──────────────────────────────────────────────────────┘ │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────┴────────────────────────────────────────┐
│ ML PIPELINE ORCHESTRATOR (automl_pipeline.py)          │
│ ┌────────────────────────────────────────────────────┐ │
│ │ 1. intelligent_data_analyzer.py                   │ │
│ │    ├─ Load data (file_handler.py)                 │ │
│ │    ├─ Analyze structure                           │ │
│ │    └─ Call LLM (cognitive_engine.py)              │ │
│ │                                                   │ │
│ │ 2. intelligent_data_processor.py (if enabled)    │ │
│ │    ├─ Impute missing values                       │ │
│ │    ├─ Encode categoricals                         │ │
│ │    ├─ Engineer features                           │ │
│ │    ├─ Scale/normalize                             │ │
│ │    └─ Select features                             │ │
│ │                                                   │ │
│ │ 3. model_registry.py                              │ │
│ │    ├─ Train 8 models in parallel (ThreadPool)    │ │
│ │    ├─ Optional: Hyperparameter tuning (Optuna)   │ │
│ │    ├─ Evaluate each model                         │ │
│ │    └─ Select best model                           │ │
│ │                                                   │ │
│ │ 4. services.py                                    │ │
│ │    ├─ Save all artifacts                          │ │
│ │    ├─ Save metadata.json                          │ │
│ │    └─ Save models/ directory                      │ │
│ └────────────────────────────────────────────────────┘ │
└────────────┬──────────────────────────────────────────┘
             │
     ┌───────┴────────┐
     │                │
  Broadcast        Save Results
  Progress         (projects/)
  via WS           
     │                │
     └────────────────┴─────────────────────────────┐
                                                    │
┌───────────────────────────────────────────────────┴─┐
│ FILE SYSTEM STORAGE                                 │
├─────────────────────────────────────────────────────┤
│ projects/                                           │
│ └── churn_prediction_20250207_143022/              │
│     ├── metadata.json (config + results)           │
│     ├── best_model.pkl (trained model)             │
│     ├── data_prep.pkl (preprocessor)               │
│     ├── evaluation_scores.json (all metrics)       │
│     ├── X_train.csv, y_train.csv                   │
│     ├── X_test.csv, y_test.csv                     │
│     └── models/ (all trained models)               │
│         ├── xgb_model.pkl                          │
│         ├── catboost_model.pkl                     │
│         └── ...                                    │
└─────────────────────────────────────────────────────┘
```

---

## Part 6: Summary

### Complete Module List

| Module | Type | Size | Purpose | Tech |
|--------|------|------|---------|------|
| main.py | Backend | 500 LOC | FastAPI server | FastAPI, AsyncIO |
| intelligent_data_analyzer.py | Backend | 400 LOC | LLM analysis | Gemini API |
| intelligent_data_processor.py | Backend | 600 LOC | Feature engineering | Pandas, Scikit-learn |
| automl_pipeline.py | Backend | 300 LOC | Training orchestration | Pandas |
| model_registry.py | Backend | 800 LOC | Model training | Scikit-learn, XGBoost |
| cognitive_engine.py | Backend | 200 LOC | LLM interface | google-generativeai |
| file_handler.py | Backend | 250 LOC | File I/O | Pandas, Chardet |
| data_pre_processor.py | Backend | 100 LOC | Column standardization | Pandas |
| services.py | Backend | 400 LOC | Business logic | Joblib |
| core/models.py | Backend | 150 LOC | Data models | Pydantic |
| prompts.py | Backend | 150 LOC | LLM prompts | Python |
| app/page.tsx | Frontend | 200 LOC | Home dashboard | Next.js, React |
| app/setup/page.tsx | Frontend | 150 LOC | LLM config | Next.js, Form |
| app/train/page.tsx | Frontend | 400 LOC | Training wizard | Next.js, Form |
| app/training/[project]/page.tsx | Frontend | 300 LOC | Progress dashboard | WebSocket |
| app/projects/page.tsx | Frontend | 250 LOC | Project list | Next.js |
| app/project-details/[project]/ | Frontend | 250 LOC | Results display | Next.js |
| app/predict/[project]/page.tsx | Frontend | 200 LOC | Predictions | Next.js |

### Total Codebase

- **Backend:** ~4,350 LOC (Python)
- **Frontend:** ~1,750 LOC (TypeScript/React)
- **Documentation:** ~3,000 LOC
- **Configuration:** 500 LOC
- **Total:** ~9,600 LOC

### Key Statistics

- **Algorithms:** 8+ classification, 8+ regression, 3+ clustering
- **API Endpoints:** 14 REST + 1 WebSocket
- **Data Formats:** 7 supported (CSV, JSON, Excel, XML, Parquet, TSV, TXT)
- **ML Libraries:** 8+ major libraries
- **UI Components:** 35+ from shadcn/ui
- **Deployment Options:** 4+ (Docker, Vercel, Railway, Render)

---

**End of Technical Documentation**
