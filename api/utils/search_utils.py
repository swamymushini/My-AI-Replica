import numpy as np
import json
import os

class SearchUtils:
    @staticmethod
    def cosine_similarity(vec1, vec2):
        """Calculate cosine similarity between two vectors"""
        try:
            vec1 = np.array(vec1)
            vec2 = np.array(vec2)
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            return dot_product / (norm1 * norm2)
        except Exception as e:
            print(f"Error calculating cosine similarity: {e}")
            return 0.0
    
    @staticmethod
    def find_relevant_context(query, embeddings_cache, get_cached_embedding_func, top_k=5):
        """Find most relevant context using embeddings"""
        try:
            query_embedding = get_cached_embedding_func(query)
            if query_embedding is None:
                print("⚠️ Falling back to simple keyword search")
                return None  # Signal to use fallback search
            
            similarities = []
            for text, data in embeddings_cache.items():
                similarity = SearchUtils.cosine_similarity(query_embedding, data['embedding'])
                similarities.append((similarity, data['content']))
            
            # Sort by similarity and get top k
            similarities.sort(key=lambda x: x[0], reverse=True)
            return [content for _, content in similarities[:top_k]]
            
        except Exception as e:
            print(f"Error in find_relevant_context: {e}")
            return None  # Signal to use fallback search
    
    @staticmethod
    def _extract_all_fields_from_profile(profile_data):
        """Extract all available fields from profile data dynamically"""
        all_fields = {}
        
        def extract_fields_recursive(data, prefix=""):
            if isinstance(data, dict):
                for key, value in data.items():
                    current_key = f"{prefix}.{key}" if prefix else key
                    if isinstance(value, (str, int, float, bool)):
                        # Simple field
                        all_fields[current_key] = {
                            'type': 'simple',
                            'value': str(value),
                            'keywords': [key, str(value).lower()]
                        }
                    elif isinstance(value, list):
                        # Array field
                        all_fields[current_key] = {
                            'type': 'array',
                            'value': value,
                            'keywords': [key] + [str(item).lower() for item in value if item]
                        }
                    elif isinstance(value, dict):
                        # Nested object
                        all_fields[current_key] = {
                            'type': 'nested',
                            'value': value,
                            'keywords': [key]
                        }
                        extract_fields_recursive(value, current_key)
        
        extract_fields_recursive(profile_data)
        return all_fields
    
    @staticmethod
    def _generate_semantic_keywords_for_field(field_name, field_value, field_type):
        """Generate semantic keywords for a field using AI or rule-based approach"""
        semantic_keywords = []
        
        # Base keywords from field name
        field_words = field_name.replace('_', ' ').lower().split()
        semantic_keywords.extend(field_words)
        
        # Add common synonyms based on field type and content
        if field_type == 'array':
            semantic_keywords.extend(['list', 'items', 'collection'])
        elif field_type == 'nested':
            semantic_keywords.extend(['details', 'information', 'data'])
        
        # Add common question words
        question_words = ['what', 'tell me about', 'describe', 'explain', 'show']
        semantic_keywords.extend(question_words)
        
        # Add field-specific semantic mappings
        semantic_mappings = {
            'hobbies': ['interests', 'passions', 'likes', 'enjoy', 'fun', 'leisure', 'activities'],
            'skills': ['expertise', 'capabilities', 'proficiencies', 'technologies', 'tools'],
            'experience': ['work history', 'career', 'background', 'years', 'duration'],
            'languages': ['speak', 'fluent', 'communication', 'tongue', 'dialect'],
            'certifications': ['certified', 'accreditation', 'qualification', 'badge', 'credential'],
            'projects': ['work', 'developed', 'built', 'created', 'implemented'],
            'achievements': ['awards', 'recognition', 'accomplishments', 'successes', 'milestones'],
            'company': ['employer', 'organization', 'firm', 'workplace', 'corporation'],
            'role': ['position', 'job title', 'responsibility', 'function', 'designation'],
            'location': ['place', 'city', 'country', 'area', 'region'],
            'ctc': ['salary', 'compensation', 'package', 'pay', 'remuneration'],
            'notice': ['period', 'joining', 'start date', 'availability', 'timeline']
        }
        
        # Find matching semantic mappings
        for key, synonyms in semantic_mappings.items():
            if key in field_name.lower() or any(word in field_name.lower() for word in key.split()):
                semantic_keywords.extend(synonyms)
                break
        
        # Add content-based keywords
        if isinstance(field_value, list):
            for item in field_value:
                if isinstance(item, str):
                    item_words = item.lower().split()
                    semantic_keywords.extend(item_words)
        
        # TODO: Future Enhancement - Use AI (Gemma) to generate better synonyms
        # This would make the system even more intelligent
        # semantic_keywords.extend(SearchUtils._generate_ai_synonyms(field_name, field_value))
        
        # Remove duplicates and return
        return list(set(semantic_keywords))
    
    @staticmethod
    def _generate_ai_synonyms(field_name, field_value):
        """Future enhancement: Use AI to generate semantic synonyms"""
        # This would call Gemma or another AI model to generate better synonyms
        # For now, return empty list - you can implement this later
        return []
    
    @staticmethod
    def _build_dynamic_mappings(profile_data):
        """Build keyword mappings dynamically from profile data using AI-generated semantics"""
        print("🔍 Building dynamic semantic mappings from profile data...")
        
        # Extract all fields from profile
        all_fields = SearchUtils._extract_all_fields_from_profile(profile_data)
        
        # Build semantic mappings for each field
        semantic_mappings = {}
        
        for field_name, field_info in all_fields.items():
            field_type = field_info['type']
            field_value = field_info['value']
            
            # Generate semantic keywords for this field
            semantic_keywords = SearchUtils._generate_semantic_keywords_for_field(
                field_name, field_value, field_type
            )
            
            # Create category name from field
            category_name = field_name.replace('_', ' ').lower()
            
            # Add to semantic mappings
            if category_name not in semantic_mappings:
                semantic_mappings[category_name] = []
            
            semantic_mappings[category_name].extend(semantic_keywords)
        
        # Remove duplicates from each category
        for category in semantic_mappings:
            semantic_mappings[category] = list(set(semantic_mappings[category]))
        
        print(f"🎯 Generated {len(semantic_mappings)} semantic categories with AI-enhanced keywords")
        
        return semantic_mappings
    
    @staticmethod
    def find_relevant_context_simple(query, profile_data, top_k=5):
        """Simple keyword-based fallback search for profile data"""
        query_lower = query.lower()
        relevant = []
        
        print(f"🔍 Simple search for: '{query}'")
        print(f"📊 Profile data has {len(profile_data)} chunks")
        
        # Dynamic keyword mappings based on profile content
        dynamic_mappings = SearchUtils._build_dynamic_mappings(profile_data)
        
        # Find the best matching category
        best_category = None
        best_score = 0
        
        for category, keywords in dynamic_mappings.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > best_score:
                best_score = score
                best_category = category
        
        print(f"🎯 Best category: {best_category} (score: {best_score})")
        
        # If no specific category found, use general word matching
        if best_score == 0:
            print("🔄 Using general word matching...")
            for chunk in profile_data:
                chunk_lower = chunk.lower()
                query_words = query_lower.split()
                score = sum(1 for word in query_words if word in chunk_lower)
                if score > 0:
                    relevant.append((score, chunk))
                    print(f"   ✅ Found match (score: {score}): {chunk[:50]}...")
        else:
            # Use category-specific matching
            print(f"🎯 Using category-specific matching for '{best_category}'...")
            for chunk in profile_data:
                chunk_lower = chunk.lower()
                category_keywords = dynamic_mappings.get(best_category, [])
                score = sum(1 for keyword in category_keywords if keyword in chunk_lower)
                if score > 0:
                    relevant.append((score, chunk))
                    print(f"   ✅ Found match (score: {score}): {chunk[:50]}...")
        
        print(f"📚 Total relevant chunks found: {len(relevant)}")
        
        # Sort by score and get top k
        relevant.sort(key=lambda x: x[0], reverse=True)
        return [chunk for _, chunk in relevant[:top_k]]
