import json
import base64
import requests
import numpy as np
import time
import os
import hashlib
import pickle
import urllib.parse

class GopalService:
    def __init__(self):
        self.conversation_data = self.load_conversation_data()
        self.embeddings_cache = {}
        self.user_query_cache = {}
        self.embeddings_file = 'conversation_embeddings.pkl'
        self.load_or_create_embeddings()
    
    def load_conversation_data(self):
        """Load conversation data from JSON file"""
        try:
            with open('conversation_data.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading conversation data: {e}")
            return []
    
    def load_or_create_embeddings(self):
        """Load existing embeddings or create new ones"""
        try:
            if os.path.exists(self.embeddings_file):
                print("🔄 Loading existing embeddings...")
                with open(self.embeddings_file, 'rb') as f:
                    self.embeddings_cache = pickle.load(f)
                print(f"✅ Loaded {len(self.embeddings_cache)} embeddings from cache")
            else:
                print("🆕 Creating new embeddings for all conversations...")
                self.create_all_embeddings()
                self.save_embeddings()
        except Exception as e:
            print(f"Error in load_or_create_embeddings: {e}")
            # Fallback: create embeddings if loading fails
            self.create_all_embeddings()
            self.save_embeddings()
    
    def create_all_embeddings(self):
        """Create embeddings for all conversations"""
        total_conversations = len(self.conversation_data)
        print(f"📊 Processing {total_conversations} conversations...")
        
        for i, conv in enumerate(self.conversation_data):
            try:
                # Create embedding for user question
                question_embedding = self.get_embedding(conv['userQuestion'])
                if question_embedding is not None:
                    self.embeddings_cache[conv['userQuestion']] = {
                        'embedding': question_embedding,
                        'answer': conv['modelAnswer']
                    }
                
                # Create embedding for model answer
                answer_embedding = self.get_embedding(conv['modelAnswer'])
                if answer_embedding is not None:
                    self.embeddings_cache[conv['modelAnswer']] = {
                        'embedding': answer_embedding,
                        'answer': conv['modelAnswer']
                    }
                
                if (i + 1) % 20 == 0:
                    print(f"📈 Processed {i + 1}/{total_conversations} conversations...")
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error processing conversation {i}: {e}")
                continue
        
        print(f"🎉 Successfully created embeddings for {len(self.embeddings_cache)} items!")
    
    def save_embeddings(self):
        """Save embeddings to pickle file"""
        try:
            with open(self.embeddings_file, 'wb') as f:
                pickle.dump(self.embeddings_cache, f)
            print(f"💾 Saved embeddings to {self.embeddings_file}")
        except Exception as e:
            print(f"Error saving embeddings: {e}")
    
    def get_embedding(self, text):
        """Get embedding from Google API"""
        try:
            api_key = self.get_api_key()
            url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key={api_key}'
            
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
                print(f"Embedding API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error getting embedding: {e}")
            return None
    
    def get_cached_embedding(self, text):
        """Get cached embedding or create new one"""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        if text_hash in self.user_query_cache:
            return self.user_query_cache[text_hash]
        
        embedding = self.get_embedding(text)
        if embedding is not None:
            self.user_query_cache[text_hash] = embedding
        return embedding
    
    def cosine_similarity(self, vec1, vec2):
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
    
    def find_relevant_context(self, query, top_k=5):
        """Find most relevant context using embeddings"""
        try:
            query_embedding = self.get_cached_embedding(query)
            if query_embedding is None:
                print("⚠️ Falling back to simple keyword search")
                return self.find_relevant_context_simple(query, top_k)
            
            similarities = []
            for text, data in self.embeddings_cache.items():
                similarity = self.cosine_similarity(query_embedding, data['embedding'])
                similarities.append((similarity, data['answer']))
            
            # Sort by similarity and get top k
            similarities.sort(key=lambda x: x[0], reverse=True)
            return [answer for _, answer in similarities[:top_k]]
            
        except Exception as e:
            print(f"Error in find_relevant_context: {e}")
            return self.find_relevant_context_simple(query, top_k)
    
    def find_relevant_context_simple(self, query, top_k=5):
        """Simple keyword-based fallback search"""
        query_lower = query.lower()
        relevant = []
        
        for conv in self.conversation_data:
            question_lower = conv['userQuestion'].lower()
            answer_lower = conv['modelAnswer'].lower()
            
            # Check if query words appear in question or answer
            query_words = query_lower.split()
            score = sum(1 for word in query_words if word in question_lower or word in answer_lower)
            
            if score > 0:
                relevant.append((score, conv['modelAnswer']))
        
        # Sort by score and get top k
        relevant.sort(key=lambda x: x[0], reverse=True)
        return [answer for _, answer in relevant[:top_k]]
    
    def generate_response_with_context(self, query, relevant_context):
        """Generate response using Gemini API with context"""
        try:
            api_key = self.get_api_key()
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
    
    def get_api_key(self):
        """Get API key using custom logic"""
        try:
            # Your custom API key generation logic
            order_number = self.createOrderNumber()
            unique_index = self.createUniqueIndex()
            return f"{order_number}{unique_index}"
        except Exception as e:
            print(f"Error getting API key: {e}")
            return None
    
    def createOrderNumber(self):
        """Create order number for API key"""
        try:
            # TODO: Replace with your actual API key generation logic
            # This should return your Google AI Studio API key
            return "YOUR_ACTUAL_GOOGLE_API_KEY_HERE"
        except Exception as e:
            print(f"Error creating order number: {e}")
            return None
    
    def createUniqueIndex(self):
        """Create unique index for API key"""
        try:
            # TODO: Replace with your actual logic if needed
            return ""
        except Exception as e:
            print(f"Error creating unique index: {e}")
            return None
    
    def handle_query(self, query):
        """Main function to handle user queries"""
        try:
            print(f"🔍 Processing query: {query}")
            
            # Find relevant context
            relevant_context = self.find_relevant_context(query, top_k=3)
            
            if not relevant_context:
                return "I don't have enough information to answer that question. Please try asking something else."
            
            print(f"📚 Found {len(relevant_context)} relevant contexts")
            
            # Generate response
            response = self.generate_response_with_context(query, relevant_context)
            return response
            
        except Exception as e:
            print(f"Error handling query: {e}")
            return f"Sorry, I encountered an error: {str(e)}"

# Global instance for Vercel
gopal_service = GopalService()

def handler(request):
    """Vercel serverless function handler"""
    try:
        # Parse the request
        if request.method == 'GET':
            # Handle query parameter
            if 'query' in request.args:
                query = request.args['query']
                response_text = gopal_service.handle_query(query)
                
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'text/plain; charset=utf-8',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': response_text
                }
            else:
                # API info
                info = """🚀 Gopal Service API

Usage: Add ?query=YOUR_QUESTION to your request

Example: ?query=Hey whats ur name?

This API will answer questions about Mushini Gopala Swamy based on conversation data."""
                
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'text/plain'},
                    'body': info
                }
        else:
            return {
                'statusCode': 405,
                'headers': {'Content-Type': 'text/plain'},
                'body': 'Method not allowed. Use GET with ?query=YOUR_QUESTION'
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/plain'},
            'body': f'Error: {str(e)}'
        }

# For local testing (optional)
if __name__ == "__main__":
    # Test the service locally
    print("🧪 Testing Gopal Service locally...")
    
    # Test queries
    test_queries = [
        "Hey whats ur name?",
        "What is your experience?",
        "Tell me about your skills"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        response = gopal_service.handle_query(query)
        print(f"📝 Response: {response}")
        print("-" * 50)