# AutoML Integration Guide

This guide explains how to integrate your existing AutoML Python code with the FastAPI backend and Next.js frontend.

## Overview

Your existing code modules:
- `intelligent_data_analyzer.py` - Data analysis and LLM preprocessing
- `intelligent_data_processor.py` - Data preprocessing
- `automl_pipeline.py` - Training pipeline
- `model_registry.py` - Model management
- `cognitive_engine.py` - LLM communication
- Plus supporting modules...

These need to be integrated into the FastAPI backend at `backend/main.py`.

## Integration Steps

### Step 1: Copy Your Python Modules

```bash
# Copy your code to backend directory
cp -r /path/to/your/code/* backend/
```

Your backend structure should look like:
```
backend/
├── main.py (FastAPI app)
├── core/
│   └── models.py
├── requirements.txt
├── intelligent_data_analyzer.py
├── intelligent_data_processor.py
├── automl_pipeline.py
├── model_registry.py
├── cognitive_engine.py
├── data_pre_processor.py
├── file_handler.py
└── prompts.py
```

### Step 2: Update Requirements

Add your dependencies to `backend/requirements.txt`:
```
# Existing
fastapi==0.104.1
uvicorn==0.24.0
websockets==12.0
python-multipart==0.0.6
pandas==2.1.3
numpy==1.26.2
scikit-learn==1.3.2
joblib==1.3.2
torch==2.1.1
python-dotenv==1.0.0

# Your additional dependencies
# (add any specialized libraries your code uses)
```

### Step 3: Update main.py to Use Your Pipeline

Replace the placeholder training function in `backend/main.py`:

```python
# In main.py, replace run_training_pipeline with:

async def run_training_pipeline(project_name: str, config: InputConfiguration):
    """Background training pipeline using your code"""
    try:
        import pandas as pd
        from automl_pipeline import preprocess_train, train
        from file_handler import open_file
        
        # Load data
        df = open_file(config.file_name)
        
        await manager.broadcast(project_name, {
            "type": "status",
            "message": f"Data loaded: {df.shape[0]} rows, {df.shape[1]} columns",
            "progress": 15
        })
        
        # Run your pipeline
        if config.processing_type == ProcessingType.PREPROCESS_TRAIN:
            await manager.broadcast(project_name, {
                "type": "status",
                "message": "Starting data preprocessing...",
                "progress": 20
            })
            
            result = preprocess_train(config, df)
            
        else:
            await manager.broadcast(project_name, {
                "type": "status",
                "message": "Starting training...",
                "progress": 40
            })
            
            result = train(config, df)
        
        # Save results
        metadata_file = Path(config.output_folder) / "metadata.json"
        metadata = {
            "project_name": project_name,
            "created_at": datetime.now().isoformat(),
            "status": "completed",
            "config": config.to_dict(),
            "best_model": result.get('best_model_name'),
            "evaluation_scores": result.get('evaluation_scores'),
            "models_trained": len(result.get('trained_models', {}))
        }
        
        metadata_file.write_text(json.dumps(metadata, indent=2))
        
        await manager.broadcast(project_name, {
            "type": "complete",
            "message": "Training complete!",
            "progress": 100,
            "result": metadata
        })
        
        projects_registry[project_name]["status"] = "completed"
        
    except RuntimeError as e:
        # Handle resource exhaustion
        if "out of memory" in str(e).lower() or "cuda" in str(e).lower():
            await manager.broadcast(project_name, {
                "type": "status",
                "message": "GPU memory exhausted, falling back to CPU...",
                "progress": 30
            })
            config.acceleration_hardware = Hardware.CPU
            # Retry with CPU
            # ... retry logic
        else:
            await manager.broadcast(project_name, {
                "type": "error",
                "message": f"Training failed: {str(e)}",
                "error": str(e)
            })
            projects_registry[project_name]["status"] = "failed"
            
    except Exception as e:
        logger.error(f"Training failed: {e}")
        await manager.broadcast(project_name, {
            "type": "error",
            "message": f"Training failed: {str(e)}",
            "error": str(e)
        })
        projects_registry[project_name]["status"] = "failed"
```

### Step 4: Update Progress Broadcasting

Add progress updates throughout your pipeline:

**In intelligent_data_analyzer.py:**
```python
async def broadcast_status(client_id, message, progress):
    """Broadcast training status to frontend"""
    from main import manager
    await manager.broadcast(client_id, {
        "type": "status",
        "message": message,
        "progress": progress
    })
```

**In automl_pipeline.py:**
```python
# After each major step, broadcast progress
await broadcast_status(project_name, "Analyzing data...", 20)
await broadcast_status(project_name, "Preprocessing data...", 35)
await broadcast_status(project_name, "Training models...", 60)
await broadcast_status(project_name, "Evaluating results...", 85)
```

### Step 5: Add Prediction Endpoint

Implement prediction in your backend code:

