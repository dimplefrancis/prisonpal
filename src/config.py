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

# URLs
GOV_UK_BASE_URL = os.getenv('GOV_UK_BASE_URL', 'https://www.gov.uk/government/publications/management-of-security-at-visits-policy-framework-closed-estate')
GOV_UK_ID_URL = os.getenv('GOV_UK_ID_URL', 'https://www.gov.uk/government/publications/management-of-security-at-visits-policy-framework-open-estate/acceptable-forms-of-identification-id-when-visiting-a-prison-in-england-and-wales-annex-a')
GOV_UK_DRESS_CODE_URL = os.getenv('GOV_UK_DRESS_CODE_URL', 'https://www.gov.uk/government/publications/management-of-security-at-visits-policy-framework-closed-estate/dress-code-for-visitors-annex-h')

# Model Configuration
COHERE_EMBEDDING_MODEL = "embed-english-v3.0"
COHERE_CHAT_MODEL = "command-r7b-12-2024"

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

# Validate configuration on import
validate_config()