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

IMPORTANT: Base your responses primarily on the profile information provided below. If specific details aren't available, you can provide general professional responses or politely indicate that you don't have specific information about certain topics. Be helpful and conversational while staying truthful to your profile.

PROFILE INFORMATION:
{profile_summary}

RELEVANT CONTEXT FOR THIS QUESTION:
{chr(10).join([f"- {ctx}" for ctx in relevant_context])}

Please provide a clear, professional answer as if you are Mushini Gopala Swamy responding to a recruiter. Use the profile information and context above to give accurate and helpful answers about your experience, skills, and preferences.

If the context doesn't contain specific information about something, you can:
- Provide general professional insights related to the topic
- Politely mention that you don't have specific details about that particular aspect
- Redirect the conversation to areas where you do have relevant information

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
                "citations": False,
                "include_citations": False,
                "search_recency_filter": "month",
                "disable_search": True
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
                response_text = result["choices"][0]['message']['content']
                
                # Remove citation markers like [1], [2], [3], etc.
                import re
                cleaned_response = re.sub(r'\[\d+\]', '', response_text)
                # Also remove any extra spaces that might be left
                cleaned_response = re.sub(r'\s+', ' ', cleaned_response).strip()
                
                return cleaned_response
            else:
                print(f"Perplexity API error: {response.status_code} - {response.text}")
                return f"Sorry, I encountered an error. Please try again. (Error: {response.status_code})"
                
        except Exception as e:
            print(f"Error generating response with Perplexity: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
