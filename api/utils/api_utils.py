import requests
import json
import os
from api.config.env_loader import get_api_key

class GeminiAPI:
    @staticmethod
    def load_conversation_history():
        """Load conversation history from JSON file"""
        try:
            # Try to load from the data directory relative to the project root
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
    
    @staticmethod
    def build_conversation_parts(conversation_history, current_query):
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
    
    @staticmethod
    def generate_response_with_context(query, relevant_context):
        """Generate response using Gemini API with context and conversation history"""
        try:
            api_key = get_api_key()
            url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}'
            
            # Load conversation history
            conversation_history = GeminiAPI.load_conversation_history()
            
            # Build conversation parts
            conversation_parts = GeminiAPI.build_conversation_parts(conversation_history, query)
            
            # Construct system prompt with context
            context_text = "\n".join([f"- {ctx}" for ctx in relevant_context])
            system_prompt = f"""You are Mushini Gopala Swamy, working as Senior Software Engineer.

You are in the job search process and need to answer recruiters based on your profile.

Context or Data:
{context_text}

Please provide a clear, professional answer as if you are Mushini Gopala Swamy responding to a recruiter. Use the context information above to give accurate and helpful answers about your experience, skills, and preferences. If the context doesn't contain enough information to answer the question, say so politely and ask for clarification.

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
            
            print(f"🤖 Sending request to Gemini with {len(conversation_parts)} conversation parts")
            print(f"📝 Current query: {query}")
            
            response = requests.post(url, json=data, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                print(f"Gemini API error: {response.status_code} - {response.text}")
                return f"Sorry, I encountered an error. Please try again. (Error: {response.status_code})"
                
        except Exception as e:
            print(f"Error generating response: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
