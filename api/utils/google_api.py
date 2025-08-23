import requests
import json
import os
from api.config.env_loader import get_api_key

class GoogleGeminiAPI:
    """Google Gemini API implementation"""
    
    def __init__(self):
        self.api_key = get_api_key()
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model = "gemini-2.0-flash"
    
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
    
    def build_conversation_parts(self, conversation_history, current_query):
        """Build the parts array with conversation history and current query"""
        parts = []
        
        # Add conversation history
        for conv in conversation_history:
            # Add user question
            parts.append({
                "role": "user",
                "parts": [{"text": conv["userQuestion"]}]
            })
            
            # Add model answer
            parts.append({
                "role": "model", 
                "parts": [{"text": conv["modelAnswer"]}]
            })
        
        # Add current query
        parts.append({
            "role": "user",
            "parts": [{"text": current_query}]
        })
        
        return parts
    
    def generate_response_with_context(self, query, relevant_context):
        """Generate response using Google Gemini API with context and conversation history"""
        try:
            url = f'{self.base_url}/models/{self.model}:generateContent?key={self.api_key}'
            
            # Load conversation history
            conversation_history = self.load_conversation_history()
            
            # Build conversation parts
            conversation_parts = self.build_conversation_parts(conversation_history, query)
            
            # Construct system prompt with context
            context_text = "\n".join([f"- {ctx}" for ctx in relevant_context])
            
            # Get dynamic profile summary
            profile_data = self.load_profile_data()
            profile_summary = self._create_profile_summary(profile_data)
            
            system_prompt = f"""You are Mushini Gopala Swamy, working as Senior Software Engineer.

You are in the job search process and need to answer recruiters based on your profile.

IMPORTANT: ONLY provide information that is explicitly present in the profile data below. If you don't have specific information about something, respond with: "I don't have that information to provide." DO NOT make up or hallucinate any information.

PROFILE INFORMATION:
{profile_summary}

Context or Data:
{context_text}

Please provide a clear, professional answer as if you are Mushini Gopala Swamy responding to a recruiter. Use ONLY the context information above to give accurate and helpful answers about your experience, skills, and preferences. 

If the context doesn't contain enough information to answer the question, respond with: "I don't have that information to provide." in a formal, professional tone.

Remember to maintain consistency with your previous responses in the conversation history."""

            # Create the request payload with conversation history
            data = {
                "contents": conversation_parts,
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 1024,
                }
            }
            
            print(f"🤖 Sending request to Google Gemini with {len(conversation_parts)} conversation parts")
            print(f"📝 Current query: {query}")
            
            response = requests.post(url, json=data, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                print(f"Google Gemini API error: {response.status_code} - {response.text}")
                return f"Sorry, I encountered an error. Please try again. (Error: {response.status_code})"
                
        except Exception as e:
            print(f"Error generating response with Google Gemini: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    def get_embedding(self, text):
        """Get embedding from Google Gemini Embedding API"""
        try:
            url = f'{self.base_url}/models/gemini-embedding-001:embedContent?key={self.api_key}'
            
            data = {
                "model": "models/gemini-embedding-001",
                "content": {
                    "parts": [{"text": text}]
                }
            }
            
            response = requests.post(url, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                return result['embedding']['values']
            else:
                print(f"Google Embedding API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error getting Google embedding: {e}")
            return None

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
    
    def _create_profile_summary(self, profile_data):
        """Create a concise summary of profile data dynamically"""
        summary_parts = []
        
        # Process all fields dynamically
        for key, value in profile_data.items():
            if value and key not in ['_id', 'created_at', 'updated_at']:  # Skip metadata fields
                if isinstance(value, str) and len(value) < 100:
                    # Short string fields
                    summary_parts.append(f"{key.replace('_', ' ').title()}: {value}")
                elif isinstance(value, (int, float)):
                    # Numeric fields
                    if key == 'experience_years':
                        summary_parts.append(f"Experience: {value} years")
                    else:
                        summary_parts.append(f"{key.replace('_', ' ').title()}: {value}")
                elif isinstance(value, list) and len(value) > 0:
                    # Array fields - show first few items
                    if len(value) <= 3:
                        summary_parts.append(f"{key.replace('_', ' ').title()}: {', '.join(str(item) for item in value)}")
                    else:
                        summary_parts.append(f"{key.replace('_', ' ').title()}: {', '.join(str(item) for item in value[:3])}...")
                elif isinstance(value, dict) and value:
                    # Nested objects - show key fields
                    nested_summary = []
                    for nested_key, nested_value in value.items():
                        if nested_value and isinstance(nested_value, (str, int, float)):
                            nested_summary.append(f"{nested_key.replace('_', ' ').title()}: {nested_value}")
                        elif isinstance(nested_value, list) and nested_value:
                            nested_summary.append(f"{nested_key.replace('_', ' ').title()}: {', '.join(str(item) for item in nested_value[:2])}")
                    
                    if nested_summary:
                        summary_parts.append(f"{key.replace('_', ' ').title()}: {'; '.join(nested_summary)}")
        
        return "\n".join(summary_parts)
