import json
from api.utils.embedding_utils import EmbeddingManager
from api.utils.search_utils import SearchUtils
from api.utils.api_utils import GeminiAPI

class GopalService:
    def __init__(self):
        self.profile_data = self.load_profile_data()
        self.embedding_manager = EmbeddingManager()
        self.embedding_manager.load_or_create_embeddings(self.profile_data)
    
    def load_profile_data(self):
        """Load profile data from JSON file"""
        try:
            with open('data/myprofile.json', 'r', encoding='utf-8') as f:
                profile = json.load(f)
                # Convert profile data into searchable text chunks
                return self.convert_profile_to_chunks(profile)
        except Exception as e:
            print(f"Error loading profile data: {e}")
            return []
    
    def convert_profile_to_chunks(self, profile):
        """Convert profile JSON into searchable text chunks dynamically"""
        chunks = []
        
        # Process simple string/number fields
        simple_fields = ['name', 'dob', 'email', 'secondary_email', 'phone', 'secondary_phone', 
                        'portfolio', 'resume_link', 'linkedin', 'github', 'scaler', 'current_location', 
                        'gender', 'race_ethnicity', 'nationality', 'first_name', 'last_name', 
                        'experience_years', 'current_company', 'current_role', 'previous_company', 
                        'reason_for_change']
        
        basic_info_parts = []
        for field in simple_fields:
            if field in profile and profile[field]:
                if field == 'experience_years':
                    basic_info_parts.append(f"{field.replace('_', ' ').title()}: {profile[field]} years")
                else:
                    basic_info_parts.append(f"{field.replace('_', ' ').title()}: {profile[field]}")
        
        if basic_info_parts:
            chunks.append(", ".join(basic_info_parts))
        
        # Process nested objects dynamically
        for key, value in profile.items():
            print(f"🔍 Processing field: {key} (type: {type(value).__name__})")
            if key in simple_fields:
                print(f"   ⏭️ Skipping simple field: {key}")
                continue  # Skip already processed fields
                
            if isinstance(value, dict):
                # Handle nested objects like education, job_preferences, best_work
                if value:  # Only process non-empty dicts
                    nested_text = f"{key.replace('_', ' ').title()}: "
                    nested_parts = []
                    
                    for nested_key, nested_value in value.items():
                        if nested_value:
                            if isinstance(nested_value, list):
                                nested_parts.append(f"{nested_key.replace('_', ' ').title()}: {', '.join(str(item) for item in nested_value)}")
                            else:
                                nested_parts.append(f"{nested_key.replace('_', ' ').title()}: {nested_value}")
                    
                    if nested_parts:
                        nested_text += ". ".join(nested_parts)
                        chunks.append(nested_text)
                        
            elif isinstance(value, list):
                # Handle arrays like work_experience, achievements, personal_projects, specializations
                if value:
                    print(f"🔍 Processing array field: {key} with {len(value)} items")
                    if key == 'work_experience':
                        # Special handling for work experience
                        for exp in value:
                            exp_text = f"Company: {exp.get('company', '')}, Role: {exp.get('role', '')}, Duration: {exp.get('duration', '')}, Location: {exp.get('location', '')}. Responsibilities: {' '.join(exp.get('responsibilities', []))}"
                            chunks.append(exp_text)
                    elif key == 'personal_projects':
                        # Special handling for personal projects
                        for project in value:
                            project_text = f"Project: {project.get('name', '')}, Description: {project.get('description', '')}"
                            if project.get('skills'):
                                project_text += f", Skills: {', '.join(project.get('skills', []))}"
                            if project.get('link'):
                                project_text += f", Link: {project.get('link', '')}"
                            chunks.append(project_text)
                    elif key == 'specializations':
                        # Handle specializations as a single chunk
                        spec_text = f"Specializations: {' '.join(value)}"
                        chunks.append(spec_text)
                    elif key == 'achievements':
                        # Handle achievements as a single chunk
                        achievements_text = f"Achievements: {' '.join(value)}"
                        chunks.append(achievements_text)
                    else:
                        # Generic handling for other arrays
                        array_text = f"{key.replace('_', ' ').title()}: {', '.join(str(item) for item in value)}"
                        print(f"   📝 Created generic array chunk: {array_text[:50]}...")
                        chunks.append(array_text)
            elif isinstance(value, (str, int, float)):
                print(f"   ⚠️ Unhandled field type: {key} = {value}")
        
        return chunks
    
    def handle_query(self, query):
        """Main function to handle user queries"""
        try:
            print(f"🔍 Processing query: {query}")
            
            # Find relevant context using embeddings
            embeddings_cache = self.embedding_manager.get_embeddings_cache()
            print(f"📊 Embeddings cache size: {len(embeddings_cache)}")
            
            # Try embedding search first
            try:
                relevant_context = SearchUtils.find_relevant_context(
                    query, 
                    embeddings_cache, 
                    self.embedding_manager.get_cached_embedding,
                    top_k=3
                )
                print(f"🔍 Embedding search result: {len(relevant_context) if relevant_context else 0} contexts")
            except Exception as e:
                print(f"⚠️ Embedding search failed: {e}")
                relevant_context = None
            
            # Fallback to simple search if embedding search fails
            if relevant_context is None or len(relevant_context) == 0:
                print("🔄 Falling back to simple keyword search...")
                relevant_context = SearchUtils.find_relevant_context_simple(
                    query, 
                    self.profile_data, 
                    top_k=3
                )
                print(f"🔍 Simple search found: {len(relevant_context) if relevant_context else 0} contexts")
            
            if not relevant_context:
                print("❌ No relevant context found in either search method")
                return "I don't have enough information to answer that question. Please try asking something else."
            
            print(f"📚 Found {len(relevant_context)} relevant contexts")
            
            # Generate response using Gemini API
            response = GeminiAPI.generate_response_with_context(query, relevant_context)
            return response
            
        except Exception as e:
            print(f"Error handling query: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
