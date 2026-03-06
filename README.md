# AutoML Platform - Professional Machine Learning from CSV

A complete, production-ready AutoML system that intelligently handles data analysis, preprocessing, model training, and evaluation. **Zero manual feature engineering required.**

## What This System Does

This platform automates the entire ML workflow:

1. **Intelligent Data Analysis** (LLM-Powered)
   - Google Gemini AI analyzes your data
   - Detects patterns, data quality issues, correlations
   - Recommends preprocessing strategies
   - Identifies useful features vs noise

2. **Advanced Data Preprocessing**
   - Automatic missing value imputation (mean/median)
   - One-hot encoding for categorical variables
   - Feature engineering (adding new derived features)
   - Outlier handling (Winsorization)
   - Feature scaling and normalization
   - Duplicate and constant feature removal
   - Correlation-based feature selection

3. **Parallel Multi-Model Training**
   - Classification: Logistic, SVM, Random Forest, Gradient Boosting, XGBoost, CatBoost, Neural Networks
   - Regression: Linear, Ridge, Lasso, SVR, Random Forest, Gradient Boosting, XGBoost, CatBoost, Neural Networks
   - Clustering: K-Means, DBSCAN, Hierarchical Clustering
   - All models train simultaneously on ThreadPoolExecutor
   - Optional Bayesian hyperparameter tuning (Optuna)

4. **Automatic Evaluation**
   - Classification: Accuracy, Precision, Recall, F1, ROC-AUC, Confusion Matrix
   - Regression: R², MAE, MSE, RMSE, Explained Variance
   - Clustering: Silhouette Score, Calinski-Harabasz, Davies-Bouldin
   - Best model selected automatically

5. **Real-Time Monitoring**
   - WebSocket updates during training
   - Progress tracking per model
   - ETA calculation
   - Live loss/metric updates

6. **Project Management**
   - Save all models, preprocessors, configs
   - Persistent project history
   - Re-prediction on new data
   - Full artifact retrieval

## Key Features

✨ **Intelligent Analysis** - Google Gemini AI understands your data
🏃 **Fast Preprocessing** - Automatic feature engineering in minutes  
🚀 **Parallel Training** - Multiple models train simultaneously
⚡ **GPU Acceleration** - Automatic detection with CPU fallback
📊 **Rich Metrics** - Comprehensive evaluation for every task
💾 **Full Reproducibility** - Save everything, replay anytime
🔮 **Batch Predictions** - Apply models to new data instantly
📈 **Real-Time Updates** - WebSocket progress tracking
🏆 **Auto Model Selection** - Best model chosen automatically
⚙️ **Tunable Algorithms** - Adjust hyperparameter search spaces

## Tech Stack

| Component | Tech | Version |
|-----------|------|---------|
| **Backend API** | FastAPI | 0.104+ |
| **Real-time Updates** | WebSocket | Native |
| **ML Pipeline** | Scikit-learn | 1.3+ |
| **Gradient Boosting** | XGBoost, CatBoost | 2.0+, 1.2+ |
| **Hyperparameter Tuning** | Optuna | 3.14+ |
| **Data Processing** | Pandas, NumPy | 2.1+, 1.26+ |
| **Feature Engineering** | Feature-Engine | 1.6+ |
| **LLM Analysis** | Google Gemini 2.0 Flash | Latest |
| **Frontend Framework** | Next.js | 16 |
| **Frontend Styling** | Tailwind CSS | Latest |
| **UI Components** | Shadcn/ui | Latest |
| **Python** | Python | 3.10+ |
| **Node.js** | Node | 18+ |

## Installation & Quick Start

