# Enhanced AI Replica API

This enhanced API uses Google's Gemini 2.5 Pro for text generation and the text-embedding-004 model for semantic search. It creates embeddings for your conversation data and provides intelligent, context-aware responses.

## Features

- **Semantic Search**: Uses Google's embeddings to find relevant conversation context
- **Context-Aware Responses**: Generates responses using Gemini 2.5 Pro with relevant context
- **Conversation Data Integration**: Automatically loads and processes your `conversation_data.json`
- **RESTful API**: Supports both GET and POST requests
- **CORS Enabled**: Can be used from web applications

## How It Works

1. **Initialization**: When the API starts, it loads your conversation data and creates embeddings for all questions and answers
2. **Query Processing**: When a user asks a question, the API:
   - Creates an embedding for the user's query
   - Finds the most semantically similar conversations using cosine similarity
   - Uses the relevant context to generate a response with Gemini 2.5 Pro
3. **Response Generation**: The response is generated with full context awareness

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements_enhanced.txt
```

### 2. Run the API

```bash
python api/enhanced_api.py
```

The API will start on `http://localhost:8000`

### 3. Test the API

```bash
python test_enhanced_api.py
```

## API Endpoints

### GET `/`
Returns API information and available endpoints.

### GET `/?query=YOUR_QUESTION_HERE`
Query the API with a question. The question should be URL-encoded.

**Example:**
```
http://localhost:8000/?query=What%20is%20your%20experience%20with%20Java
```

### POST `/`
Send a POST request with JSON body containing the query.

**Example:**
```json
{
  "query": "Tell me about your AWS experience"
}
```

## Response Format

```json
{
  "response": "Generated response from Gemini 2.5 Pro",
  "relevant_context": [
    {
      "question": "Relevant question from conversation data...",
      "answer": "Relevant answer from conversation data..."
    }
  ],
  "query": "Original user query",
  "timestamp": 1234567890.123
}
```

## Usage Examples

### Using cURL

```bash
# GET request
curl "http://localhost:8000/?query=What%20is%20your%20name"

# POST request
curl -X POST http://localhost:8000/ \
  -H "Content-Type: application/json" \
  -d '{"query": "What is your experience with Spring Boot?"}'
```

### Using Python

```python
import requests

# GET request
response = requests.get("http://localhost:8000/?query=What%20is%20your%20notice%20period")
result = response.json()
print(result['response'])

# POST request
data = {"query": "Tell me about your projects"}
response = requests.post("http://localhost:8000/", json=data)
result = response.json()
print(result['response'])
```

### Using JavaScript/Fetch

```javascript
// GET request
fetch('http://localhost:8000/?query=What%20is%20your%20experience')
  .then(response => response.json())
  .then(data => console.log(data.response));

// POST request
fetch('http://localhost:8000/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: 'What technologies do you work with?'
  })
})
.then(response => response.json())
.then(data => console.log(data.response));
```

## Configuration

The API automatically uses your existing API key logic from the original `index.py`. It will:

1. Use the same base64 decoding mechanism
2. Rotate between two API keys based on timestamp
3. Apply the same rate limiting considerations

## Rate Limits

- **Google AI Studio Free Tier**: 15 requests per minute for embeddings, 15 requests per minute for text generation
- **Embeddings**: Created once during initialization, then cached
- **Text Generation**: Each query generates one request to Gemini 2.5 Pro

## Error Handling

The API includes comprehensive error handling:

- Invalid queries return appropriate error messages
- API failures are gracefully handled
- CORS preflight requests are supported
- Detailed error logging for debugging

## Performance Considerations

- **Embeddings Cache**: All conversation embeddings are cached in memory
- **Similarity Calculation**: Uses efficient numpy operations for cosine similarity
- **Context Selection**: Limits context to top 3 most relevant conversations
- **Response Generation**: Single API call to Gemini per query

## Troubleshooting

### Common Issues

1. **Port Already in Use**: Change the port in `enhanced_api.py` line 1000
2. **API Key Issues**: Check your Google AI Studio API key configuration
3. **Memory Issues**: Large conversation datasets may require more memory for embeddings

### Debug Mode

The API prints initialization progress and error details to help with debugging.

## Security Notes

- The API includes CORS headers for web application usage
- API keys are handled using your existing secure method
- No sensitive data is logged or exposed

## Future Enhancements

Potential improvements:
- Persistent embedding storage
- Batch processing for large datasets
- Advanced similarity algorithms
- Response caching
- User authentication
- Rate limiting per user
