"""
Configuration module.

This module handles loading and managing configuration settings.
"""
import os
import logging
from typing import Dict, Any
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

def load_config() -> Dict[str, Any]:
    """
    Load configuration from environment variables.
    
    Returns:
        A dictionary containing configuration settings
    """
    # Load environment variables from .env file
    load_dotenv()
    
    # Load configuration from environment variables
    config = {
        'model': os.environ.get("OLLAMA_MODEL", "llama2"),
        'url': os.environ.get("OLLAMA_URL", "http://localhost:11434"),
        'timeout': int(os.environ.get("OLLAMA_TIMEOUT", "60")),  # Timeout in seconds
        'db_host': os.environ.get("DB_HOST", "localhost"),
        'db_port': os.environ.get("DB_PORT", "5432"),
        'db_name': os.environ.get("DB_NAME", "thoughts_db"),
        'db_user': os.environ.get("DB_USER", "postgres"),
        'db_password': os.environ.get("DB_PASSWORD", "postgres"),
        # Whisper configuration
        'whisper_model': os.environ.get("WHISPER_MODEL", "large-v3"),
        'device': os.environ.get("DEVICE", "cpu"),
        'compute_type': os.environ.get("COMPUTE_TYPE", "int8"),
        'cpu_threads': int(os.environ.get("CPU_THREADS", "4")),
        'beam_size': int(os.environ.get("BEAM_SIZE", "5")),
        'model_dir': os.environ.get("MODEL_DIR", None),
        'condition_on_previous_text': os.environ.get("CONDITION_ON_PREVIOUS_TEXT", "True").lower() == "true"
    }
    
    logger.info(f"Configuration loaded: model={config['model']}, url={config['url']}, db_host={config['db_host']}")
    
    return config
