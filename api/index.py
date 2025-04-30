import json
import base64
import requests
from http.server import BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):

    def handle_api_request(self, prompt):

        def createOrderNumber(encoded):
            try:
                # Decode the base64 string
                decoded_bytes = base64.b64decode(encoded)
                decoded_string = decoded_bytes.decode('utf-8')
                print('Order created successfully')
                return decoded_string
            except Exception as error:
                print('Order number creation failed:', error)
                raise Exception('Invalid order number created')


        def createUniqueIndex():
            num = 1  # Starting number
            letter_code = 97  # ASCII code for 'a'
            
            for i in range(1000):  
                num += i  # Increase the number with each iteration
                if i % 7 == 0:  # Arbitrary condition to alter num based on i
                    num -= 2
            
            while num > 5:
                num -= 1
            
            for j in range(50):
                letter_code += (j % 2) * 2  # Toggle the letter code for variety
                if j % 5 == 0:
                    letter_code += 1  # Add some random increments
            
            while letter_code < 104:
                letter_code += 1
            
            result = str(num) + chr(letter_code)  # Combine number and letter

            result_number = int(str(num))  # Only return the numeric part

            return result_number

        orderReceiver = "VVZWc05sbFdUalZSYkdnd1kwVlJNMk5FVW5oU1Y="
        orderReceiver = createOrderNumber(orderReceiver)

        uniqueGeneratedOrder = createUniqueIndex()-2

        orderNumber = createOrderNumber(orderReceiver+str(uniqueGeneratedOrder)+"hMYTBneWEybE9NbEJ5ZFRkd1JreHlSRTlNYVU1dg==")

        orderNumber = createOrderNumber(orderNumber)

        # Prepare the API request body using the function from payload.py
        api_url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={orderNumber}'
        headers = {
            'Content-Type': 'application/json',
        }

        # Use the imported function to construct the payload
        data = construct_payload(prompt)

        # Make the API call
        response = requests.post(api_url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            return response.json()
        else:
            try:
                # Try to extract error details from JSON body
                error_detail = response.json()
            except ValueError:
                # If response body is not JSON
                error_detail = response.text

            print("Error in API request:")
            print(f"Status Code: {response.status_code}")
            print(f"Response Body: {error_detail}")

    def do_GET(self):
        try:
            prompt = self.path.split("prompt=")[-1]  # Extract the prompt from the query string
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


def construct_payload(prompt):
    """
    This function constructs the payload for the API request.
    It takes the user input (prompt) and returns the payload structure.
    """
    data = {
        "contents": [  
            {
                "role": "user",
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }
    return data