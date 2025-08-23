import hashlib
import pickle
import os
import time
import json
from api.utils.google_api import GoogleGeminiAPI

class EmbeddingManager:
    def __init__(self, embeddings_file='cache/profile_embeddings.pkl'):
        self.embeddings_file = embeddings_file
        self.embeddings_cache = {}
        self.user_query_cache = {}
        self.google_api = GoogleGeminiAPI()
        self.profile_metadata_file = 'cache/profile_metadata.json'
    
    def _get_profile_hash(self, profile_data):
        """Generate a hash of the profile data to detect changes"""
        profile_str = json.dumps(profile_data, sort_keys=True)
        return hashlib.md5(profile_str.encode()).hexdigest()
    
    def _load_profile_metadata(self):
        """Load profile metadata to track changes"""
        try:
            if os.path.exists(self.profile_metadata_file):
                with open(self.profile_metadata_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading profile metadata: {e}")
        return {}
    
    def _save_profile_metadata(self, metadata):
        """Save profile metadata"""
        try:
            os.makedirs(os.path.dirname(self.profile_metadata_file), exist_ok=True)
            with open(self.profile_metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            print(f"Error saving profile metadata: {e}")
    
    def _detect_new_fields(self, profile_data):
        """Detect newly added fields in the profile"""
        current_hash = self._get_profile_hash(profile_data)
        metadata = self._load_profile_metadata()
        
        if 'last_hash' not in metadata or metadata['last_hash'] != current_hash:
            # Profile has changed, detect new fields
            old_fields = set(metadata.get('known_fields', []))
            current_fields = self._extract_all_field_names(profile_data)
            new_fields = current_fields - old_fields
            
            if new_fields:
                print(f"🆕 Detected {len(new_fields)} new fields: {list(new_fields)}")
            
            # Update metadata
            metadata['last_hash'] = current_hash
            metadata['known_fields'] = list(current_fields)
            metadata['last_updated'] = time.strftime('%Y-%m-%d %H:%M:%S')
            self._save_profile_metadata(metadata)
            
            return new_fields
        
        return set()
    
    def _extract_all_field_names(self, profile_data):
        """Extract all field names from profile data recursively"""
        field_names = set()
        
        def extract_fields_recursive(data, prefix=""):
            if isinstance(data, dict):
                for key, value in data.items():
                    current_key = f"{prefix}.{key}" if prefix else key
                    field_names.add(current_key)
                    if isinstance(value, dict):
                        extract_fields_recursive(value, current_key)
                    elif isinstance(value, list) and value and isinstance(value[0], dict):
                        # Handle array of objects
                        for item in value:
                            extract_fields_recursive(item, current_key)
        
        extract_fields_recursive(profile_data)
        return field_names
    
    def _create_semantic_chunks_for_new_fields(self, profile_data, new_fields):
        """Create semantic chunks for newly added fields"""
        new_chunks = []
        
        for field_path in new_fields:
            field_value = self._get_field_value(profile_data, field_path)
            if field_value:
                # Create semantic chunk for the new field
                chunk = self._create_semantic_chunk(field_path, field_value)
                if chunk:
                    new_chunks.append(chunk)
                    print(f"   📝 Created semantic chunk for: {field_path}")
        
        return new_chunks
    
    def _get_field_value(self, profile_data, field_path):
        """Get field value from nested profile data"""
        keys = field_path.split('.')
        current = profile_data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            elif isinstance(current, list) and key.isdigit():
                current = current[int(key)]
            else:
                return None
        
        return current
    
    def _create_semantic_chunk(self, field_path, field_value):
        """Create a semantic chunk for a field"""
        field_name = field_path.split('.')[-1]
        
        if isinstance(field_value, str):
            return f"{field_name.replace('_', ' ').title()}: {field_value}"
        elif isinstance(field_value, (int, float)):
            return f"{field_name.replace('_', ' ').title()}: {field_value}"
        elif isinstance(field_value, list):
            if all(isinstance(item, str) for item in field_value):
                return f"{field_name.replace('_', ' ').title()}: {', '.join(field_value)}"
            elif all(isinstance(item, dict) for item in field_value):
                # Handle array of objects
                chunks = []
                for item in field_value:
                    item_chunk = f"{field_name.replace('_', ' ').title()}: "
                    item_parts = []
                    for k, v in item.items():
                        if isinstance(v, str) and len(v) < 100:
                            item_parts.append(f"{k.replace('_', ' ').title()}: {v}")
                    if item_parts:
                        item_chunk += ". ".join(item_parts)
                        chunks.append(item_chunk)
                return chunks
        elif isinstance(field_value, dict):
            # Handle nested objects
            chunk_parts = [f"{field_name.replace('_', ' ').title()}:"]
            for k, v in field_value.items():
                if isinstance(v, (str, int, float)) and len(str(v)) < 100:
                    chunk_parts.append(f"{k.replace('_', ' ').title()}: {v}")
            return " ".join(chunk_parts)
        
        return None
    
    def load_or_create_embeddings(self, profile_data):
        """Load existing embeddings or create new ones with new field detection"""
        try:
            # Detect new fields first
            new_fields = self._detect_new_fields(profile_data)
            
            if os.path.exists(self.embeddings_file) and not new_fields:
                print("🔄 Loading existing profile embeddings...")
                with open(self.embeddings_file, 'rb') as f:
                    self.embeddings_cache = pickle.load(f)
                print(f"✅ Loaded {len(self.embeddings_cache)} profile embeddings from cache")
            else:
                if new_fields:
                    print(f"🆕 New fields detected, updating embeddings...")
                    # Load existing embeddings if available
                    if os.path.exists(self.embeddings_file):
                        with open(self.embeddings_file, 'rb') as f:
                            self.embeddings_cache = pickle.load(f)
                        print(f"📚 Loaded {len(self.embeddings_cache)} existing embeddings")
                    
                    # Create embeddings for new fields only
                    self._update_embeddings_for_new_fields(profile_data, new_fields)
                else:
                    print("🆕 Creating new embeddings for profile data...")
                    self.create_all_embeddings(profile_data)
                
                self.save_embeddings()
                
        except Exception as e:
            print(f"Error in load_or_create_embeddings: {e}")
            # Fallback: create embeddings if loading fails
            self.create_all_embeddings(profile_data)
            self.save_embeddings()
    
    def _update_embeddings_for_new_fields(self, profile_data, new_fields):
        """Update embeddings only for newly added fields"""
        print(f"🔄 Updating embeddings for {len(new_fields)} new fields...")
        
        # Create semantic chunks for new fields
        new_chunks = self._create_semantic_chunks_for_new_fields(profile_data, new_fields)
        
        # Flatten chunks if needed
        flat_chunks = []
        for chunk in new_chunks:
            if isinstance(chunk, list):
                flat_chunks.extend(chunk)
            else:
                flat_chunks.append(chunk)
        
        # Create embeddings for new chunks
        for i, chunk in enumerate(flat_chunks):
            try:
                chunk_embedding = self.get_embedding(chunk)
                if chunk_embedding is not None:
                    self.embeddings_cache[chunk] = {
                        'embedding': chunk_embedding,
                        'content': chunk,
                        'source_field': 'new_field'
                    }
                    print(f"   📈 Created embedding for new chunk {i+1}/{len(flat_chunks)}")
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error processing new chunk {i}: {e}")
                continue
        
        print(f"🎉 Successfully updated embeddings for {len(flat_chunks)} new chunks!")
    
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
                        'content': chunk,
                        'source_field': 'existing_field'
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
    
    def get_cache_stats(self):
        """Get statistics about the embeddings cache"""
        total_embeddings = len(self.embeddings_cache)
        new_field_embeddings = sum(1 for data in self.embeddings_cache.values() 
                                 if data.get('source_field') == 'new_field')
        existing_field_embeddings = sum(1 for data in self.embeddings_cache.values() 
                                      if data.get('source_field') == 'existing_field')
        
        return {
            'total': total_embeddings,
            'new_fields': new_field_embeddings,
            'existing_fields': existing_field_embeddings
        }
