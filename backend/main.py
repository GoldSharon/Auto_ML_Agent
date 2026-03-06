from fastapi import FastAPI, WebSocket, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import asyncio
import logging
from pathlib import Path
from datetime import datetime
import torch
import shutil
import traceback
import pandas as pd
from io import StringIO

# Import your ML modules
from core.models import (
    InputConfiguration, MLType, LearningType, ProcessingType, Hardware
)
from file_handler import open_file
from services import create_new_project_folder, run_automl, restore_session, predict_new_data
from data_pre_processor import canonicalize_columns

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global variables for WebSocket management
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}
        self.project_status: dict = {}
    
    async def connect(self, websocket: WebSocket, project_name: str):
        await websocket.accept()
        self.active_connections[project_name] = websocket
        self.project_status[project_name] = {"status": "connected"}
    
    async def disconnect(self, project_name: str):
        if project_name in self.active_connections:
            del self.active_connections[project_name]
    
    async def broadcast(self, project_name: str, message: dict):
        if project_name in self.active_connections:
            try:
                await self.active_connections[project_name].send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to {project_name}: {e}")
    
    def get_project_status(self, project_name: str):
        return self.project_status.get(project_name, {})
    
    def update_project_status(self, project_name: str, status: dict):
        self.project_status[project_name] = status

manager = ConnectionManager()
projects_registry = {}

# Project directory setup
PROJECTS_DIR = Path("projects")
PROJECTS_DIR.mkdir(exist_ok=True)

async def lifespan(app: FastAPI):
    # Startup
    logger.info("AutoML Backend starting...")
    yield
    # Shutdown
    logger.info("Application shutting down...")

app = FastAPI(title="AutoML API", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= ROUTES =============

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "gpu_available": torch.cuda.is_available(),
        "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "N/A"
    }

@app.get("/api/env-status")
async def check_env():
    """Check if .env file exists and has LLM config"""
    env_file = ".env"
    env_exists = Path(env_file).exists()
    
    if env_exists:
        with open(env_file) as f:
            env_content = f.read()
            has_llm_model = "LLM_MODEL_NAME" in env_content
            has_llm_key = "LLM_API_KEY" in env_content
    else:
        has_llm_model = False
        has_llm_key = False
    
    return {
        "env_exists": env_exists,
        "has_llm_config": has_llm_model and has_llm_key,
        "needs_setup": not (has_llm_model and has_llm_key)
    }

@app.post("/api/setup-llm")
async def setup_llm(data: dict):
    """Setup LLM configuration"""
    try:
        llm_model = data.get("llm_model")
        llm_api_key = data.get("llm_api_key")
        
        if not llm_model or not llm_api_key:
            raise HTTPException(status_code=400, detail="Missing LLM credentials")
        
        # Save to .env
        from dotenv import set_key
        set_key(".env", "LLM_MODEL_NAME", llm_model)
        set_key(".env", "LLM_API_KEY", llm_api_key)
        
        return {"status": "success", "message": "LLM configuration saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/projects")
async def list_projects():
    """List all projects"""
    projects = []
    for project_dir in PROJECTS_DIR.iterdir():
        if project_dir.is_dir():
            metadata_file = project_dir / "metadata.json"
            if metadata_file.exists():
                metadata = json.loads(metadata_file.read_text())
                projects.append(metadata)
    
    return {"projects": sorted(projects, key=lambda x: x.get("created_at", ""), reverse=True)}

