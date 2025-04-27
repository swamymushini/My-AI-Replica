import json
import requests
from http.server import BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):
    
    def handle_api_request(self, prompt):
        # Function to decode the API key
        def handle_decode(encoded):
            try:
                decoded_string = bytes(encoded, 'utf-8').decode('base64')
                print('API Key decoded successfully')
                return decoded_string
            except Exception as error:
                print('Decoding failed:', error)
                raise Exception('Invalid API Key')

        # Your encoded API key
        encoded_api_key = 'QUl6YVN5RFMxdEVBakhVaURjTVFsOUtlaThCTmRSUzF5NEl3WGRN'

        # Decode the API key
        api_key = handle_decode(encoded_api_key)

        # Prepare the API request body
        api_url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}'
        headers = {
            'Content-Type': 'application/json',
        }

        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        # Make the API call
        response = requests.post(api_url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            return response.json()  # Return the response from the API
        else:
            print('Error in API request:', response.status_code)
            return {"error": "API request failed"}

    def do_GET(self):
        try:
            prompt = 'Explain how AI works'  # This can be dynamic based on the request
            result = self.handle_api_request(prompt)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            self.wfile.write(json.dumps(result).encode('utf-8'))
        
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode('utf-8'))