```python
# In main.py, add:

@app.post("/api/predict")
async def predict(file: UploadFile = File(...), project_name: str = None):
    """Make predictions using trained model"""
    try:
        import joblib
        import pandas as pd
        
        # Load trained model
        project_folder = PROJECTS_DIR / project_name
        model = joblib.load(project_folder / "best_model.pkl")
        data_prep = joblib.load(project_folder / "data_prep.pkl")
        
        # Load prediction data
        contents = await file.read()
        temp_path = f"temp_pred_{datetime.now().timestamp()}.csv"
        
        with open(temp_path, "wb") as f:
            f.write(contents)
        
        df = pd.read_csv(temp_path)
        
        # Preprocess and predict
        X = data_prep.transform(df)
        predictions = model.predict(X)
        
        return {
            "predictions": predictions.tolist(),
            "count": len(predictions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Step 6: Handle LLM Configuration

Your `LLMConfiguration` class is already in `core/models.py`. Update it to work with environment variables:

```python
# In core/models.py
from dotenv import load_dotenv, set_key

class LLMConfiguration:
    def __init__(self, model_name: Optional[str] = None, api_key: Optional[str] = None):
        load_dotenv(".env")
        
        self.model_name = model_name or os.getenv("LLM_MODEL_NAME")
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        
        if not self.api_key:
            raise ValueError("API key not provided and not found in .env")
        
        self._save_to_env()
    
    def _save_to_env(self):
        set_key(".env", "LLM_MODEL_NAME", self.model_name)
        set_key(".env", "LLM_API_KEY", self.api_key)
```

## Data Flow Integration

```
Frontend Upload
    ↓
FastAPI /api/upload
    ↓
Temporary CSV storage
    ↓
FastAPI /api/analyze
    ↓
Frontend Configure (ML type, target, etc.)
    ↓
FastAPI /api/train (start background task)
    ↓
run_training_pipeline() calls YOUR CODE:
    1. open_file() - Load CSV
    2. IntelligentDataAnalyzer.analyze_dataframe()
    3. DataPrepAgent preprocessing (if enabled)
    4. run_train() - Train models
    5. evaluate() - Evaluate
    ↓
WebSocket broadcasts progress to frontend
    ↓
Results saved to projects/{project_name}/
    ↓
Frontend displays results
```

## Error Handling Patterns

### GPU Memory Exhaustion
```python
try:
    result = run_train(config, X_train, y_train)
except RuntimeError as e:
    if torch.cuda.is_available() and "CUDA" in str(e):
        config.acceleration_hardware = Hardware.CPU
        result = run_train(config, X_train, y_train)
    else:
        raise
```

### Data Validation
```python
# In your pipeline
if config.target_column not in df.columns:
    raise ValueError(f"Target column '{config.target_column}' not found")

if df.empty:
    raise ValueError("Dataset is empty")
```

### Resource Monitoring
```python
import psutil

def check_resources():
    """Check available memory and GPU"""
    memory_percent = psutil.virtual_memory().percent
    if memory_percent > 90:
        # Reduce batch size or switch to CPU
        config.acceleration_hardware = Hardware.CPU
```

## Testing Integration

1. **Unit Tests**
```python
# backend/tests/test_pipeline.py
import pytest
from automl_pipeline import train

def test_training_pipeline():
    """Test your training pipeline"""
    # ...
```

2. **Integration Tests**
```bash
# Test full flow
curl -X POST http://localhost:8000/api/upload -F "file=@test.csv"
curl -X POST http://localhost:8000/api/analyze -H "Content-Type: application/json" -d '{"temp_path":"..."}'
curl -X POST http://localhost:8000/api/train -H "Content-Type: application/json" -d '{...}'
```

## Performance Optimization

1. **Async Processing**
   - Use `asyncio` for concurrent operations
   - Don't block on heavy computations in FastAPI handlers

2. **Memory Management**
   - Use generators for large datasets
   - Clean up temporary files after training
   - Save only necessary model artifacts

3. **GPU Optimization**
   - Batch operations when possible
   - Use mixed precision training
   - Monitor CUDA memory

## Debugging

Enable detailed logging:

```python
# In main.py
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# In your pipeline
logger.debug(f"Processing data shape: {df.shape}")
logger.info(f"Training on {len(X_train)} samples")
logger.error(f"Error occurred: {error_message}")
```

## Common Issues

### Import Errors
```python
# Make sure all modules are in PYTHONPATH
import sys
sys.path.insert(0, '/path/to/backend')
```

### Missing Dependencies
```bash
# Ensure all required packages are installed
pip install -r backend/requirements.txt
```

### WebSocket Connection Issues
```javascript
// Frontend - check browser console
console.log("Connecting to WebSocket...");
// Should see: "WebSocket connected"
```

## Next Steps

1. Copy your code to `backend/`
2. Update `requirements.txt`
3. Modify `run_training_pipeline()` to use your code
4. Test with sample CSV
5. Monitor logs for errors
6. Deploy to production

## Support

For integration issues:
1. Check logs in terminal
2. Verify all modules are copied
3. Test individual functions with print statements
4. Use debugger: `import pdb; pdb.set_trace()`
