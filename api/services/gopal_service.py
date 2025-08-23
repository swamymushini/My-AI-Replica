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
        """Convert profile JSON into searchable text chunks"""
        chunks = []
        
        # Basic info chunk
        basic_info = f"Name: {profile.get('name', '')}, Current Role: {profile.get('current_role', '')} at {profile.get('current_company', '')}, Experience: {profile.get('experience_years', '')} years, Location: {profile.get('current_location', '')}, Email: {profile.get('email', '')}, Phone: {profile.get('phone', '')}"
        chunks.append(basic_info)
        
        # Skills chunk
        skills = profile.get('skills', {})
        skills_text = "Skills: "
        for category, skill_list in skills.items():
            if isinstance(skill_list, list):
                skills_text += f"{category}: {', '.join(skill_list)}. "
        chunks.append(skills_text)
        
        # Work experience chunks
        work_exp = profile.get('work_experience', [])
        for exp in work_exp:
            exp_text = f"Company: {exp.get('company', '')}, Role: {exp.get('role', '')}, Duration: {exp.get('duration', '')}, Location: {exp.get('location', '')}. Responsibilities: {' '.join(exp.get('responsibilities', []))}"
            chunks.append(exp_text)
        
        # Education chunk
        education = profile.get('education', {})
        if education:
            edu_text = f"Education: {education.get('degree', '')} from {education.get('university', '')}, Duration: {education.get('duration', '')}"
            chunks.append(edu_text)
        
        # Job preferences chunk
        job_prefs = profile.get('job_preferences', {})
        if job_prefs:
            prefs_text = f"Current CTC: {job_prefs.get('current_ctc', '')}, Expected CTC: {job_prefs.get('expected_ctc', '')}, Notice Period: {job_prefs.get('negotiable_notice_period', '')} days, Open to relocation: {job_prefs.get('open_to_relocation', '')}, Preferred locations: {', '.join(job_prefs.get('preferred_locations', []))}"
            chunks.append(prefs_text)
        
        # Achievements chunk
        achievements = profile.get('achievements', [])
        if achievements:
            achievements_text = f"Achievements: {' '.join(achievements)}"
            chunks.append(achievements_text)
        
        # Personal projects chunk
        projects = profile.get('personal_projects', [])
        for project in projects:
            project_text = f"Project: {project.get('name', '')}, Description: {project.get('description', '')}, Skills: {', '.join(project.get('skills', []))}"
            chunks.append(project_text)
        
        # Reason for change
        reason = profile.get('reason_for_change', '')
        if reason:
            chunks.append(f"Reason for change: {reason}")
        
        return chunks
    
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
                    self.profile_data, 
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
