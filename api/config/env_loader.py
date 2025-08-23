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
    """Get API key from environment variable"""
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise Exception("GOOGLE_API_KEY environment variable not set")
    return api_key
