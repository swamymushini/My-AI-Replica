#!/usr/bin/env python3
"""
Debug script to test search functionality
"""

import sys
import os
import glob

# Add the api directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))

from api.utils.search_utils import SearchUtils

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

def debug_search():
    """Debug the search functionality"""
    
    print("🔍 Debugging Search Functionality")
    print("=" * 40)
    
    # Clear cache first to ensure fresh data
    clear_cache()
    print()
    
    # Load profile data
    try:
        with open('data/myprofile.json', 'r', encoding='utf-8') as f:
            profile_data = json.load(f)
        print("✅ Profile data loaded successfully")
    except Exception as e:
        print(f"❌ Error loading profile: {e}")
        return
    
    # Test the dynamic mappings
    print("\n📊 Building dynamic keyword mappings...")
    dynamic_mappings = SearchUtils._build_dynamic_mappings(profile_data)
    
    print(f"\n🎯 Found {len(dynamic_mappings)} search categories:")
    for category, keywords in dynamic_mappings.items():
        print(f"   {category}: {keywords[:5]}...")  # Show first 5 keywords
    
    # Test specific search queries
    test_queries = [
        "What are your hobbies?",
        "Do you like reading?",
        "What do you do for fun?",
        "Tell me about your interests"
    ]
    
    print(f"\n🧪 Testing search queries:")
    for query in test_queries:
        print(f"\n❓ Query: {query}")
        print("-" * 30)
        
        # Find relevant context
        relevant_context = SearchUtils.find_relevant_context_simple(query, profile_data, top_k=3)
        
        if relevant_context:
            print(f"✅ Found {len(relevant_context)} relevant contexts")
            for i, ctx in enumerate(relevant_context[:2]):  # Show first 2
                print(f"   {i+1}. {ctx[:100]}...")
        else:
            print("❌ No relevant context found")

if __name__ == "__main__":
    import json
    debug_search()
