# AutoML Platform - Complete Setup Guide

## Overview
This is a professional AutoML system that combines:
- **Data Analysis**: LLM-powered intelligent data analysis
- **Preprocessing**: Automated feature engineering and data preparation
- **Model Training**: Multiple ML algorithms with hyperparameter tuning
- **Real-time Updates**: WebSocket-based progress tracking
- **Model Management**: Project history and re-prediction capabilities

## Tech Stack
- **Frontend**: Next.js 16 + React 19 + TypeScript
- **Backend**: FastAPI + WebSocket + Python ML Stack
- **ML Libraries**: XGBoost, CatBoost, Scikit-learn, Feature-Engine
- **LLM**: Google Gemini AI for intelligent analysis

## Prerequisites
1. Python 3.10+ with pip
2. Node.js 18+ with npm
3. Google API Key (for Gemini AI)
4. Optional: NVIDIA GPU for faster training

## Step 1: Setup Backend

### 1.1 Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 1.2 Configure Environment Variables
Create a `.env` file in the project root:
```bash
cp .env.example .env
```

Edit `.env` and add:
```
LLM_MODEL_NAME=gemini-2.0-flash
LLM_API_KEY=your_google_api_key_here
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Get Google API Key:**
1. Go to https://ai.google.dev
2. Click "Get API Key"
3. Create a new project or select existing
4. Generate and copy your API key
5. Paste into `.env`

### 1.3 Start Backend Server
```bash
cd backend
python main.py
```

The backend will start on `http://localhost:8000`

Verify:
- Visit http://localhost:8000/docs (Swagger UI)
- You should see all API endpoints

## Step 2: Setup Frontend

### 2.1 Install Node Dependencies
```bash
npm install
```

### 2.2 Start Frontend Development Server
```bash
npm run dev
```

The frontend will start on `http://localhost:3000`

## Step 3: First Run

### 3.1 Access the Application
Visit http://localhost:3000 in your browser

### 3.2 Configure LLM (if not done via .env)
1. Click "Configure LLM" on the home page
2. Enter:
   - **Model Name**: `gemini-2.0-flash`
   - **API Key**: Your Google API key
3. Click "Save Configuration"

### 3.3 Create Your First Project
1. Click "Create New Project"
2. **Upload CSV**: Select your dataset
3. **Analyze**: System automatically detects:
   - Data types
   - Missing values
   - Statistical summaries
4. **Configure**:
   - Select ML Type (Supervised/Unsupervised)
   - Choose Learning Type (Classification/Regression/Clustering)
   - Set target column (for supervised learning)
   - Choose preprocessing mode (Full or Training-Only)
5. **Review**: Confirm settings and start training
6. **Monitor**: Watch real-time progress via WebSocket
7. **Download**: Get evaluation scores as JSON

## How the ML Pipeline Works

### Full Preprocessing + Training Flow
1. **Data Loading**: Reads CSV, detects encoding, handles missing values
2. **Data Analysis**: LLM analyzes data to understand structure
3. **Data Preparation**: 
   - Missing value imputation
   - Categorical encoding
   - Feature engineering (combining features)
   - Outlier handling
   - Feature scaling
4. **Model Training**: Trains multiple models:
   - Classification: Logistic Regression, SVM, Random Forest, Gradient Boosting, XGBoost, CatBoost
   - Regression: Linear Regression, Ridge, Lasso, SVR, Random Forest, Gradient Boosting, XGBoost, CatBoost
   - Clustering: K-Means, DBSCAN, Hierarchical Clustering
5. **Hyperparameter Tuning**: Uses Optuna for automatic tuning (if enabled)
6. **Evaluation**: Computes metrics:
   - Classification: Accuracy, Precision, Recall, F1, ROC-AUC
   - Regression: R², MAE, MSE, RMSE
   - Clustering: Silhouette Score, Calinski-Harabasz, Davies-Bouldin
7. **Model Selection**: Picks best model based on primary metric
8. **Artifact Saving**: Saves model, preprocessor, config, scores

### Training-Only Flow
Faster alternative that skips advanced preprocessing:
1. Basic missing value handling
2. Categorical encoding
3. Direct model training
4. Evaluation on test set

## Project Management Features

### View All Projects
- Click "Projects" in navigation
- See training history with timestamps
- View model performance metrics

