# 🤖 My AI Replica - Intelligent Q&A API

A sophisticated AI-powered Q&A system that answers questions about **Mushini Gopala Swamy** using Retrieval-Augmented Generation (RAG) with Google's Gemini AI and embeddings.

## 🚀 What It Does

This API creates an intelligent AI replica that can answer questions about a specific person by:

1. **📚 Knowledge Base**: Uses `conversation_data.json` containing 227+ Q&A pairs
2. **🧠 Smart Search**: Creates embeddings for semantic similarity search
3. **🔍 Context Retrieval**: Finds most relevant conversations for each question
4. **💬 AI Generation**: Uses Google Gemini 2.0 Flash to generate contextual responses
5. **⚡ Performance**: Caches embeddings for instant responses after first run

## 🏗️ Architecture

```
User Query → Embedding → Similarity Search → Context Retrieval → Gemini AI → Response
    ↓           ↓           ↓              ↓           ↓         ↓
  Text    Vectorized   Find Relevant   Top 3 Most   Generate   Smart
Input    Query        Conversations   Similar      Contextual  Answer
```

## 🏗️ Modular Code Structure

The codebase has been refactored into a clean, modular architecture for better maintainability and readability:

### **Module Responsibilities**

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| **`config/env_loader.py`** | Environment configuration | `load_env_file()`, `get_api_key()` |
| **`utils/embedding_utils.py`** | Embedding management | `EmbeddingManager`, embedding creation & caching |
| **`utils/search_utils.py`** | Search algorithms | `SearchUtils`, similarity search, fallback search |
| **`utils/api_utils.py`** | Gemini API interactions | `GeminiAPI`, response generation |
| **`services/gopal_service.py`** | Business logic orchestration | `GopalService`, query handling |
| **`handlers/api_handler.py`** | HTTP request handling | `APIHandler`, CORS, routing |

### **Benefits of Modular Structure**

✅ **Improved Readability** - Each module has a single, clear responsibility  
✅ **Better Maintainability** - Changes to one module don't affect others  
✅ **Enhanced Testability** - Each module can be tested independently  
✅ **Code Reusability** - Utility functions can be reused across modules  
✅ **Professional Structure** - Industry-standard code organization

### **Data Organization**

The project now has a clean data structure:

| Folder | Purpose | Contents |
|--------|---------|----------|
| **`data/`** | Knowledge base and profile data | `conversation_data.json`, `email_data.json`, `myprofile.json` |
| **`cache/`** | Generated embeddings and temporary files | `conversation_embeddings.pkl` |
| **`api/`** | Application code and logic | All Python modules and handlers |

## 🛠️ Technologies Used

- **Python 3.8+** - Core language
- **Google Gemini 2.0 Flash** - Text generation
- **Google Gemini Embeddings** - Vector embeddings
- **NumPy** - Mathematical operations
- **Requests** - HTTP client
- **Vercel** - Serverless deployment

## 📁 Project Structure

```
My-AI-Replica/
├── api/
│   ├── __init__.py                 # Package initialization
│   ├── index.py                    # Main entry point (simplified)
│   ├── config/
│   │   ├── __init__.py            # Config package
│   │   └── env_loader.py          # Environment configuration
│   ├── utils/
│   │   ├── __init__.py            # Utils package
│   │   ├── embedding_utils.py     # Embedding management
│   │   ├── search_utils.py        # Search and similarity
│   │   └── api_utils.py           # Gemini API interactions
│   ├── services/
│   │   ├── __init__.py            # Services package
│   │   └── gopal_service.py       # Main business logic
│   └── handlers/
│       ├── __init__.py            # Handlers package
│       └── api_handler.py         # HTTP request handling
├── data/
│   ├── __init__.py                # Data package
│   ├── conversation_data.json     # Knowledge base (227 Q&A pairs)
│   ├── email_data.json            # Email templates and responses
│   └── myprofile.json             # Personal profile information
├── cache/
│   ├── __init__.py                # Cache package
│   └── conversation_embeddings.pkl # Cached embeddings (auto-generated)
├── requirements.txt               # Python dependencies
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd My-AI-Replica
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Environment Variable
```bash
# Create .env file
echo "GOOGLE_API_KEY=your_google_api_key_here" > .env
```

### 4. Test Locally
```bash
cd api
python index.py
```

### 5. Test Modular Structure (Optional)
```bash
# From project root
python test_modular.py
```

## 🌐 Deploy to Vercel

### 1. Push to GitHub
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### 2. Connect to Vercel
- Import your GitHub repository
- Vercel auto-detects Python function

### 3. Set Environment Variable
In Vercel dashboard:
- Go to **Settings** → **Environment Variables**
- Add: `GOOGLE_API_KEY` = `your_api_key`

### 4. Deploy
Vercel automatically deploys on every push!

## 📡 API Usage

### Base URL
```
https://your-domain.vercel.app/api/index
```

### Endpoints

#### Get API Info
```
GET /api/index
```

#### Ask a Question
```
GET /api/index?query=YOUR_QUESTION
```

### Examples

```bash
# Get API info
curl "https://your-domain.vercel.app/api/index"

