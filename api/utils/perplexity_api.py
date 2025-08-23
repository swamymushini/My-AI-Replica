import requests
import json
import os
from api.config.env_loader import get_perplexity_api_key

class PerplexityAPI:
    """Perplexity API implementation"""
    
    def __init__(self):
        self.api_key = get_perplexity_api_key()
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.model = "sonar-pro"  # You can change this to other models like "llama-3.1-sonar-small-128k"
    
    def load_conversation_history(self):
        """Load conversation history from JSON file"""
        try:
            conversation_file = 'data/conversation_data.json'
            if os.path.exists(conversation_file):
                with open(conversation_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"Conversation file not found at: {conversation_file}")
                return []
        except Exception as e:
            print(f"Error loading conversation history: {e}")
            return []
    
    def load_profile_data(self):
        """Load profile data from JSON file"""
        try:
            profile_file = 'data/myprofile.json'
            if os.path.exists(profile_file):
                with open(profile_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"Profile file not found at: {profile_file}")
                return {}
        except Exception as e:
            print(f"Error loading profile data: {e}")
            return {}
    
    def build_messages(self, query, relevant_context, conversation_history):
        """Build messages array for Perplexity API"""
        messages = []
        
        # System message with profile context
        profile_data = self.load_profile_data()
        profile_summary = self._create_profile_summary(profile_data)
        
        system_message = f"""You are Mushini Gopala Swamy, working as Senior Software Engineer.

You are in the job search process and need to answer recruiters based on your profile.

PROFILE INFORMATION:
{profile_summary}

RELEVANT CONTEXT FOR THIS QUESTION:
{chr(10).join([f"- {ctx}" for ctx in relevant_context])}

Please provide a clear, professional answer as if you are Mushini Gopala Swamy responding to a recruiter. Use the profile information and context above to give accurate and helpful answers about your experience, skills, and preferences. If the context doesn't contain enough information to answer the question, say so politely and ask for clarification.

Remember to maintain consistency with your previous responses in the conversation history."""
        
        messages.append({"role": "system", "content": system_message})
        
        # Add conversation history
        for conv in conversation_history:
            messages.append({"role": "user", "content": conv["userQuestion"]})
            messages.append({"role": "assistant", "content": conv["modelAnswer"]})
        
        # Add current query
        messages.append({"role": "user", "content": query})
        
        return messages
    
    def _create_profile_summary(self, profile_data):
        """Create a concise summary of profile data"""
        summary_parts = []
        
        # Basic info
        if profile_data.get('name'):
            summary_parts.append(f"Name: {profile_data['name']}")
        if profile_data.get('current_role'):
            summary_parts.append(f"Current Role: {profile_data['current_role']}")
        if profile_data.get('current_company'):
            summary_parts.append(f"Company: {profile_data['current_company']}")
        if profile_data.get('experience_years'):
            summary_parts.append(f"Experience: {profile_data['experience_years']} years")
        if profile_data.get('current_location'):
            summary_parts.append(f"Location: {profile_data['current_location']}")
        
        # Skills summary
        if profile_data.get('skills'):
            skills = profile_data['skills']
            skill_summary = []
            for category, skill_list in skills.items():
                if isinstance(skill_list, list):
                    skill_summary.append(f"{category}: {', '.join(skill_list[:3])}")
            if skill_summary:
                summary_parts.append(f"Key Skills: {'; '.join(skill_summary)}")
        
        # Job preferences
        if profile_data.get('job_preferences'):
            prefs = profile_data['job_preferences']
            if prefs.get('current_ctc'):
                summary_parts.append(f"Current CTC: {prefs['current_ctc']}")
            if prefs.get('expected_ctc'):
                summary_parts.append(f"Expected CTC: {prefs['expected_ctc']}")
            if prefs.get('negotiable_notice_period'):
                summary_parts.append(f"Notice Period: {prefs['negotiable_notice_period']} days")
        
        return "\n".join(summary_parts)
    
    def generate_response_with_context(self, query, relevant_context):
        """Generate response using Perplexity API with context and conversation history"""
        try:
            # Load conversation history
            conversation_history = self.load_conversation_history()
            
            # Build messages for Perplexity
            messages = self.build_messages(query, relevant_context, conversation_history)
            
            # Create the request payload
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": 1024,
                "temperature": 0.7,
                "top_p": 0.95,
                "citations": False
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            print(f"🤖 Sending request to Perplexity with {len(messages)} messages")
            print(f"📝 Current query: {query}")
            
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]['message']['content']
            else:
                print(f"Perplexity API error: {response.status_code} - {response.text}")
                return f"Sorry, I encountered an error. Please try again. (Error: {response.status_code})"
                
        except Exception as e:
            print(f"Error generating response with Perplexity: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
