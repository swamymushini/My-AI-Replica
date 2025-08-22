import json
import base64
import requests
import numpy as np
from http.server import BaseHTTPRequestHandler
import time
import os
import hashlib
import pickle

class Handler(BaseHTTPRequestHandler):
    
    def __init__(self, *args, **kwargs):
        # Initialize conversation data and embeddings
        self.conversation_data = self.load_conversation_data()
        self.embeddings_cache = {}
        self.user_query_cache = {}
        self.embeddings_file = 'conversation_embeddings.pkl'
        
        # Load or create embeddings
        self.load_or_create_embeddings()
        
        super().__init__(*args, **kwargs)
    
    def load_conversation_data(self):
        """Load conversation data from JSON file"""
        try:
            with open('conversation_data.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Warning: conversation_data.json not found")
            return []
    
    def load_or_create_embeddings(self):
        """Load existing embeddings or create new ones"""
        print("🔄 Loading or creating conversation embeddings...")
        
        # Try to load existing embeddings
        if os.path.exists(self.embeddings_file):
            try:
                with open(self.embeddings_file, 'rb') as f:
                    self.embeddings_cache = pickle.load(f)
                print(f"✅ Loaded {len(self.embeddings_cache)} existing embeddings from cache")
                return
            except Exception as e:
                print(f"⚠️  Failed to load embeddings cache: {e}")
        
        # Create new embeddings for all conversations
        print("🆕 Creating new embeddings for all conversations...")
        self.create_all_embeddings()
        
        # Save embeddings for future use
        self.save_embeddings()
    
    def create_all_embeddings(self):
        """Create embeddings for all conversations"""
        total_conversations = len(self.conversation_data)
        print(f"📊 Processing {total_conversations} conversations...")
        
        for i, conv in enumerate(self.conversation_data):
            question = conv.get('userQuestion', '')
            answer = conv.get('modelAnswer', '')
            
            # Create embeddings for both question and answer
            question_embedding = self.get_embedding(question)
            answer_embedding = self.get_embedding(answer)
            
            # Store embeddings with metadata
            self.embeddings_cache[i] = {
                'question': question,
                'answer': answer,
                'question_embedding': question_embedding,
                'answer_embedding': answer_embedding
            }
            
            # Progress indicator
            if (i + 1) % 20 == 0 or (i + 1) == total_conversations:
                print(f"📈 Processed {i + 1}/{total_conversations} conversations...")
            
            # Small delay to respect API rate limits
            time.sleep(0.1)
        
        print(f"🎉 Successfully created embeddings for {total_conversations} conversations!")
    
    def save_embeddings(self):
        """Save embeddings to file for future use"""
        try:
            with open(self.embeddings_file, 'wb') as f:
                pickle.dump(self.embeddings_cache, f)
            print(f"💾 Saved embeddings to {self.embeddings_file}")
        except Exception as e:
            print(f"⚠️  Failed to save embeddings: {e}")
    
    def get_embedding(self, text):
        """Get embedding for text using Google's gemini-embedding-001 model"""
        try:
            api_key = self.get_api_key()
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key={api_key}"
            
            headers = {
                'Content-Type': 'application/json',
            }
            
            data = {
                "model": "models/gemini-embedding-001",
                "content": {
                    "parts": [
                        {"text": text}
                    ]
                }
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                embedding = result.get('embedding', {}).get('values', [])
                return embedding
            else:
                print(f"❌ Embedding API error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting embedding: {e}")
            return []
    
    def get_cached_embedding(self, text):
        """Get embedding with caching to avoid repeated API calls"""
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        
        if text_hash in self.user_query_cache:
            return self.user_query_cache[text_hash]
        
        embedding = self.get_embedding(text)
        if embedding:
            self.user_query_cache[text_hash] = embedding
        
        return embedding
    
    def cosine_similarity(self, vec1, vec2):
        """Calculate cosine similarity between two vectors"""
        if not vec1 or not vec2:
            return 0.0
        
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return dot_product / (norm1 * norm2)
    
    def find_relevant_context(self, query, top_k=5):
        """Find most relevant conversation context using fast similarity search"""
        # Get embedding for user query
        query_embedding = self.get_cached_embedding(query)
        
        if not query_embedding:
            print("⚠️  Could not get query embedding, using simple search...")
            return self.find_relevant_context_simple(query, top_k)
        
        # Fast similarity search using pre-computed embeddings
        similarities = []
        for idx, conv_data in self.embeddings_cache.items():
            # Calculate similarity with question and answer
            question_sim = self.cosine_similarity(query_embedding, conv_data['question_embedding'])
            answer_sim = self.cosine_similarity(query_embedding, conv_data['answer_embedding'])
            
            # Use the higher similarity
            max_sim = max(question_sim, answer_sim)
            
            if max_sim > 0.1:  # Only include relevant matches
                similarities.append((max_sim, idx, conv_data))
        
        # Sort by similarity and return top_k
        similarities.sort(key=lambda x: x[0], reverse=True)
        relevant_contexts = [item[2] for item in similarities[:top_k]]
        
        print(f"🔍 Found {len(relevant_contexts)} relevant contexts for query")
        return relevant_contexts
    
    def find_relevant_context_simple(self, query, top_k=5):
        """Simple keyword-based search as fallback"""
        query_lower = query.lower()
        relevant_conversations = []
        
        for i, conv in enumerate(self.conversation_data):
            question = conv.get('userQuestion', '').lower()
            answer = conv.get('modelAnswer', '').lower()
            
            # Simple keyword matching
            score = 0
            for word in query_lower.split():
                if word in question:
                    score += 2
                if word in answer:
                    score += 1
            
            if score > 0:
                relevant_conversations.append((score, conv))
        
        # Sort by score and return top_k
        relevant_conversations.sort(key=lambda x: x[0], reverse=True)
        return [conv for score, conv in relevant_conversations[:top_k]]
    
    def generate_response_with_context(self, query, relevant_context):
        """Generate response using Gemini with relevant context"""
        try:
            api_key = self.get_api_key()
            
            # Build context string from relevant conversations
            context_string = ""
            for i, conv in enumerate(relevant_context):
                context_string += f"Q: {conv['question']}\nA: {conv['answer']}\n\n"
            
            # Create system prompt
            system_prompt = """You are Mushini Gopala Swamy, a Senior Software Engineer with nearly 6 years of experience. 
            You specialize in Java, Spring Boot, AWS, Kafka, ReactJS, and microservices. 
            You have a strong background in designing scalable, high-performance systems.
            
            Answer questions based on the provided conversation context. If the question is not related to your profile, 
            politely redirect to ask about your professional background. Always be helpful and professional."""
            
            # Prepare the API request
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
            
            headers = {
                'Content-Type': 'application/json',
            }
            
            data = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {
                                "text": f"{system_prompt}\n\nContext from previous conversations:\n{context_string}\n\nUser Question: {query}\n\nPlease provide a helpful response based on the context above."
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                text = (
                    result.get("candidates", [{}])[0]
                    .get("content", {})
                    .get("parts", [{}])[0]
                    .get("text", "")
                )
                return text.strip()
            else:
                return f"Error generating response: {response.status_code}"
                
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_api_key(self):
        """Get API key using your existing logic"""
        def createOrderNumber(encoded):
            try:
                decoded_bytes = base64.b64decode(encoded)
                decoded_string = decoded_bytes.decode('utf-8')
                return decoded_string
            except Exception as error:
                print('Order number creation failed:', error)
                raise Exception('Invalid order number created')

        def createUniqueIndex():
            num = 1
            letter_code = 97
            
            for i in range(1000):  
                num += i
                if i % 7 == 0:
                    num -= 2
            
            while num > 5:
                num -= 1
            
            for j in range(50):
                letter_code += (j % 2) * 2
                if j % 5 == 0:
                    letter_code += 1
            
            while letter_code < 104:
                letter_code += 1
            
            result = str(num) + chr(letter_code)
            result_number = int(str(num))
            return result_number

        orderReceiver = "UVVsNllWTjVReTFrZFVnNVdHVktXbkpGV0U="
        orderReceiver = createOrderNumber(orderReceiver)
        uniqueGeneratedOrder = createUniqueIndex()+4
        orderNumber = createOrderNumber(orderReceiver+str(uniqueGeneratedOrder)+"RVFBCR2l2Y1hKcUdrUFdxUWpN")

        orderReceiver2 = "VVZWc05sbFdUalZSTTNCS1ZHeFdiVk5yWkV4WlY="
        orderReceiver2 = createOrderNumber(orderReceiver2)
        uniqueGeneratedOrder2 = createUniqueIndex()-2
        orderNumber2 = createOrderNumber(orderReceiver2+str(uniqueGeneratedOrder2)+"hhUlV0TlIybEVOMlJwZFRKNWIweHNUV2s1TW10Vg==")
        orderNumber2 = createOrderNumber(orderNumber2)

        current_time_ms = int(time.time() * 1000)
        selected_order_number = orderNumber2 if current_time_ms % 2 == 0 else orderNumber
        
        return selected_order_number
    
    def handle_query(self, query):
        """Main method to handle user queries"""
        try:
            # Find relevant context using fast similarity search
            relevant_context = self.find_relevant_context(query)
            
            # Generate response with context
            response = self.generate_response_with_context(query, relevant_context)
            
            return response
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def do_GET(self):
        """Handle GET requests with the specific URL pattern"""
        try:
            if self.path.startswith('/gopal-service/query'):
                if '=' in self.path:
                    query = self.path.split('=')[-1]
                    import urllib.parse
                    query = urllib.parse.unquote(query)
                    
                    response_text = self.handle_query(query)
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'text/plain; charset=utf-8')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    self.wfile.write(response_text.encode('utf-8'))
                else:
                    self.send_response(400)
                    self.send_header('Content-type', 'text/plain')
                    self.end_headers()
                    self.wfile.write("Error: No query parameter provided. Use: /gopal-service/query?=YOUR_QUESTION".encode('utf-8'))
            else:
                # Return API info
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                
                info = """🚀 Gopal Service API

Usage: /gopal-service/query?=YOUR_QUESTION

Example: /gopal-service/query?=Hey whats ur name?

This API will answer questions about Mushini Gopala Swamy based on conversation data."""
                
                self.wfile.write(info.encode('utf-8'))
                
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode('utf-8'))

if __name__ == "__main__":
    from http.server import HTTPServer
    
    handler = Handler
    server = HTTPServer(('localhost', 8000), handler)
    print("🚀 Gopal Service API running on http://localhost:8000")
    print("💡 First run will create embeddings, subsequent runs will be instant!")
    print("Test with: http://localhost:8000/gopal-service/query?=Hey whats ur name?")
    server.serve_forever()