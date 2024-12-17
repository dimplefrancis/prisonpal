"""Configuration settings for the Prison Visitor Assistant."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
COHERE_API_KEY = os.getenv('COHERE_API_KEY')
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')

# Qdrant Configuration
QDRANT_URL = os.getenv('QDRANT_URL')
COLLECTION_NAME = "prison_visitor_assistant"

# Model Configuration
COHERE_EMBEDDING_MODEL = "embed-english-v3.0"
COHERE_CHAT_MODEL = "command-r7b-12-2024"

# Document Paths
PDF_PATHS = {
    'dress_code': 'data/Dresscode.pdf',
    'id': 'data/ID.pdf',
    'policy': 'data/policy.pdf'
}

# Validation
def validate_config():
    """Validate that all required environment variables are set."""
    required_vars = {
        'COHERE_API_KEY': COHERE_API_KEY,
        'QDRANT_API_KEY': QDRANT_API_KEY,
        'QDRANT_URL': QDRANT_URL
    }
    
    missing_vars = [var_name for var_name, var_value in required_vars.items() 
                   if not var_value]
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

    # Validate PDF paths exist
    for name, path in PDF_PATHS.items():
        if not os.path.exists(path):
            raise ValueError(f"PDF file not found: {path}")

# Validate configuration on import
validate_config()