### Project Details
- Configuration used
- Preprocessing steps applied
- Evaluation scores for all models
- Best model details
- All output files

### Make New Predictions
1. Go to project details
2. Click "Make Predictions"
3. Upload new CSV with same features
4. System automatically:
   - Applies same preprocessing
   - Loads trained model
   - Generates predictions
   - Downloads results

### Delete Projects
- Remove old projects to save space
- Reclaim disk storage

## Advanced Features

### Hyperparameter Tuning
- Enable during project creation
- Uses Optuna with Bayesian optimization
- 30 trials per model (configurable)
- Finds optimal parameters automatically

### GPU Acceleration
- Automatically detects NVIDIA GPU
- Falls back to CPU if unavailable
- Supports CatBoost GPU training
- Set `CUDA_VISIBLE_DEVICES` in .env to select GPU

### LLM-Powered Analysis
- Google Gemini AI analyzes your data
- Intelligent feature selection
- Preprocessing recommendations
- Data quality assessment
- Automatic preprocessing configuration

## Troubleshooting

### Backend Won't Start
```bash
# Check Python version
python --version  # Should be 3.10+

# Try with python3
python3 main.py

# Check if port 8000 is in use
lsof -i :8000
```

### "Connection refused" Error
- Backend not running: Run `python main.py` in backend folder
- Frontend looking at wrong URL: Check NEXT_PUBLIC_API_URL in .env

### LLM Configuration Errors
- API key invalid: Verify on https://ai.google.dev
- Model name wrong: Use exactly `gemini-2.0-flash`
- Rate limit hit: Wait a moment and retry

### Training Takes Too Long
- Large dataset: Consider sampling
- Many models: Disable hyperparameter tuning
- GPU issues: Check GPU availability with `nvidia-smi`

### Out of Memory
- Reduce data size
- Lower batch size in model config
- Close other applications
- Use CPU mode (no GPU)

## File Structure
```
project/
├── app/                    # Next.js frontend
│   ├── page.tsx           # Home page
│   ├── train/             # Training page
│   ├── training/          # Training dashboard
│   ├── projects/          # Projects list
│   └── predict/           # Prediction page
├── backend/               # FastAPI backend
│   ├── main.py           # Main API server
│   ├── intelligent_data_analyzer.py
│   ├── intelligent_data_processor.py
│   ├── automl_pipeline.py
│   ├── model_registry.py
│   ├── cognitive_engine.py
│   ├── file_handler.py
│   ├── services.py
│   └── requirements.txt
├── projects/             # Stored projects & models
└── .env                  # Environment variables
```

## API Endpoints

### Core Training
- `POST /api/upload` - Upload CSV file
- `POST /api/analyze` - Analyze uploaded data
- `POST /api/train` - Start training
- `WebSocket /ws/{project_name}` - Real-time updates

### Project Management
- `GET /api/projects` - List all projects
- `GET /api/project/{project_name}` - Get project details
- `GET /api/project/{project_name}/report` - Get full report
- `DELETE /api/project/{project_name}` - Delete project

### Predictions & Results
- `POST /api/predict/{project_name}` - Make predictions
- `GET /api/project/{project_name}/download` - Download scores
- `GET /api/project/{project_name}/files` - List project files

### Configuration
- `GET /api/health` - Check backend health
- `GET /api/env-status` - Check LLM configuration
- `POST /api/setup-llm` - Configure LLM

## Production Deployment

### Using Docker
```bash
docker-compose up
```

This runs both frontend and backend in containers.

### Deploy to Vercel (Frontend)
```bash
npm run build
vercel deploy
```

### Deploy Backend
- Use dedicated Python hosting (Heroku, Railway, Render, etc.)
- Update NEXT_PUBLIC_API_URL to production backend URL
- Ensure environment variables are set

## Support & Issues

- Check logs in backend console for errors
- Browser DevTools for frontend issues
- Verify .env configuration
- Ensure backend is running before using frontend
- Check CORS settings if cross-origin errors occur

## Next Steps

1. **Experiment** with your datasets
2. **Compare** different ML approaches
3. **Tune** hyperparameters for better accuracy
4. **Deploy** your best models
5. **Monitor** performance over time

Happy machine learning!
