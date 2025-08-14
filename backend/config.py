"""
Configuration management for StudyMate with HuggingFace Models
"""

import os
from pathlib import Path
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration with HuggingFace model support"""

    # Base paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    UPLOAD_DIR = DATA_DIR / "uploads"
    PROCESSED_DIR = DATA_DIR / "processed"
    EMBEDDINGS_DIR = DATA_DIR / "embeddings"
    LOGS_DIR = BASE_DIR / "logs"
    TEMP_DIR = BASE_DIR / "temp"
    MODELS_DIR = BASE_DIR / "models"

    # App settings
    APP_TITLE = "StudyMate - AI Academic Assistant"
    APP_ICON = "📚"
    MAX_FILE_SIZE_MB = 50
    MAX_FILES_UPLOAD = 10

    # HuggingFace Model Configuration
    HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "")

    # Available Models
    AVAILABLE_MODELS = {
        "flan-t5": {
            "name": "FLAN-T5 Small",
            "model_id": "google/flan-t5-small",
            "description": "Google's instruction-tuned T5 model - best for accurate Q&A",
            "max_length": 512,
            "temperature": 0.3,
            "type": "text2text"
        },
        "flan-t5-base": {
            "name": "FLAN-T5 Base",
            "model_id": "google/flan-t5-base",
            "description": "Larger FLAN-T5 model - more accurate but slower",
            "max_length": 512,
            "temperature": 0.3,
            "type": "text2text"
        },
        "distilgpt2": {
            "name": "DistilGPT-2",
            "model_id": "distilgpt2",
            "description": "Lightweight GPT-2 - fast but less accurate for Q&A",
            "max_length": 1024,
            "temperature": 0.7,
            "type": "causal"
        }
    }

    # Default model - use FLAN-T5 for better Q&A accuracy
    DEFAULT_MODEL = "flan-t5"

    # Embedding Model Configuration
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION = 384

    # FAISS Configuration
    FAISS_INDEX_TYPE = "IndexFlatIP"  # Inner Product for cosine similarity
    FAISS_NLIST = 100  # For IVF indices
    FAISS_NPROBE = 10  # For search

    # Text processing
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    MIN_CHUNK_SIZE = 100

    # Search settings
    MAX_SEARCH_RESULTS = 10
    MIN_SIMILARITY_SCORE = 0.1

    # Generation settings
    MAX_NEW_TOKENS = 512
    TEMPERATURE = 0.7
    TOP_P = 0.9
    TOP_K = 50
    DO_SAMPLE = True

    # File settings
    ALLOWED_EXTENSIONS = ["pdf", "txt"]

    # UI settings
    THEME_PRIMARY = "#6366f1"
    THEME_SECONDARY = "#06b6d4"
    THEME_SUCCESS = "#10b981"
    THEME_WARNING = "#f59e0b"
    THEME_ERROR = "#ef4444"

    @classmethod
    def create_directories(cls):
        """Create necessary directories"""
        directories = [
            cls.DATA_DIR, cls.UPLOAD_DIR, cls.PROCESSED_DIR,
            cls.EMBEDDINGS_DIR, cls.LOGS_DIR, cls.TEMP_DIR, cls.MODELS_DIR
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

            # Create .gitkeep files
            gitkeep = directory / ".gitkeep"
            if not gitkeep.exists():
                gitkeep.touch()

    @classmethod
    def setup_logging(cls):
        """Setup logging configuration"""
        log_file = cls.LOGS_DIR / "studymate.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

        return logging.getLogger(__name__)

    @classmethod
    def get_model_config(cls, model_key: str = None):
        """Get configuration for a specific model"""
        if model_key is None:
            model_key = cls.DEFAULT_MODEL

        return cls.AVAILABLE_MODELS.get(model_key, cls.AVAILABLE_MODELS[cls.DEFAULT_MODEL])

# Initialize
config = Config()
config.create_directories()
logger = config.setup_logging()
