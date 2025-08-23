import requests
from config.env_loader import get_api_key

class GeminiAPI:
    @staticmethod
    def generate_response_with_context(query, relevant_context):
        """Generate response using Gemini API with context"""
        try:
            api_key = get_api_key()
            url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}'
            
            # Construct system prompt with context
            context_text = "\n".join([f"- {ctx}" for ctx in relevant_context])
            system_prompt = f"""You are an AI assistant that helps answer questions about Mushini Gopala Swamy. 
Use the following context information to provide accurate and helpful answers:

{context_text}

User Question: {query}

Please provide a clear, concise answer based on the context above. If the context doesn't contain enough information to answer the question, say so politely."""

            data = {
                "contents": [{
                    "parts": [{"text": system_prompt}]
                }]
            }
            
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
