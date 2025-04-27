import base64

def handle_decode(encoded):
    try:
        # Decode the base64 string
        decoded_bytes = base64.b64decode(encoded)
        decoded_string = decoded_bytes.decode('utf-8')  # Convert bytes to string
        print('API Key decoded successfully')
        return decoded_string
    except Exception as error:
        print('Decoding failed:', error)
        raise Exception('Invalid API Key')

# Your encoded API key
encoded_api_key = 'QUl6YVN5RFMxdEVBakhVaURjTVFsOUtlaThCTmRSUzF5NEl3WGRN'

# Call the decode function
decoded_key = handle_decode(encoded_api_key)
print(f'Decoded API Key: {decoded_key}')
