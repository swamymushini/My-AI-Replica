import os

def load_env_file():
    """Load environment variables from .env file if it exists"""
    try:
        with open('.env', 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    except FileNotFoundError:
        pass  # .env file doesn't exist, use system environment variables

def get_api_key():
    """Get Google API key from environment variable"""
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise Exception("GOOGLE_API_KEY environment variable not set")
    return api_key

def get_perplexity_api_key():
    """Get Perplexity API key from environment variable"""
    api_key = os.getenv('PERPLEXITY_API_KEY')
    if not api_key:
        raise Exception("PERPLEXITY_API_KEY environment variable not set")
    return api_key

def get_selected_model():
    """Get the selected AI model from environment variable"""
    model = os.getenv('MODEL', 'GEMINI').upper()
    if model not in ['GEMINI', 'PERPLEXITY']:
        print(f"⚠️ Invalid MODEL value: {model}. Defaulting to GEMINI")
        model = 'GEMINI'
    return model
