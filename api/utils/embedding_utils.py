import hashlib
import pickle
import os
import time
from api.utils.google_api import GoogleGeminiAPI

class EmbeddingManager:
    def __init__(self, embeddings_file='cache/profile_embeddings.pkl'):
        self.embeddings_file = embeddings_file
        self.embeddings_cache = {}
        self.user_query_cache = {}
        self.google_api = GoogleGeminiAPI()
    
    def load_or_create_embeddings(self, profile_data):
        """Load existing embeddings or create new ones"""
        try:
            if os.path.exists(self.embeddings_file):
                print("🔄 Loading existing profile embeddings...")
                with open(self.embeddings_file, 'rb') as f:
                    self.embeddings_cache = pickle.load(f)
                print(f"✅ Loaded {len(self.embeddings_cache)} profile embeddings from cache")
            else:
                print("🆕 Creating new embeddings for profile data...")
                self.create_all_embeddings(profile_data)
                self.save_embeddings()
        except Exception as e:
            print(f"Error in load_or_create_embeddings: {e}")
            # Fallback: create embeddings if loading fails
            self.create_all_embeddings(profile_data)
            self.save_embeddings()
    
    def create_all_embeddings(self, profile_data):
        """Create embeddings for all profile data chunks"""
        total_chunks = len(profile_data)
        print(f"📊 Processing {total_chunks} profile chunks...")
        
        for i, chunk in enumerate(profile_data):
            try:
                # Create embedding for each profile chunk
                chunk_embedding = self.get_embedding(chunk)
                if chunk_embedding is not None:
                    self.embeddings_cache[chunk] = {
                        'embedding': chunk_embedding,
                        'content': chunk
                    }
                
                if (i + 1) % 5 == 0:
                    print(f"📈 Processed {i + 1}/{total_chunks} profile chunks...")
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error processing profile chunk {i}: {e}")
                continue
        
        print(f"🎉 Successfully created embeddings for {len(self.embeddings_cache)} profile chunks!")
    
    def save_embeddings(self):
        """Save embeddings to pickle file"""
        try:
            # Ensure cache directory exists
            os.makedirs(os.path.dirname(self.embeddings_file), exist_ok=True)
            with open(self.embeddings_file, 'wb') as f:
                pickle.dump(self.embeddings_cache, f)
            print(f"💾 Saved profile embeddings to {self.embeddings_file}")
        except Exception as e:
            print(f"Error saving embeddings: {e}")
    
    def get_embedding(self, text):
        """Get embedding using the configured AI provider"""
        return self.google_api.get_embedding(text)
    
    def get_cached_embedding(self, text):
        """Get cached embedding or create new one"""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        if text_hash in self.user_query_cache:
            return self.user_query_cache[text_hash]
        
        embedding = self.get_embedding(text)
        if embedding is not None:
            self.user_query_cache[text_hash] = embedding
        return embedding
    
    def get_embeddings_cache(self):
        """Get the embeddings cache"""
        return self.embeddings_cache
