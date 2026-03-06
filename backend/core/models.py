from dataclasses import dataclass, asdict
from typing import Optional
from enum import Enum
from dotenv import load_dotenv, set_key
import os
import json
from pathlib import Path

class MLType(Enum):
    SUPERVISED = "Supervised"
    UNSUPERVISED = "Unsupervised"

class LearningType(Enum):
    REGRESSION = "Regression"
    CLASSIFICATION = "Classification"
    CLUSTERING = "Clustering"
    APRIORI = "Apriori"

class ProcessingType(Enum):
    TRAINING_ONLY = "Training-Alone"
    PREPROCESS_TRAIN = "Pre-Processes+Training"

class Hardware(Enum):
    CPU = "CPU"
    GPU = "GPU"
    HYBRID = "Hybrid"

@dataclass
class InputConfiguration:
    project_name: str
    file_name: str
    ml_type: MLType
    learning_type: LearningType
    processing_type: ProcessingType
    llm_name: str
    target_column: Optional[str] = None
    index_column: Optional[str] = None
    output_folder: str = None
    acceleration_hardware: Hardware = Hardware.CPU
    test_size: Optional[float] = 0.2
    hyper_parameter_tuning: bool = False

    def __post_init__(self):
        if self.ml_type == MLType.SUPERVISED and not self.target_column:
            raise ValueError("target_column is required for supervised learning")

    def to_dict(self):
        return {
            'project_name': self.project_name,
            'file_name': self.file_name,
            'ml_type': self.ml_type.value,
            'learning_type': self.learning_type.value,
            'processing_type': self.processing_type.value,
            'llm_name': self.llm_name,
            'target_column': self.target_column,
            'index_column': self.index_column,
            'output_folder': self.output_folder,
            'acceleration_hardware': self.acceleration_hardware.value,
            'test_size': self.test_size,
            'hyper_parameter_tuning': self.hyper_parameter_tuning
        }

ENV_FILE = ".env"

class LLMConfiguration:
    def __init__(self, model_name: Optional[str] = None, api_key: Optional[str] = None):
        load_dotenv(ENV_FILE)
        
        self.model_name = model_name or os.getenv("LLM_MODEL_NAME")
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        
        if not self.api_key:
            raise ValueError("API key not provided and not found in .env")
        
        self._save_to_env()
    
    def _save_to_env(self):
        set_key(ENV_FILE, "LLM_MODEL_NAME", self.model_name)
        set_key(ENV_FILE, "LLM_API_KEY", self.api_key)

class ProjectMetadata:
    """Manage project metadata stored as JSON"""
    
    def __init__(self, project_name: str, output_folder: str):
        self.project_name = project_name
        self.output_folder = output_folder
        self.metadata_file = Path(output_folder) / "metadata.json"
    
    def save(self, config: InputConfiguration, status: str = "training"):
        """Save project metadata"""
        metadata = {
            "project_name": self.project_name,
            "created_at": str(Path(self.output_folder).stat().st_ctime),
            "status": status,
            "config": config.to_dict(),
            "models": [],
            "evaluation_scores": None,
            "best_model": None
        }
        
        self.metadata_file.write_text(json.dumps(metadata, indent=2))
    
    def load(self):
        """Load project metadata"""
        if self.metadata_file.exists():
            return json.loads(self.metadata_file.read_text())
        return None
    
    def update(self, **kwargs):
        """Update project metadata"""
        metadata = self.load() or {}
        metadata.update(kwargs)
        self.metadata_file.write_text(json.dumps(metadata, indent=2))
