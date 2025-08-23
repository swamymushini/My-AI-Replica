from api.config.env_loader import load_env_file
from api.handlers.api_handler import APIHandler

# Load environment variables
load_env_file()

# Global instance for Vercel
handler = APIHandler