# Ask a question
curl "https://your-domain.vercel.app/api/index?query=Hey%20whats%20ur%20name?"

# Ask about experience
curl "https://your-domain.vercel.app/api/index?query=What%20is%20your%20experience?"
```

### Response Format
```json
{
  "statusCode": 200,
  "headers": {
    "Content-Type": "text/plain; charset=utf-8",
    "Access-Control-Allow-Origin": "*"
  },
  "body": "My name is Mushini Gopala Swamy."
}
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Google AI Studio API key | ✅ Yes |

### API Keys Setup

1. **Get Google AI Studio API Key**:
   - Visit [Google AI Studio](https://aistudio.google.com/)
   - Create API key
   - Enable Gemini models

2. **Set Locally**:
   ```bash
   export GOOGLE_API_KEY="your_key_here"
   ```

3. **Set in Vercel**:
   - Dashboard → Settings → Environment Variables

## 🧠 How It Works

### 1. **Initialization**
- Loads conversation data from JSON
- Creates embeddings for all Q&A pairs
- Saves embeddings to `.pkl` file for future use

### 2. **Query Processing**
- User asks a question
- System creates embedding for the question
- Finds most similar conversations using cosine similarity
- Retrieves top 3 most relevant contexts

### 3. **Response Generation**
- Constructs system prompt with retrieved context
- Sends to Google Gemini 2.0 Flash
- Returns intelligent, context-aware response

### 4. **Caching**
- User query embeddings are cached
- Conversation embeddings are persistent
- Subsequent queries are lightning fast

## 📊 Performance

- **First Run**: ~30-60 seconds (creates embeddings)
- **Subsequent Runs**: Instant (loads cached embeddings)
- **Query Response**: 2-5 seconds (Gemini API + processing)
- **Concurrent Users**: Unlimited (serverless)

## 🔒 Security Features

- ✅ **API Key Protection**: Never committed to git
- ✅ **Environment Variables**: Secure configuration
- ✅ **CORS Support**: Cross-origin requests allowed
- ✅ **Error Handling**: Graceful failure responses

## 🚨 Troubleshooting

### Common Issues

1. **"GOOGLE_API_KEY environment variable not set"**
   - Set environment variable in Vercel
   - Redeploy after setting

2. **Slow First Response**
   - Normal behavior - creating embeddings
   - Subsequent calls will be fast

3. **API Key Invalid**
   - Check Google AI Studio API key
   - Ensure Gemini models are enabled

4. **Embedding Errors**
   - Check API key validity
   - Verify internet connectivity

### Debug Mode

Enable debug logging by checking Vercel function logs:
- Vercel Dashboard → Functions → View Logs

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- **Google AI Studio** for Gemini models
- **Vercel** for serverless hosting
- **OpenAI** for RAG architecture inspiration

## 📞 Support

For issues and questions:
- Create GitHub issue
- Check Vercel deployment logs
- Verify environment variables

---

**Built with ❤️ using Python, Google Gemini, and Vercel**
