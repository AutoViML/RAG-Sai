import json
import os
from typing import Dict, Any

CONFIG_FILE = "active_config.json"

DEFAULT_CONFIG = {
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "chunker_type": "semantic",
    "embedding_model": "text-embedding-3-small",
    "use_contextual_enrichment": False
}

def load_active_config() -> Dict[str, Any]:
    """Load the currently active ingestion configuration."""
    if not os.path.exists(CONFIG_FILE):
        return DEFAULT_CONFIG
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return DEFAULT_CONFIG

def save_active_config(config: Dict[str, Any]):
    """Save the active configuration."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def get_active_embedding_model() -> str:
    """Get the embedding model name from active config."""
    config = load_active_config()
    return config.get("embedding_model", "text-embedding-3-small")