### Prerequisites
- **Python 3.10+** 
- **Node.js 18+**
- **Google API Key** (free from https://ai.google.dev)
- Optional: NVIDIA GPU for acceleration

### Fastest Way: Automated Setup

**Linux/macOS:**
```bash
chmod +x start.sh
./start.sh
```

**Windows:**
```bash
start.bat
```

This automatically:
- Checks all dependencies
- Creates .env file
- Installs Python & Node packages
- Starts backend on http://localhost:8000
- Starts frontend on http://localhost:3000

### Manual Setup

**1. Backend Setup**
```bash
cd backend
pip install -r requirements.txt

# Create .env with your Google API key
cp ../.env.example ../.env
# Edit .env and add: LLM_API_KEY=your_key_from_ai.google.dev

python main.py
```
Backend runs on `http://localhost:8000`

**2. Frontend Setup (new terminal)**
```bash
npm install
npm run dev
```
Frontend runs on `http://localhost:3000`

**3. Visit Application**
Open http://localhost:3000 in browser

## Usage Example

### Step 1: Upload Data
- Click "Create New Project"
- Upload CSV (auto-detects: CSV, JSON, XML, Excel, Parquet)
- System analyzes: 15,000 rows × 23 columns, 2% missing values

### Step 2: Configure
```
ML Type:        Supervised
Learning Type:  Classification (predicting customer churn)
Target Column:  is_churned
Preprocessing:  Full (advanced feature engineering)
Test Size:      20%
Tuning:         Enable (30 trials per model)
```

### Step 3: Train
- Data Analysis: Gemini AI analyzes relationships
- Preprocessing: Encodes categoricals, imputes missing, engineers features
- Training: 8 models train in parallel (2 min on GPU)
- Evaluation: All metrics calculated automatically
- Selection: XGBoost wins with F1=0.91

### Step 4: Results
- Download `evaluation_scores.json`
- View all model performances
- See preprocessing applied
- Access trained model artifacts

### Step 5: Predict
- Go to project → "Make Predictions"
- Upload new CSV with same columns
- System automatically preprocesses with saved pipeline
- Download predictions

## Complete File Structure

```
automl-platform/
│
├── app/                           # Next.js 16 Frontend
│   ├── page.tsx                  # Home dashboard
│   ├── setup/page.tsx            # LLM configuration
│   ├── train/page.tsx            # 3-step training wizard
│   ├── training/[project]/page.tsx  # Live training dashboard
│   ├── projects/page.tsx         # Project history
│   ├── project-details/[project]/ # Results & details
│   ├── predict/[project]/        # Batch predictions
│   ├── layout.tsx
│   └── globals.css
│
├── backend/                       # FastAPI Backend
│   ├── main.py                   # API server + WebSocket
│   │
│   ├── intelligent_data_analyzer.py  # LLM-powered analysis
│   │   ├── IntelligentDataAnalyzer class
│   │   ├── Dataset analysis
│   │   ├── Data type detection
│   │   └── LLM preprocessing recommendations
│   │
│   ├── intelligent_data_processor.py # Data preparation agent
│   │   ├── TargetProcessor
│   │   ├── FeatureEngineeringEngine
│   │   ├── Feature engineering (add/divide/multiply)
│   │   ├── Imputation (mean/median/categorical)
│   │   ├── Encoding (one-hot, count frequency)
│   │   ├── Scaling (standard, minmax, robust)
│   │   └── Outlier handling (Winsorization)
│   │
│   ├── automl_pipeline.py        # Main training orchestration
│   │   ├── preprocess_train() - Full preprocessing + training
│   │   └── train() - Training only mode
│   │
│   ├── model_registry.py         # Model training & evaluation
│   │   ├── ProgressTracker
│   │   ├── Hyperparameter tuning with Optuna
│   │   ├── Parallel model training (ThreadPoolExecutor)
│   │   ├── Cross-validation
│   │   ├── Metric calculation
│   │   └── Best model selection
│   │
│   ├── cognitive_engine.py       # LLM interface (Google Gemini)
│   ├── file_handler.py           # File I/O (CSV, JSON, XML, Excel)
│   ├── data_pre_processor.py     # Column name canonicalization
│   ├── services.py               # Service layer (project management)
│   │
│   ├── core/
│   │   └── models.py             # Data models, enums, configs
│   │
│   ├── prompts.py                # LLM prompt templates
│   ├── hyper_parameter_config.json  # Tuning search spaces
│   ├── requirements.txt
│   └── .env                      # API keys (Git ignored)
│
├── projects/                      # Stored projects (auto-created)
│   └── churn_prediction_20250207_143022/
│       ├── metadata.json         # Config, results, timestamps
│       ├── best_model.pkl        # Trained model (joblib)
│       ├── data_prep.pkl         # Preprocessor pipeline
│       ├── ipc.pkl               # Input configuration
│       ├── evaluation_scores.json # All metrics
│       ├── preprocessing_config.json # LLM recommendations
│       ├── report.json           # Data analysis report
│       ├── X_train.csv, y_train.csv
│       ├── X_test.csv, y_test.csv
│       ├── train_data.csv, test_data.csv
│       └── models/               # All trained models
│           ├── xgb_model.pkl
│           ├── catboost_model.pkl
│           ├── rf_model.pkl
│           └── ...
│
├── components/ui/                # Shadcn/ui components
├── lib/
│   └── utils.ts                 # Utility functions
│
├── .env.example                  # Template with instructions
├── .env                          # Actual config (Git ignored)
├── .gitignore
│
├── start.sh                      # Linux/Mac startup script
├── start.bat                     # Windows startup script
│
├── docker-compose.yml            # Docker orchestration
├── Dockerfile.backend
├── Dockerfile.frontend
│
├── package.json
├── tsconfig.json
├── next.config.mjs
├── tailwind.config.ts
│
├── README.md                     # This file
├── SETUP_GUIDE.md               # Detailed setup instructions
├── INTEGRATION_GUIDE.md         # Backend integration details
└── STARTUP.md                   # Startup checklist
```

## API Reference

### Training Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/api/upload` | Upload CSV file |
| `POST` | `/api/analyze` | Analyze uploaded data |
| `POST` | `/api/train` | Start training pipeline |
| `WS` | `/ws/{project}` | WebSocket for real-time updates |

### Project Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/api/projects` | List all projects |
| `GET` | `/api/project/{name}` | Get project details |
| `GET` | `/api/project/{name}/report` | Full analysis report |
| `GET` | `/api/project/{name}/files` | List all project files |
| `DELETE` | `/api/project/{name}` | Delete project |

### Prediction Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/api/predict/{name}` | Batch predictions on new data |
| `GET` | `/api/project/{name}/download` | Download evaluation scores |

### Config Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/api/health` | Backend status + GPU info |
| `GET` | `/api/env-status` | LLM configuration check |
| `POST` | `/api/setup-llm` | Configure LLM credentials |

Full interactive API docs: http://localhost:8000/docs

## WebSocket Message Format

**Status Update (from server)**
```json
{
  "type": "status",
  "message": "Training XGBoost model...",
  "progress": 65
}
```

**Completion (from server)**
```json
{
  "type": "complete",
  "message": "✓ Training complete! Best model: XGBoost",
  "progress": 100,
  "result": {
    "best_model": "xgb",
    "models_trained": ["logistic", "svm", "rf", "gb", "xgb", "catboost"],
    "evaluation_scores": {
      "xgb": {"f1": 0.91, "accuracy": 0.89},
      "catboost": {"f1": 0.89, "accuracy": 0.87}
    }
  }
}
```

**Error (from server)**
```json
{
  "type": "error",
  "message": "Training failed",
  "error": "CUDA out of memory. Falling back to CPU.",
  "details": "..."
}
```

## Environment Variables

Create `.env` file:
```bash
# Required: Google Gemini AI (free from https://ai.google.dev)
LLM_MODEL_NAME=gemini-2.0-flash
LLM_API_KEY=your_google_api_key_here

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional: GPU Configuration
CUDA_VISIBLE_DEVICES=0  # GPU to use (0 for first GPU)
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Connection refused" on frontend | Backend not running: `cd backend && python main.py` |
| "LLM API key invalid" | Get key from https://ai.google.dev, update .env |
| "CUDA out of memory" | System auto-fallbacks to CPU, or reduce data size |
| "Training extremely slow" | Enable GPU with `nvidia-smi` check, or use Training-Only mode |
| WebSocket connection failing | Check NEXT_PUBLIC_API_URL in .env matches backend URL |
| Port 8000/3000 already in use | Kill process: `lsof -i :8000` then `kill -9 <PID>` |

See [SETUP_GUIDE.md](./SETUP_GUIDE.md) for comprehensive troubleshooting.

## Production Deployment

### Docker
```bash
docker-compose up
```

### Frontend to Vercel
```bash
npm run build
vercel deploy
```

### Backend to Cloud Host
Deploy to Railway, Render, Heroku, or your preferred Python host. Set environment variables on the platform.

## Performance

- **Small datasets (<10K rows)**: ~2-5 minutes
- **Medium datasets (10K-100K rows)**: 5-20 minutes with preprocessing
- **Large datasets (>100K rows)**: Use Training-Only mode, enable GPU
- **GPU acceleration**: 3-5x faster than CPU

## Advanced Configuration

### Hyperparameter Tuning
Edit `backend/hyper_parameter_config.json` to customize Optuna search spaces:
```json
{
  "xgb": {
    "n_estimators": [100, 300],
    "max_depth": [3, 8],
    "learning_rate": [0.01, 0.1]
  }
}
```

### Model Selection
Modify `model_registry.py` to add/remove algorithms or change cross-validation folds.

## Next Steps

1. Read [SETUP_GUIDE.md](./SETUP_GUIDE.md) for detailed instructions
2. Check [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) to customize ML pipeline
3. Review [STARTUP.md](./STARTUP.md) for quick reference
4. Try with your own datasets
5. Deploy to production when satisfied

---

**Built with ❤️ using FastAPI + Next.js + Scikit-learn + Google Gemini AI**

Start now: `./start.sh` (Linux/Mac) or `start.bat` (Windows)
