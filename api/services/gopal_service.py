import json
from utils.embedding_utils import EmbeddingManager
from utils.search_utils import SearchUtils
from utils.api_utils import GeminiAPI

class GopalService:
    def __init__(self):
        self.conversation_data = self.load_conversation_data()
        self.embedding_manager = EmbeddingManager()
        self.embedding_manager.load_or_create_embeddings(self.conversation_data)
    
    def load_conversation_data(self):
        """Load conversation data from JSON file"""
        try:
            with open('data/conversation_data.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading conversation data: {e}")
            return []
    
    def handle_query(self, query):
        """Main function to handle user queries"""
        try:
            print(f"🔍 Processing query: {query}")
            
            # Find relevant context using embeddings
            embeddings_cache = self.embedding_manager.get_embeddings_cache()
            relevant_context = SearchUtils.find_relevant_context(
                query, 
                embeddings_cache, 
                self.embedding_manager.get_cached_embedding,
                top_k=3
            )
            
            # Fallback to simple search if embedding search fails
            if relevant_context is None:
                relevant_context = SearchUtils.find_relevant_context_simple(
                    query, 
                    self.conversation_data, 
                    top_k=3
                )
            
            if not relevant_context:
                return "I don't have enough information to answer that question. Please try asking something else."
            
            print(f"📚 Found {len(relevant_context)} relevant contexts")
            
            # Generate response using Gemini API
            response = GeminiAPI.generate_response_with_context(query, relevant_context)
            return response
            
        except Exception as e:
            print(f"Error handling query: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
