# AutoML Platform - Technical Documentation

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Backend API](#backend-api)
3. [Frontend Architecture](#frontend-architecture)
4. [Data Flow](#data-flow)
5. [ML Pipeline](#ml-pipeline)
6. [Project Structure](#project-structure)
7. [Configuration](#configuration)
8. [Deployment](#deployment)
9. [Performance](#performance)
10. [Security](#security)

---

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js 16)                       │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐  │
│  │ Upload Form  │ Train Config  │ Live Progress Dashboard    │  │
│  │ Management   │ Re-prediction │ WebSocket Connection       │  │
│  └──────────────┴──────────────┴──────────────┴──────────────┘  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
        REST API      WebSocket          File Upload
    (JSON over HTTP)   (Binary Stream)   (Multipart)
         │                 │                 │
┌────────┴─────────────────┴─────────────────┴───────────────────┐
│               Backend (FastAPI + Uvicorn)                      │
│  ┌────────────────────────────────────────────────────────────┤
│  │ API Layer (REST Endpoints + WebSocket Manager)             │
│  │  • /api/upload, /api/analyze, /api/train                   │
│  │  • /api/predict, /api/project/*, /ws/{project}             │
│  ├────────────────────────────────────────────────────────────┤
│  │ ML Pipeline Orchestrator                                   │
│  │  ├─ IntelligentDataAnalyzer (LLM-powered)                  │
│  │  ├─ IntelligentDataProcessor (Feature engineering)         │
│  │  ├─ AutoMLPipeline (Training orchestration)                │
│  │  └─ ModelRegistry (Algorithm management)                   │
│  ├────────────────────────────────────────────────────────────┤
│  │ Supporting Services                                        │
│  │  ├─ CognitiveEngine (LLM Interface - Google Gemini)        │
│  │  ├─ FileHandler (CSV/JSON/XML/Excel parsing)               │
│  │  └─ Services Layer (Project management)                    │
│  └────────────────────────────────────────────────────────────┘
└────────────────────┬─────────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
    Projects    Models        Data Cache
    (JSON)     (Pickle)      (CSV/Parquet)
        │            │            │
┌───────┴────────────┴────────────┴─────────────────────────────┐
│              File System Storage (projects/)                  │
│  ├─ project_name_YYYYMMDD_HHMMSS/                            │
│  │  ├─ metadata.json (config + results)                      │
│  │  ├─ best_model.pkl (trained model)                        │
│  │  ├─ data_prep.pkl (preprocessor)                          │
│  │  ├─ evaluation_scores.json                                │
│  │  ├─ preprocessing_config.json                             │
│  │  ├─ models/ (all trained models)                          │
│  │  └─ data/ (train/test splits)                             │
└──────────────────────────────────────────────────────────────┘
```

### Component Architecture

```
Frontend (Next.js)
├── Pages
│   ├── / (Home)
│   ├── /setup (LLM Configuration)
│   ├── /train (Training Wizard)
│   ├── /training/[project] (Live Dashboard)
│   ├── /projects (History)
│   ├── /project-details/[project] (Results)
│   └── /predict/[project] (Predictions)
├── Components
│   ├── UI Components (shadcn/ui)
│   ├── Forms (Upload, Configuration)
│   ├── Progress Tracking
│   └── Results Display

Backend (FastAPI)
├── Core Layer
│   ├── models.py (Pydantic models, enums)
│   ├── main.py (FastAPI app, WebSocket, endpoints)
│   └── core/models.py (Data classes)
├── ML Pipeline Layer
│   ├── intelligent_data_analyzer.py (LLM analysis)
│   ├── intelligent_data_processor.py (Feature engineering)
│   ├── automl_pipeline.py (Training orchestration)
│   └── model_registry.py (Model training)
├── Support Layer
│   ├── cognitive_engine.py (LLM interface)
│   ├── file_handler.py (File I/O)
│   ├── services.py (Business logic)
│   ├── data_pre_processor.py (Data cleaning)
│   └── prompts.py (LLM prompts)
└── Configuration
    ├── hyper_parameter_config.json
    ├── requirements.txt
    └── .env
```

---

## Backend API

### API Server Configuration

**Framework:** FastAPI 0.104+  
**Server:** Uvicorn  
**Host:** 0.0.0.0  
**Port:** 8000  
**CORS:** Enabled for frontend localhost:3000

### Endpoint Reference

#### Health & Configuration

##### GET /api/health
Returns system status and GPU availability.

**Response:**
```json
{
  "status": "healthy",
  "gpu_available": true,
  "gpu_name": "NVIDIA RTX 3090",
  "cpu_count": 8,
  "memory_gb": 32
}
```

##### GET /api/env-status
Checks if LLM is configured.

**Response:**
```json
{
  "configured": true,
  "llm_model": "gemini-2.0-flash",
  "needs_setup": false
}
```

##### POST /api/setup-llm
Configure LLM credentials.

**Request:**
```json
{
  "llm_model": "gemini-2.0-flash",
  "llm_api_key": "your-api-key"
}
```

**Response:**
```json
{
  "status": "configured",
  "message": "LLM configured successfully"
}
```

#### Data Management

##### POST /api/upload
Upload CSV file for analysis.

**Request:** multipart/form-data
```
- file: CSV file (max 100MB)
```

**Response:**
```json
{
  "file_id": "upload_20250207_143022",
  "filename": "data.csv",
  "size": 1024000,
  "path": "/tmp/upload_20250207_143022.csv"
}
```

##### POST /api/analyze
Analyze uploaded data structure.

**Request:**
```json
{
  "file_path": "/tmp/upload_20250207_143022.csv",
  "target_column": "is_churned"
}
```

**Response:**
```json
{
  "rows": 15000,
  "columns": 23,
  "dtypes": {
    "age": "int64",
    "income": "float64",
    "name": "object"
  },
  "missing_percent": 2.1,
  "categorical_features": ["name", "category"],
  "numeric_features": ["age", "income"],
  "target_info": {
    "type": "binary_classification",
    "classes": [0, 1],
    "class_distribution": {0: 0.78, 1: 0.22}
  }
}
```

#### Training

##### POST /api/train
Start training pipeline.

**Request:**
```json
{
  "project_name": "churn_prediction",
  "file_name": "/tmp/upload_20250207_143022.csv",
  "ml_type": "supervised",
  "learning_type": "classification",
  "processing_type": "preprocess_train",
  "llm_name": "gemini-2.0-flash",
  "target_column": "is_churned",
  "index_column": "id",
  "output_folder": "projects/churn_prediction_20250207_143022",
  "acceleration_hardware": "auto",
  "test_size": 0.2,
  "hyper_parameter_tuning": true
}
```

**Response:**
```json
{
  "status": "training_started",
  "project_name": "churn_prediction",
  "project_id": "churn_prediction_20250207_143022",
  "message": "Check WebSocket /ws/churn_prediction for real-time updates"
}
```

**Background Process:**
- Starts async training on thread pool executor
- Updates via WebSocket `/ws/{project_name}`
- Duration: 2-30 minutes depending on data size and hyperparameter tuning

#### Project Management

##### GET /api/projects
List all trained projects.

**Response:**
```json
{
  "projects": [
    {
      "name": "churn_prediction_20250207_143022",
      "created_at": "2025-02-07T14:30:22",
      "status": "completed",
      "best_model": "xgb",
      "accuracy": 0.89
    }
  ],
  "count": 1
}
```

##### GET /api/project/{project_name}
Get project details and metadata.

**Response:**
```json
{
  "project_name": "churn_prediction_20250207_143022",
  "created_at": "2025-02-07T14:30:22",
  "status": "completed",
  "config": {
    "ml_type": "supervised",
    "learning_type": "classification",
    "processing_type": "preprocess_train",
    "target_column": "is_churned",
    "test_size": 0.2,
    "hyper_parameter_tuning": true
  },
  "best_model": "xgb",
  "models_trained": ["logistic", "svm", "rf", "gb", "xgb", "catboost"],
  "evaluation_scores": {
    "xgb": {
      "accuracy": 0.891,
      "precision": 0.876,
      "recall": 0.823,
      "f1": 0.848,
      "roc_auc": 0.923
    }
  }
}
```

##### GET /api/project/{project_name}/report
Get detailed analysis report.

**Response:**
```json
{
  "project_name": "churn_prediction_20250207_143022",
  "metadata": {...},
  "preprocessing_config": {
    "llm_analysis": "Data has 15% categorical features with high cardinality...",
    "steps_applied": ["imputation", "encoding", "scaling", "feature_engineering"],
    "features_engineered": 5
  },
  "evaluation_scores": {...}
}
```

##### GET /api/project/{project_name}/files
List all project files.

**Response:**
```json
{
  "exists": true,
  "files": [
    {"name": "best_model.pkl", "size": 2048000, "path": "best_model.pkl"},
    {"name": "data_prep.pkl", "size": 512000, "path": "data_prep.pkl"},
    {"name": "metadata.json", "size": 4096, "path": "metadata.json"},
    {"name": "evaluation_scores.json", "size": 2048, "path": "evaluation_scores.json"}
  ]
}
```

##### DELETE /api/project/{project_name}
Delete a project and all its files.

**Response:**
```json
{
  "status": "success",
  "message": "Project churn_prediction_20250207_143022 deleted"
}
```

#### Predictions

##### POST /api/predict/{project_name}
Make batch predictions on new data.

**Request:**
```json
{
  "csv_data": "age,income,name\n25,50000,John\n30,60000,Jane"
}
```

**Response:**
```json
{
  "status": "success",
  "predictions_count": 2,
  "results": [
    {"age": 25, "income": 50000, "name": "John", "prediction": 0, "probability": 0.12},
    {"age": 30, "income": 60000, "name": "Jane", "prediction": 1, "probability": 0.87}
  ],
  "csv_download": "age,income,name,prediction,probability\n25,50000,John,0,0.12\n..."
}
```

##### GET /api/project/{project_name}/download
Download evaluation scores JSON.

**Response:** JSON file (evaluation_scores.json)

### WebSocket: Real-Time Progress Updates

**Connection:** `WS ws://localhost:8000/ws/{project_name}`

**Message Format:**

Status Update:
```json
{
  "type": "status",
  "message": "Training XGBoost model...",
  "progress": 65,
  "current_model": "xgb",
  "elapsed_time": 120
}
```

Completion:
```json
{
  "type": "complete",
  "message": "✓ Training complete! Best model: XGBoost",
  "progress": 100,
  "result": {
    "best_model": "xgb",
    "models_trained": ["logistic", "svm", "rf", "gb", "xgb"],
    "evaluation_scores": {...}
  }
}
```

Error:
```json
{
  "type": "error",
  "message": "Training failed",
  "error": "CUDA out of memory. Falling back to CPU.",
  "details": "Full traceback..."
}
```

---

## Frontend Architecture

### Technology Stack

| Technology | Version | Purpose |
|-----------|---------|---------|
| Next.js | 16 | Framework & Routing |
| React | 19.2+ | UI Components |
| TypeScript | 5.3+ | Type Safety |
| Tailwind CSS | 3.4+ | Styling |
| shadcn/ui | Latest | Component Library |
| Lucide Icons | Latest | Icon Set |

### Page Components

#### Home Page (/)

**Purpose:** Dashboard and navigation hub

**Key Features:**
- System health check (GPU status)
- LLM configuration status
- Quick navigation buttons
- Feature highlights

**Data Flow:**
```
1. useEffect() runs health check endpoints
2. Display GPU status & config status
3. Provide navigation links
```

#### Setup Page (/setup)

**Purpose:** LLM configuration interface

**Features:**
- Text input for model name
- API key input (password masked)
- Form validation
- Save to .env

**Implementation:**
```tsx
const handleSave = async (model, apiKey) => {
  const response = await fetch(`${API_URL}/api/setup-llm`, {
    method: 'POST',
    body: JSON.stringify({llm_model: model, llm_api_key: apiKey})
  })
}
```

#### Training Page (/train)

**Purpose:** 3-step training wizard

**Steps:**
1. **File Upload** - Drag-drop or click to upload CSV
2. **Configuration** - Set ML task, target column, preprocessing mode
3. **Review** - Confirm settings before training

**Data Structure:**
```tsx
interface TrainingConfig {
  projectName: string
  file: File
  mlType: 'supervised' | 'unsupervised'
  learningType: 'classification' | 'regression' | 'clustering'
  processingType: 'preprocess_train' | 'train_only'
  targetColumn: string
  testSize: number
  hyperparameterTuning: boolean
}
```

**Form Submission:**
```tsx
const handleSubmit = async (config) => {
  // 1. Upload file
  const formData = new FormData()
  formData.append('file', config.file)
  const uploadRes = await fetch(`${API_URL}/api/upload`, {
    method: 'POST',
    body: formData
  })
  
  // 2. Analyze data
  const analyzeRes = await fetch(`${API_URL}/api/analyze`, {...})
  
  // 3. Start training
  const trainRes = await fetch(`${API_URL}/api/train`, {
    method: 'POST',
    body: JSON.stringify({...config, file_name: uploadRes.path})
  })
  
  // 4. Redirect to training dashboard
  router.push(`/training/${config.projectName}`)
}
```

#### Training Dashboard (/training/[project])

**Purpose:** Real-time training progress monitoring

**Key Components:**
- Progress bar (0-100%)
- Status messages
- Live logs from WebSocket
- Error handling
- Results display

**WebSocket Implementation:**
```tsx
useEffect(() => {
  const wsUrl = `ws://localhost:8000/ws/${projectName}`
  const ws = new WebSocket(wsUrl)
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    
    if (data.type === 'status') {
      setProgress(data.progress)
      setStatus(data.message)
      setLogs(prev => [...prev, data.message])
    }
    
    if (data.type === 'complete') {
      setCompleted(true)
      setResult(data.result)
    }
    
    if (data.type === 'error') {
      setError(data.error)
    }
  }
  
  return () => ws.close()
}, [projectName])
```

#### Projects Page (/projects)

**Purpose:** View all trained projects

**Features:**
- List of projects with metadata
- Click to view details
- Delete project button
- Sort by date/accuracy

**Data Fetching:**
```tsx
useEffect(() => {
  const fetchProjects = async () => {
    const res = await fetch(`${API_URL}/api/projects`)
    const data = await res.json()
    setProjects(data.projects)
  }
  fetchProjects()
}, [])
```

#### Project Details (/project-details/[project])

**Purpose:** View results and artifacts

**Displays:**
- Project configuration
- All model performances
- Evaluation metrics
- Download buttons
- Link to predictions

#### Prediction Page (/predict/[project])

**Purpose:** Make batch predictions

**Workflow:**
1. Upload CSV with same features
2. System preprocesses with saved pipeline
3. Display predictions
4. Download results

**Implementation:**
```tsx
const handlePredict = async (csvData) => {
  const response = await fetch(`${API_URL}/api/predict/${projectName}`, {
    method: 'POST',
    body: JSON.stringify({csv_data: csvData})
  })
  const results = await response.json()
  setResults(results.results)
}
```

---

## Data Flow

### Training Pipeline Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. USER UPLOAD & CONFIGURATION                               │
├─────────────────────────────────────────────────────────────┤
│ • User uploads CSV via /train page                            │
│ • Specifies ML task, target column, options                  │
│ • Frontend validates, uploads to /api/upload                 │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│ 2. DATA ANALYSIS (Backend)                                   │
├─────────────────────────────────────────────────────────────┤
│ • FileHandler reads CSV (auto-detects format)                │
│ • Parse to Pandas DataFrame                                  │
│ • IntelligentDataAnalyzer examines:                          │
│   - Data types, missing values, shape                        │
│   - Distributions, correlations                              │
│   - Outliers, duplicates                                     │
│ • LLM (Google Gemini) analyzes patterns                      │
│ • Return analysis report to frontend                         │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│ 3. PREPROCESSING (if enabled)                                │
├─────────────────────────────────────────────────────────────┤
│ IntelligentDataProcessor performs:                           │
│ • Target Encoding: Separate target from features             │
│ • Feature Engineering:                                       │
│   - Add derived features (ratios, interactions)              │
│   - Polynomial features                                      │
│   - Domain-specific features via LLM                         │
│ • Categorical Encoding:                                      │
│   - One-hot encoding (pd.get_dummies)                        │
│   - Frequency encoding for high-cardinality                  │
│ • Numeric Scaling:                                           │
│   - StandardScaler for most algorithms                       │
│   - MinMaxScaler alternative                                 │
│   - RobustScaler for outliers                                │
│ • Missing Value Imputation:                                  │
│   - Mean/median for numeric                                  │
│   - Mode for categorical                                     │
│   - KNN imputation option                                    │
│ • Outlier Handling: Winsorization                            │
│ • Feature Selection:                                         │
│   - Remove low-variance features                             │
│   - Remove highly correlated duplicates                      │
│ • Train/Test Split: sklearn.model_selection.train_test_split │
│   - Default 80/20, configurable                              │
│ • Save preprocessor pipeline (joblib)                        │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│ 4. MODEL TRAINING (Parallel ThreadPoolExecutor)              │
├─────────────────────────────────────────────────────────────┤
│ ModelRegistry trains 6-8 models simultaneously:              │
│                                                               │
│ For Classification:                                          │
│ • LogisticRegression (sklearn)                               │
│ • SVC (sklearn)                                              │
│ • RandomForestClassifier (sklearn)                           │
│ • GradientBoostingClassifier (sklearn)                       │
│ • XGBClassifier (xgboost)                                    │
│ • CatBoostClassifier (catboost)                              │
│ • MLPClassifier (sklearn neural network)                     │
│                                                               │
│ For Regression:                                              │
│ • LinearRegression, Ridge, Lasso (sklearn)                   │
│ • SVR (sklearn)                                              │
│ • RandomForestRegressor (sklearn)                            │
│ • GradientBoostingRegressor (sklearn)                        │
│ • XGBRegressor (xgboost)                                     │
│ • CatBoostRegressor (catboost)                               │
│ • MLPRegressor (sklearn)                                     │
│                                                               │
│ For Clustering:                                              │
│ • KMeans                                                     │
│ • DBSCAN                                                     │
│ • AgglomerativeClustering                                    │
│                                                               │
│ Training Strategy:                                           │
│ 1. Cross-validation (5-fold default)                         │
│ 2. Hyperparameter tuning (optional Optuna)                   │
│ 3. Train on full training set                                │
│ 4. Evaluate on test set                                      │
│ 5. Save each trained model                                   │
│                                                               │
│ Hyperparameter Tuning (Optuna):                              │
│ • 30 trials per model (configurable)                         │
│ • Tree-structured Parzen Estimator (TPE) sampler             │
│ • Maximize target metric (accuracy/R²/silhouette)            │
│ • 60s timeout per trial                                      │
│ • Save best params                                           │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│ 5. EVALUATION & METRIC CALCULATION                           │
├─────────────────────────────────────────────────────────────┤
│ For each trained model:                                      │
│                                                               │
│ Classification Metrics:                                      │
│ • Accuracy = (TP + TN) / (TP + TN + FP + FN)                 │
│ • Precision = TP / (TP + FP)                                 │
│ • Recall = TP / (TP + FN)                                    │
│ • F1 = 2 * (Precision * Recall) / (Precision + Recall)       │
│ • ROC-AUC = Area under ROC curve                             │
│ • Confusion matrix                                           │
│                                                               │
│ Regression Metrics:                                          │
│ • R² = 1 - (SS_res / SS_tot)                                 │
│ • MAE = (1/n) * Σ|y_true - y_pred|                           │
│ • MSE = (1/n) * Σ(y_true - y_pred)²                          │
│ • RMSE = √MSE                                                │
│ • Explained Variance                                         │
│                                                               │
│ Clustering Metrics:                                          │
│ • Silhouette Score [-1, 1]                                   │
│ • Calinski-Harabasz Index (higher is better)                 │
│ • Davies-Bouldin Index (lower is better)                     │
│                                                               │
│ Select best model (highest F1/R²/Silhouette)                 │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│ 6. RESULTS SAVING & STORAGE                                  │
├─────────────────────────────────────────────────────────────┤
│ Save to: projects/{project_name}_{timestamp}/                │
│                                                               │
│ Files created:                                               │
│ • metadata.json         - Project config & results           │
│ • best_model.pkl        - Best trained model (joblib)        │
│ • data_prep.pkl         - Preprocessor pipeline              │
│ • ipc.pkl               - Input configuration                │
│ • evaluation_scores.json - All metrics                       │
│ • preprocessing_config.json - LLM recommendations            │
│ • report.json           - Full analysis                      │
│ • X_train.csv, y_train.csv - Training data                   │
│ • X_test.csv, y_test.csv   - Test data                       │
│ • models/{algorithm}.pkl    - All trained models             │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│ 7. FRONTEND RESULT DISPLAY                                   │
├─────────────────────────────────────────────────────────────┤
│ • Progress complete (100%)                                   │
│ • Best model name displayed                                  │
│ • All model metrics shown                                    │
│ • Download button active                                     │
│ • Navigation to predictions available                        │
└─────────────────────────────────────────────────────────────┘
```

### Prediction Flow

```
User Data (CSV)
       │
       ├─> Load saved preprocessor pipeline
       │
       ├─> Apply same transformations:
       │   • Categorical encoding
       │   • Numeric scaling
       │   • Feature engineering
       │
       ├─> Load best trained model
       │
       ├─> Make predictions: model.predict(X_new)
       │
       └─> Return: Original data + predictions + probabilities
```

---

## ML Pipeline

### intelligent_data_analyzer.py

**Class:** `IntelligentDataAnalyzer`

**Methods:**

```python
def analyze(df, target_column=None):
    """
    Comprehensive data analysis
    
    Returns:
    {
      'shape': (rows, cols),
      'dtypes': {col: dtype},
      'missing': {col: percent},
      'duplicates': count,
      'categorical': [cols],
      'numeric': [cols],
      'correlations': matrix,
      'distributions': {...},
      'target_info': {...},
      'insights': [str],
      'recommendations': [str]
    }
    """

def get_llm_analysis(df_analysis, llm_model):
    """
    Send analysis to LLM for insights
    
    Returns:
    {
      'data_quality': str,
      'preprocessing_strategy': str,
      'feature_recommendations': [str],
      'potential_issues': [str]
    }
    """
```

### intelligent_data_processor.py

**Class:** `IntelligentDataProcessor`

**Methods:**

```python
def process(df, target_col, ml_type):
    """Main preprocessing orchestrator"""
    
    # 1. Target processing
    X, y = self.target_processor.separate_target(df, target_col)
    
    # 2. Feature engineering
    X = self.feature_engine.engineer_features(X)
    
    # 3. Categorical encoding
    X = self.categorical_encoder(X)
    
    # 4. Imputation
    X = self.imputer.fit_transform(X)
    
    # 5. Scaling
    X = self.scaler.fit_transform(X)
    
    # 6. Feature selection
    X = self.feature_selector.fit_transform(X, y)
    
    return X, y, metadata

def fit_preprocessor(X, y):
    """Fit all preprocessor components for reuse"""

def transform_new_data(X_new):
    """Apply fitted preprocessing to new data"""
```

### automl_pipeline.py

**Function:** `run_automl(df, config)`

**Execution:**

```python
def run_automl(df, config):
    """
    Orchestrate full AutoML pipeline
    
    1. Analyze data
    2. Preprocess (if enabled)
    3. Train models
    4. Evaluate
    5. Save artifacts
    
    Returns: {
      'best_model': Model,
      'best_model_name': str,
      'trained_models': {name: model},
      'evaluation_scores': {name: metrics},
      'preprocessing_config': dict
    }
    """
    
    # Data analysis
    analyzer = IntelligentDataAnalyzer()
    analysis = analyzer.analyze(df, config.target_column)
    
    # Preprocessing
    if config.processing_type == PREPROCESS_TRAIN:
        processor = IntelligentDataProcessor()
        X, y, prep_config = processor.process(df, config.target_column)
    else:
        X, y = separate_target(df, config.target_column)
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=config.test_size, random_state=42
    )
    
    # Training
    registry = ModelRegistry(config)
    results = registry.train_models(X_train, y_train, X_test, y_test)
    
    return results
```

### model_registry.py

**Class:** `ModelRegistry`

**Methods:**

```python
def train_models(X_train, y_train, X_test, y_test):
    """
    Train all models in parallel
    
    Uses ThreadPoolExecutor for concurrent training
    Updates progress via callback
    
    Returns:
    {
      'trained_models': {algorithm: model},
      'evaluation_scores': {algorithm: metrics},
      'best_model_name': str,
      'best_model': Model,
      'training_times': {algorithm: seconds}
    }
    """
    
    # Get models for task type
    models = self.get_models()  # Returns dict of {name: hyperparams}
    
    # Submit training tasks
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {}
        for model_name, model in models.items():
            future = executor.submit(
                self.train_and_evaluate,
                model_name,
                model,
                X_train, y_train,
                X_test, y_test
            )
            futures[model_name] = future
        
        # Collect results
        results = {}
        for model_name, future in futures.items():
            results[model_name] = future.result()
    
    return results

def train_and_evaluate(model_name, model, X_train, y_train, X_test, y_test):
    """Train single model with cross-validation"""
    
    # Hyperparameter tuning (optional)
    if self.config.hyper_parameter_tuning:
        study = optuna.create_study(direction='maximize')
        study.optimize(
            lambda trial: self.objective(trial, model, X_train, y_train),
            n_trials=30
        )
        best_params = study.best_params
        model.set_params(**best_params)
    
    # Cross-validation
    cv_scores = cross_val_score(model, X_train, y_train, cv=5)
    
    # Train on full set
    model.fit(X_train, y_train)
    
    # Evaluate
    metrics = self.calculate_metrics(model, X_test, y_test)
    
    return {
        'model': model,
        'metrics': metrics,
        'cv_mean': cv_scores.mean(),
        'cv_std': cv_scores.std()
    }

def calculate_metrics(model, X_test, y_test):
    """Calculate appropriate metrics based on task type"""
    
    predictions = model.predict(X_test)
    
    if self.config.learning_type == 'classification':
        return {
            'accuracy': accuracy_score(y_test, predictions),
            'precision': precision_score(y_test, predictions, average='weighted'),
            'recall': recall_score(y_test, predictions, average='weighted'),
            'f1': f1_score(y_test, predictions, average='weighted'),
            'roc_auc': roc_auc_score(y_test, predictions) if binary else None
        }
    
    elif self.config.learning_type == 'regression':
        return {
            'r2': r2_score(y_test, predictions),
            'mae': mean_absolute_error(y_test, predictions),
            'mse': mean_squared_error(y_test, predictions),
            'rmse': sqrt(mean_squared_error(y_test, predictions))
        }
    
    elif self.config.learning_type == 'clustering':
        return {
            'silhouette': silhouette_score(X_test, predictions),
            'calinski': calinski_harabasz_score(X_test, predictions),
            'davies': davies_bouldin_score(X_test, predictions)
        }
```

---

## Project Structure

### Directory Layout

```
projects/
└── churn_prediction_20250207_143022/
    ├── metadata.json                 # Project metadata & results
    ├── best_model.pkl                # Best trained model
    ├── data_prep.pkl                 # Preprocessor pipeline
    ├── ipc.pkl                       # InputConfiguration
    ├── evaluation_scores.json         # All metrics
    ├── preprocessing_config.json      # Feature engineering details
    ├── report.json                   # Full analysis report
    ├── X_train.csv                   # Training features
    ├── y_train.csv                   # Training target
    ├── X_test.csv                    # Test features
    ├── y_test.csv                    # Test target
    ├── train_data.csv                # Full training dataset
    ├── test_data.csv                 # Full test dataset
    └── models/
        ├── logistic.pkl
        ├── svm.pkl
        ├── random_forest.pkl
        ├── gradient_boost.pkl
        ├── xgb.pkl
        ├── catboost.pkl
        └── mlp.pkl
```

### metadata.json Structure

```json
{
  "project_name": "churn_prediction",
  "created_at": "2025-02-07T14:30:22Z",
  "status": "completed",
  "duration_seconds": 1240,
  "config": {
    "ml_type": "supervised",
    "learning_type": "classification",
    "processing_type": "preprocess_train",
    "target_column": "is_churned",
    "index_column": "customer_id",
    "test_size": 0.2,
    "hyper_parameter_tuning": true,
    "acceleration_hardware": "auto"
  },
  "data_analysis": {
    "rows": 15000,
    "columns": 23,
    "missing_percent": 2.1,
    "categorical_features": 8,
    "numeric_features": 15
  },
  "preprocessing": {
    "features_engineered": 5,
    "features_dropped": 2,
    "imputation_method": "mean",
    "scaling_method": "standard",
    "encoding_method": "one_hot"
  },
  "training": {
    "best_model": "xgb",
    "models_trained": 7,
    "total_training_time": 1200,
    "avg_cv_score": 0.891
  },
  "evaluation_scores": {
    "xgb": {
      "accuracy": 0.891,
      "precision": 0.876,
      "recall": 0.823,
      "f1": 0.848,
      "roc_auc": 0.923,
      "cv_mean": 0.885,
      "cv_std": 0.012
    }
  }
}
```

---

## Configuration

### Environment Variables (.env)

```bash
# Required: Google Gemini AI
LLM_MODEL_NAME=gemini-2.0-flash
LLM_API_KEY=your_api_key_here

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional: GPU Configuration
CUDA_VISIBLE_DEVICES=0

# Optional: Backend Settings
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
WORKERS=4
```

### hyper_parameter_config.json

Structure for customizing hyperparameter search:

```json
{
  "logistic_regression": {
    "C": [0.001, 1.0, 100.0],
    "max_iter": 1000
  },
  "random_forest": {
    "n_estimators": [50, 100, 200],
    "max_depth": [5, 10, 15],
    "min_samples_split": [2, 5],
    "min_samples_leaf": [1, 2]
  },
  "xgb": {
    "n_estimators": [100, 200, 300],
    "max_depth": [3, 5, 7],
    "learning_rate": [0.01, 0.05, 0.1],
    "subsample": [0.7, 0.9],
    "colsample_bytree": [0.7, 0.9]
  },
  "catboost": {
    "iterations": [100, 200, 300],
    "depth": [4, 6, 8],
    "learning_rate": [0.01, 0.05, 0.1],
    "l2_leaf_reg": [1, 3, 5]
  }
}
```

### Core Data Models (core/models.py)

```python
from enum import Enum
from pydantic import BaseModel
from typing import Optional

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
    AUTO = "auto"

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
    acceleration_hardware: Hardware = Hardware.AUTO
    test_size: Optional[float] = 0.2
    hyper_parameter_tuning: bool = False
```

---

## Deployment

### Docker Deployment

**Backend Dockerfile:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
```

**Frontend Dockerfile:**
```dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json .
RUN npm install

COPY . .
ENV NEXT_PUBLIC_API_URL=http://backend:8000

RUN npm run build

CMD ["npm", "start"]
```

**Docker Compose:**
```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - LLM_API_KEY=${LLM_API_KEY}
      - LLM_MODEL_NAME=gemini-2.0-flash
    volumes:
      - ./projects:/app/projects

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
```

### Production Deployment Checklist

1. **Environment Setup**
   - Set LLM_API_KEY in platform secrets
   - Configure NEXT_PUBLIC_API_URL to production backend
   - Set CUDA_VISIBLE_DEVICES if using GPU

2. **Backend (Python)**
   - Deploy to Railway, Render, or similar
   - Set up persistent volume for projects/
   - Configure CORS for production domain
   - Monitor memory usage

3. **Frontend (Next.js)**
   - Deploy to Vercel or similar
   - Configure custom domain
   - Set environment variables
   - Enable HTTPS

4. **Monitoring**
   - Set up logging aggregation
   - Monitor WebSocket connections
   - Track API response times
   - Alert on errors

---

## Performance

### Benchmarks

| Scenario | Data Size | GPU | Time | Models |
|----------|-----------|-----|------|--------|
| Quick Demo | 1K rows | No | 30s | 3 |
| Small Dataset | 10K rows | No | 2-3 min | 7 |
| Medium Dataset | 100K rows | Yes | 5-10 min | 7 |
| Large Dataset | 1M rows | Yes | 20-30 min | 7 |
| With Hyperparameter Tuning | 10K rows | Yes | 15-20 min | 7 |

### Memory Usage

- **Base Backend:** 200-300 MB
- **Per Model During Training:** 100-500 MB
- **Project Storage:** 10-100 MB (model artifacts)
- **Typical Deployment:** 2-4 GB recommended

### Optimization Tips

1. **Training Speed**
   - Enable GPU (3-5x faster)
   - Use Training-Only mode (skip preprocessing)
   - Reduce hyperparameter tuning trials
   - Increase thread pool workers

2. **Memory Efficiency**
   - Reduce dataset sample size (e.g., stratified sample)
   - Disable preprocessing if not needed
   - Use sparse matrices for high-dimensional data
   - Clean up old projects regularly

3. **API Response Time**
   - Cache analysis results
   - Use async/await patterns
   - Implement request rate limiting
   - Use CDN for static files

---

## Security

### Authentication & Authorization

Currently: No authentication required (can be added)

**Recommended for production:**
- Add JWT authentication to /api endpoints
- Implement role-based access control
- Use API keys for programmatic access

### Data Protection

1. **File Upload Validation**
   - File type whitelist (CSV, JSON, XML, Excel, Parquet)
   - File size limit (100 MB)
   - Virus scan integration optional

2. **Stored Models**
   - Pickled models in projects/ directory
   - Consider encryption for sensitive models
   - Access control on project directories

3. **LLM API Key**
   - Store in .env file (not in code)
   - Environment variable injection
   - Consider secrets manager (Vault, AWS Secrets Manager)

### Input Validation

1. **CSV Validation**
   - File size check
   - Column name validation
   - Data type inference
   - Missing value handling

2. **Request Validation**
   - Pydantic model validation
   - SQL injection prevention (pandas operations)
   - XSS prevention (React/Next.js built-in)

### CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### WebSocket Security

- Same-origin policy enforcement
- Connection authentication (optional)
- Message validation before processing
- Timeout on idle connections (60s)

---

## API Error Responses

### Standard Error Format

```json
{
  "detail": "Description of error",
  "status_code": 400,
  "error_type": "validation_error"
}
```

### Common HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Training started |
| 400 | Bad Request | Invalid parameters |
| 404 | Not Found | Project not found |
| 500 | Server Error | GPU out of memory |
| 503 | Service Unavailable | LLM API down |

### Example Error Responses

**Missing Target Column (400):**
```json
{
  "detail": "Target column 'churn' not found in data",
  "status_code": 400,
  "error_type": "validation_error"
}
```

**Project Not Found (404):**
```json
{
  "detail": "Project 'invalid_project' not found",
  "status_code": 404,
  "error_type": "not_found"
}
```

**GPU Out of Memory (500):**
```json
{
  "detail": "CUDA out of memory. Falling back to CPU.",
  "status_code": 500,
  "error_type": "resource_exhaustion"
}
```

---

## Logging

### Backend Logging

**Configuration:**
```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
```

**Log Levels:**
- `DEBUG` - Detailed variable states
- `INFO` - Training progress, milestones
- `WARNING` - Potential issues (missing values >10%)
- `ERROR` - Failed operations
- `CRITICAL` - System failures

### Frontend Logging

Debug statements format:
```javascript
console.log("[v0] Description", variable)
```

---

## Version Information

| Component | Version | Pinned |
|-----------|---------|--------|
| FastAPI | 0.104.1 | Yes |
| Python | 3.10+ | Yes |
| Next.js | 16 | Yes |
| React | 19+ | Yes |
| Scikit-learn | 1.3.2 | Yes |
| XGBoost | 2.0.3 | Yes |
| CatBoost | 1.2.2 | Yes |
| Pandas | 2.1.3 | Yes |

---

## References & Standards

- **ML Standards:** Scikit-learn conventions
- **API Design:** OpenAPI/Swagger spec
- **Data Format:** JSON for metadata, Pickle for models, CSV for data
- **Code Style:** Black formatter, isort for imports
- **Frontend:** Tailwind CSS utilities, shadcn/ui components

---

**Last Updated:** 2025-02-07  
**Documentation Version:** 1.0
