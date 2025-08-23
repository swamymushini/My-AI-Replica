import urllib.parse
from http.server import BaseHTTPRequestHandler
from api.services.gopal_service import GopalService

class APIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Create service instance for each request (Vercel compatibility)
            gopal_service = GopalService()
            
            # Parse query parameters
            if '?' in self.path:
                path, query_string = self.path.split('?', 1)
                query_params = {}
                for param in query_string.split('&'):
                    if '=' in param:
                        key, value = param.split('=', 1)
                        query_params[key] = value
                
                # Handle query parameter
                if 'query' in query_params:
                    query = urllib.parse.unquote(query_params['query'])
                    response_text = gopal_service.handle_query(query)
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'text/plain; charset=utf-8')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(response_text.encode('utf-8'))
                else:
                    self.send_response(400)
                    self.send_header('Content-type', 'text/plain')
                    self.end_headers()
                    self.wfile.write("Error: No query parameter provided. Use: ?query=YOUR_QUESTION".encode('utf-8'))
            else:
                # API info
                info = """🚀 Gopal Service API

Usage: Add ?query=YOUR_QUESTION to your request

Example: ?query=Hey whats ur name?

This API will answer questions about Mushini Gopala Swamy based on conversation data."""
                
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(info.encode('utf-8'))
                
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle CORS preflight request"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
