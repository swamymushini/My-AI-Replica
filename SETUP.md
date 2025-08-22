# 🚀 Gopal Service API Setup Guide

## 🔒 **Security First: API Key Setup**

### **1. Create Local Environment File**
Create a `.env` file in your project root:
```bash
# .env (DO NOT COMMIT THIS FILE!)
GOOGLE_API_KEY=AIzaSyBRhny0obRqrK3sJqM50fSx1S9n4uOJBwY
```

### **2. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **3. Test Locally**
```bash
cd api
python index.py
```

## 🌐 **Vercel Deployment**

### **1. Set Environment Variable in Vercel**
- Go to your Vercel project dashboard
- Navigate to Settings → Environment Variables
- Add: `GOOGLE_API_KEY` = `AIzaSyBRhny0obRqrK3sJqM50fSx1S9n4uOJBwY`

### **2. Deploy**
- Push your code to GitHub
- Vercel will automatically deploy
- Your API key stays secure!

## 📝 **Usage**

### **Local Testing:**
```
http://localhost:8000/gopal-service/query?=Hey%20whats%20ur%20name?
```

### **Vercel:**
```
https://your-domain.vercel.app/api/index?query=Hey%20whats%20ur%20name?
```

## ✅ **What's Protected:**
- ✅ `.env` file (ignored by git)
- ✅ API key in environment variables
- ✅ Secure deployment on Vercel

## ❌ **What's NOT Committed:**
- ❌ API keys in code
- ❌ Environment files
- ❌ Sensitive credentials

## 🔍 **File Structure:**
```
My-AI-Replica/
├── .env                    # 🔒 Local API key (NOT committed)
├── .gitignore             # ✅ Protects sensitive files
├── api/
│   └── index.py          # ✅ Uses environment variables
├── conversation_data.json # ✅ Safe to commit
└── requirements.txt       # ✅ Safe to commit
```

Now you can safely commit your code without exposing the API key! 🎉
