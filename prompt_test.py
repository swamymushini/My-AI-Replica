#!/usr/bin/env python3
"""
Prompt Test Script - Test individual prompts with command line arguments
Usage: python3 prompt_test.py "your question here"
"""

import sys
import os
import glob

# Add the api directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))

# Load environment variables first
from api.config.env_loader import load_env_file
load_env_file()

from api.services.gopal_service import GopalService

def clear_cache():
    """Clear all cached files to ensure fresh data"""
    print("🧹 Clearing cache files...")
    
    # Clear profile embeddings cache
    cache_files = glob.glob('cache/*.pkl')
    for cache_file in cache_files:
        try:
            os.remove(cache_file)
            print(f"   ✅ Removed: {cache_file}")
        except Exception as e:
            print(f"   ⚠️ Could not remove {cache_file}: {e}")
    
    if not cache_files:
        print("   ℹ️ No cache files found to clear")
    
    print("🧹 Cache cleared successfully!")

def test_single_prompt(question):
    """Test a single prompt and return the response"""
    
    print("🤖 AI Replica - Single Prompt Test")
    print("=" * 50)
    
    # Check if API key is loaded
    try:
        from api.config.env_loader import get_selected_model
        model = get_selected_model()
        print(f"🤖 Using AI Model: {model}")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return
    
    # Clear cache first to ensure fresh data
    clear_cache()
    print()
    
    # Initialize the service
    try:
        gopal_service = GopalService()
        print("✅ Service initialized successfully!")
        print(f"📊 Loaded {len(gopal_service.profile_data)} profile chunks")
        print()
    except Exception as e:
        print(f"❌ Error initializing service: {e}")
        return
    
    # Test the question
    print(f"❓ Question: {question}")
    print("-" * 40)
    
    try:
        response = gopal_service.handle_query(question)
        print(f"🤖 Answer: {response}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main function to handle command line arguments"""
    
    if len(sys.argv) < 2:
        print("❌ Usage: python3 prompt_test.py \"your question here\"")
        print("💡 Examples:")
        print("   python3 prompt_test.py \"who are you\"")
        print("   python3 prompt_test.py \"what is your experience\"")
        print("   python3 prompt_test.py \"tell me about your skills\"")
        return
    
    # Get the question from command line arguments
    question = sys.argv[1]
    
    # Test the prompt
    test_single_prompt(question)

if __name__ == "__main__":
    main()
