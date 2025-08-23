import requests
import json
import os
from api.config.env_loader import get_api_key
from api.utils.google_api import GoogleGeminiAPI
from api.utils.perplexity_api import PerplexityAPI
from api.config.env_loader import get_selected_model

class GeminiAPI:
    """Generic AI API interface - supports both Google Gemini and Perplexity"""
    
    def __init__(self):
        self.model = get_selected_model()
        if self.model == 'GEMINI':
            self.ai_provider = GoogleGeminiAPI()
        else:
            self.ai_provider = PerplexityAPI()
        
        print(f"🤖 Using AI Model: {self.model}")
    
    @staticmethod
    def generate_response_with_context(query, relevant_context):
        """Generate response using the configured AI provider"""
        model = get_selected_model()
        
        if model == 'GEMINI':
            ai_provider = GoogleGeminiAPI()
        else:
            ai_provider = PerplexityAPI()
        
        return ai_provider.generate_response_with_context(query, relevant_context)