@app.post("/api/upload")
async def upload_csv(file: UploadFile = File(...)):
    """Upload CSV file"""
    try:
        contents = await file.read()
        temp_path = f"temp_{datetime.now().timestamp()}.csv"
        
        with open(temp_path, "wb") as f:
            f.write(contents)
        
        return {
            "filename": file.filename,
            "temp_path": temp_path,
            "size": len(contents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze")
async def analyze_data(data: dict):
    """Analyze uploaded CSV"""
    try:
        import pandas as pd
        
        temp_path = data.get("temp_path")
        if not temp_path or not Path(temp_path).exists():
            raise HTTPException(status_code=400, detail="File not found")
        
        df = pd.read_csv(temp_path)
        
        return {
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "missing_values": df.isnull().sum().to_dict(),
            "head": df.head(5).to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/train")
async def start_training(data: dict, background_tasks: BackgroundTasks):
    """Start training with WebSocket"""
    try:
        project_name = data.get("project_name")
        ml_type = MLType[data.get("ml_type", "SUPERVISED")]
        learning_type = LearningType[data.get("learning_type", "REGRESSION")]
        processing_type = ProcessingType[data.get("processing_type", "TRAINING_ONLY")]
        target_column = data.get("target_column")
        test_size = float(data.get("test_size", 0.2))
        hyper_parameter_tuning = data.get("hyper_parameter_tuning", False)
        
        # Create project folder
        project_folder = PROJECTS_DIR / project_name
        project_folder.mkdir(exist_ok=True)
        
        config = InputConfiguration(
            project_name=project_name,
            file_name=data.get("temp_path"),
            ml_type=ml_type,
            learning_type=learning_type,
            processing_type=processing_type,
            llm_name=os.getenv("LLM_MODEL_NAME", "default"),
            target_column=target_column,
            output_folder=str(project_folder),
            acceleration_hardware=Hardware.GPU if torch.cuda.is_available() else Hardware.CPU,
            test_size=test_size,
            hyper_parameter_tuning=hyper_parameter_tuning
        )
        
        # Store in registry
        projects_registry[project_name] = {
            "config": config,
            "status": "queued",
            "progress": 0
        }
        
        # Start training in background
        background_tasks.add_task(run_training_pipeline, project_name, config)
        
        return {
            "project_name": project_name,
            "status": "training_started",
            "project_id": project_name
        }
    except Exception as e:
        logger.error(f"Training error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def run_training_pipeline(project_name: str, config: InputConfiguration):
    """Background training pipeline using actual ML code with progress updates"""
    try:
        loop = asyncio.get_event_loop()
        
        await manager.broadcast(project_name, {
            "type": "status",
            "message": "Initializing AutoML pipeline...",
            "progress": 5
        })
        
        # Load data using file_handler
        df = await loop.run_in_executor(None, open_file, config.file_name)
        if df is None:
            raise ValueError(f"Failed to load file: {config.file_name}")
        
        await manager.broadcast(project_name, {
            "type": "status",
            "message": f"✓ Data loaded: {df.shape[0]} rows × {df.shape[1]} columns",
            "progress": 15
        })
        
        # Data Analysis
        await manager.broadcast(project_name, {
            "type": "status",
            "message": "Analyzing data with LLM...",
            "progress": 20
        })
        
        def run_automl_sync(df, config):
            """Synchronous wrapper for AutoML"""
            return run_automl(df, config)
        
        # Run AutoML pipeline
        result = await loop.run_in_executor(None, run_automl_sync, df, config)
        
        if config.processing_type == ProcessingType.PREPROCESS_TRAIN:
            await manager.broadcast(project_name, {
                "type": "status",
                "message": "✓ Data preprocessing and feature engineering complete",
                "progress": 45
            })
        
        await manager.broadcast(project_name, {
            "type": "status",
            "message": "Training multiple models...",
            "progress": 50
        })
        
        trained_models = result.get('trained_models', {})
        evaluation_scores = result.get('evaluation_scores', {})
        best_model_name = result.get('best_model_name', '')
        
        await manager.broadcast(project_name, {
            "type": "status",
            "message": f"✓ Trained {len(trained_models)} models",
            "progress": 75
        })
        
        await manager.broadcast(project_name, {
            "type": "status",
            "message": "Evaluating models on test set...",
            "progress": 85
        })
        
        # Save metadata
        metadata_file = Path(config.output_folder) / "metadata.json"
        metadata = {
            "project_name": project_name,
            "created_at": datetime.now().isoformat(),
            "status": "completed",
            "config": {
                "ml_type": config.ml_type.value,
                "learning_type": config.learning_type.value,
                "processing_type": config.processing_type.value,
                "target_column": config.target_column,
                "test_size": config.test_size,
                "hyper_parameter_tuning": config.hyper_parameter_tuning
            },
            "best_model": best_model_name,
            "models_trained": list(trained_models.keys()),
            "evaluation_scores": evaluation_scores,
            "output_folder": config.output_folder
        }
        
        metadata_file.write_text(json.dumps(metadata, indent=2))
        
        # Read evaluation scores
        eval_scores_path = Path(config.output_folder) / "evaluation_scores.json"
        eval_scores = {}
        if eval_scores_path.exists():
            eval_scores = json.loads(eval_scores_path.read_text())
        
        await manager.broadcast(project_name, {
            "type": "complete",
            "message": f"✓ Training complete! Best model: {best_model_name}",
            "progress": 100,
            "result": {
                **metadata,
                "evaluation_scores": eval_scores
            }
        })
        
        projects_registry[project_name]["status"] = "completed"
        logger.info(f"Project {project_name} completed successfully")
        
    except Exception as e:
        logger.error(f"Training failed for {project_name}: {e}\n{traceback.format_exc()}")
        await manager.broadcast(project_name, {
            "type": "error",
            "message": f"Training failed: {str(e)}",
            "error": str(e),
            "details": traceback.format_exc()
        })
        projects_registry[project_name]["status"] = "failed"

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket for real-time progress updates"""
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "subscribe":
                # Client subscribes to project updates
                pass
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await manager.disconnect(client_id)

@app.get("/api/project/{project_name}")
async def get_project(project_name: str):
    """Get project details"""
    project_folder = PROJECTS_DIR / project_name
    metadata_file = project_folder / "metadata.json"
    
    if not metadata_file.exists():
        raise HTTPException(status_code=404, detail="Project not found")
    
    return json.loads(metadata_file.read_text())

@app.get("/api/project/{project_name}/download")
async def download_evaluation(project_name: str):
    """Download evaluation scores"""
    project_folder = PROJECTS_DIR / project_name
    eval_file = project_folder / "evaluation_scores.json"
    
    if not eval_file.exists():
        raise HTTPException(status_code=404, detail="Evaluation file not found")
    
    return json.loads(eval_file.read_text())

@app.post("/api/predict/{project_name}")
async def make_prediction(project_name: str, data: dict):
    """Make predictions using trained model"""
    try:
        project_folder = PROJECTS_DIR / project_name
        
        # Check if project exists
        metadata_file = project_folder / "metadata.json"
        if not metadata_file.exists():
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Load CSV data from request
        csv_string = data.get("csv_data", "")
        if not csv_string:
            raise HTTPException(status_code=400, detail="No CSV data provided")
        
        # Parse CSV
        df = pd.read_csv(StringIO(csv_string))
        
        loop = asyncio.get_event_loop()
        
        # Make predictions
        def predict_sync(df, project_folder):
            return predict_new_data(df, str(project_folder))
        
        results = await loop.run_in_executor(None, predict_sync, df, project_folder)
        
        return {
            "status": "success",
            "predictions_count": len(results),
            "results": results.to_dict(orient="records"),
            "csv_download": results.to_csv(index=False)
        }
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/project/{project_name}/files")
async def get_project_files(project_name: str):
    """Get all files in project"""
    try:
        project_folder = PROJECTS_DIR / project_name
        
        if not project_folder.exists():
            raise HTTPException(status_code=404, detail="Project not found")
        
        files = {
            "exists": True,
            "files": []
        }
        
        for file in project_folder.rglob("*"):
            if file.is_file():
                files["files"].append({
                    "name": file.name,
                    "size": file.stat().st_size,
                    "path": str(file.relative_to(project_folder))
                })
        
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/project/{project_name}/report")
async def get_project_report(project_name: str):
    """Get detailed project report"""
    try:
        project_folder = PROJECTS_DIR / project_name
        
        report = {
            "project_name": project_name,
            "metadata": None,
            "preprocessing_config": None,
            "evaluation_scores": None
        }
        
        # Load metadata
        metadata_file = project_folder / "metadata.json"
        if metadata_file.exists():
            report["metadata"] = json.loads(metadata_file.read_text())
        
        # Load preprocessing config
        prep_config_file = project_folder / "preprocessing_config.json"
        if prep_config_file.exists():
            report["preprocessing_config"] = json.loads(prep_config_file.read_text())
        
        # Load evaluation scores
        eval_file = project_folder / "evaluation_scores.json"
        if eval_file.exists():
            report["evaluation_scores"] = json.loads(eval_file.read_text())
        
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/project/{project_name}")
async def delete_project(project_name: str):
    """Delete a project"""
    try:
        project_folder = PROJECTS_DIR / project_name
        
        if not project_folder.exists():
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Remove project directory
        shutil.rmtree(project_folder)
        
        # Remove from registry
        if project_name in projects_registry:
            del projects_registry[project_name]
        
        return {"status": "success", "message": f"Project {project_name} deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
