"""
Advanced API Configuration for StudyMate
"""

import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator, ConfigDict
import secrets

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application Info
    app_name: str = "StudyMate API"
    app_version: str = "2.0.0"
    app_description: str = "Advanced AI Academic Assistant with IBM Granite Integration"
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    debug: bool = Field(default=False, env="DEBUG")
    reload: bool = Field(default=False, env="RELOAD")
    
    # Security
    secret_key: str = Field(default_factory=lambda: secrets.token_urlsafe(32), env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # CORS Settings
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8501", "http://localhost:8502"],
        env="ALLOWED_ORIGINS"
    )
    allowed_methods: List[str] = Field(default=["*"], env="ALLOWED_METHODS")
    allowed_headers: List[str] = Field(default=["*"], env="ALLOWED_HEADERS")
    
    # Database Configuration
    database_url: str = Field(
        default="postgresql://studymate:studymate@localhost/studymate_db",
        env="DATABASE_URL"
    )
    database_echo: bool = Field(default=False, env="DATABASE_ECHO")
    
    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # HuggingFace Configuration
    huggingface_token: Optional[str] = Field(default=None, env="HUGGINGFACE_TOKEN")
    huggingface_cache_dir: str = Field(default="./models/huggingface", env="HUGGINGFACE_CACHE_DIR")
    
    # IBM Granite Model Configuration
    granite_models: dict = Field(default={
        "granite-3b-code-instruct": {
            "model_id": "ibm-granite/granite-3b-code-instruct",
            "name": "IBM Granite 3B Code Instruct",
            "description": "IBM's Granite model optimized for code and instruction following",
            "max_length": 2048,
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 50
        },
        "granite-8b-code-instruct": {
            "model_id": "ibm-granite/granite-8b-code-instruct", 
            "name": "IBM Granite 8B Code Instruct",
            "description": "Advanced IBM Granite model for complex code understanding",
            "max_length": 4096,
            "temperature": 0.6,
            "top_p": 0.9,
            "top_k": 40
        },
        "granite-13b-instruct": {
            "model_id": "ibm-granite/granite-13b-instruct-v2",
            "name": "IBM Granite 13B Instruct",
            "description": "Large IBM Granite model for advanced reasoning",
            "max_length": 4096,
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 50
        }
    })
    
    # Default model
    default_granite_model: str = Field(default="granite-3b-code-instruct", env="DEFAULT_GRANITE_MODEL")
    
    # Embedding Configuration
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        env="EMBEDDING_MODEL"
    )
    embedding_dimension: int = Field(default=384, env="EMBEDDING_DIMENSION")
    
    # FAISS Configuration
    faiss_index_type: str = Field(default="IndexFlatIP", env="FAISS_INDEX_TYPE")
    faiss_nlist: int = Field(default=100, env="FAISS_NLIST")
    faiss_nprobe: int = Field(default=10, env="FAISS_NPROBE")
    
    # File Processing
    max_file_size_mb: int = Field(default=100, env="MAX_FILE_SIZE_MB")
    max_files_per_upload: int = Field(default=20, env="MAX_FILES_PER_UPLOAD")
    allowed_file_types: List[str] = Field(default=["pdf", "txt", "docx"], env="ALLOWED_FILE_TYPES")
    
    # Text Processing
    chunk_size: int = Field(default=1000, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, env="CHUNK_OVERLAP")
    min_chunk_size: int = Field(default=100, env="MIN_CHUNK_SIZE")
    
    # Search Configuration
    max_search_results: int = Field(default=10, env="MAX_SEARCH_RESULTS")
    min_similarity_score: float = Field(default=0.1, env="MIN_SIMILARITY_SCORE")
    
    # Generation Configuration
    max_new_tokens: int = Field(default=512, env="MAX_NEW_TOKENS")
    default_temperature: float = Field(default=0.7, env="DEFAULT_TEMPERATURE")
    default_top_p: float = Field(default=0.9, env="DEFAULT_TOP_P")
    default_top_k: int = Field(default=50, env="DEFAULT_TOP_K")
    
    # Directory Configuration
    base_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent)
    data_dir: Optional[Path] = Field(default=None)
    upload_dir: Optional[Path] = Field(default=None)
    processed_dir: Optional[Path] = Field(default=None)
    embeddings_dir: Optional[Path] = Field(default=None)
    models_dir: Optional[Path] = Field(default=None)
    logs_dir: Optional[Path] = Field(default=None)
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    
    # Rate Limiting
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")  # seconds
    
    # Monitoring
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_directories()
    
    def _setup_directories(self):
        """Setup directory paths"""
        if self.data_dir is None:
            self.data_dir = self.base_dir / "data"
        
        if self.upload_dir is None:
            self.upload_dir = self.data_dir / "uploads"
        
        if self.processed_dir is None:
            self.processed_dir = self.data_dir / "processed"
        
        if self.embeddings_dir is None:
            self.embeddings_dir = self.data_dir / "embeddings"
        
        if self.models_dir is None:
            self.models_dir = self.base_dir / "models"
        
        if self.logs_dir is None:
            self.logs_dir = self.base_dir / "logs"
        
        # Create directories
        for directory in [
            self.data_dir, self.upload_dir, self.processed_dir,
            self.embeddings_dir, self.models_dir, self.logs_dir
        ]:
            directory.mkdir(parents=True, exist_ok=True)
    
    @validator('allowed_origins', pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @validator('allowed_file_types', pre=True)
    def parse_file_types(cls, v):
        if isinstance(v, str):
            return [ft.strip().lower() for ft in v.split(',')]
        return v
    
    def get_granite_model_config(self, model_key: str = None) -> dict:
        """Get configuration for a specific Granite model"""
        if model_key is None:
            model_key = self.default_granite_model
        
        return self.granite_models.get(model_key, self.granite_models[self.default_granite_model])
    
    def get_database_url(self, async_driver: bool = False) -> str:
        """Get database URL with optional async driver"""
        if async_driver and self.database_url.startswith("postgresql://"):
            return self.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return self.database_url
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignore extra fields from .env
    )

# Global settings instance
settings = Settings()

# Export commonly used paths
BASE_DIR = settings.base_dir
DATA_DIR = settings.data_dir
UPLOAD_DIR = settings.upload_dir
PROCESSED_DIR = settings.processed_dir
EMBEDDINGS_DIR = settings.embeddings_dir
MODELS_DIR = settings.models_dir
LOGS_DIR = settings.logs_dir
