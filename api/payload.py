# payload.py

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
