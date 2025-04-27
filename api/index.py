# api/index.py

from http.server import BaseHTTPRequestHandler

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'Hello, Vercel!')

def handler(request):
    try:
        base = MyHandler  # Replace this with the correct base class or handler class
        if not isinstance(base, type):  # Check if 'base' is a class
            raise TypeError("Expected a class type, got {0}".format(type(base)))
        return {
            "statusCode": 200,
            "body": "Handler is working!"
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Error: {str(e)}"
        }
