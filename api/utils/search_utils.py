import numpy as np

class SearchUtils:
    @staticmethod
    def cosine_similarity(vec1, vec2):
        """Calculate cosine similarity between two vectors"""
        try:
            vec1 = np.array(vec1)
            vec2 = np.array(vec2)
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            return dot_product / (norm1 * norm2)
        except Exception as e:
            print(f"Error calculating cosine similarity: {e}")
            return 0.0
    
    @staticmethod
    def find_relevant_context(query, embeddings_cache, get_cached_embedding_func, top_k=5):
        """Find most relevant context using embeddings"""
        try:
            query_embedding = get_cached_embedding_func(query)
            if query_embedding is None:
                print("⚠️ Falling back to simple keyword search")
                return None  # Signal to use fallback search
            
            similarities = []
            for text, data in embeddings_cache.items():
                similarity = SearchUtils.cosine_similarity(query_embedding, data['embedding'])
                similarities.append((similarity, data['content']))
            
            # Sort by similarity and get top k
            similarities.sort(key=lambda x: x[0], reverse=True)
            return [content for _, content in similarities[:top_k]]
            
        except Exception as e:
            print(f"Error in find_relevant_context: {e}")
            return None  # Signal to use fallback search
    
    @staticmethod
    def find_relevant_context_simple(query, profile_data, top_k=5):
        """Simple keyword-based fallback search for profile data"""
        query_lower = query.lower()
        relevant = []
        
        print(f"🔍 Simple search for: '{query}'")
        print(f"📊 Profile data has {len(profile_data)} chunks")
        
        # Define keyword mappings for common questions
        keyword_mappings = {
            'name': ['name', 'mushini', 'gopala', 'swamy'],
            'experience': ['experience', 'years', '6.2', '6+'],
            'skills': ['skills', 'programming', 'java', 'python', 'javascript'],
            'ctc': ['ctc', 'salary', 'lpa', '31'],
            'relocation': ['relocation', 'relocate', 'open to'],
            'project': ['project', 'eod', 'fintech', 'work'],
            'notice': ['notice', 'period', '45', '60'],
            'company': ['company', 'rocket', 'software', 'working'],
            'languages': ['languages', 'java', 'python', 'javascript', 'telugu', 'hindi'],
            'who': ['name', 'mushini', 'gopala', 'swamy', 'senior', 'engineer'],
            'what': ['skills', 'experience', 'role', 'company']
        }
        
        # Find the best matching category
        best_category = None
        best_score = 0
        
        for category, keywords in keyword_mappings.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > best_score:
                best_score = score
                best_category = category
        
        print(f"🎯 Best category: {best_category} (score: {best_score})")
        
        # If no specific category found, use general word matching
        if best_score == 0:
            print("🔄 Using general word matching...")
            for chunk in profile_data:
                chunk_lower = chunk.lower()
                query_words = query_lower.split()
                score = sum(1 for word in query_words if word in chunk_lower)
                if score > 0:
                    relevant.append((score, chunk))
                    print(f"   ✅ Found match (score: {score}): {chunk[:50]}...")
        else:
            # Use category-specific matching
            print(f"🎯 Using category-specific matching for '{best_category}'...")
            for chunk in profile_data:
                chunk_lower = chunk.lower()
                category_keywords = keyword_mappings.get(best_category, [])
                score = sum(1 for keyword in category_keywords if keyword in chunk_lower)
                if score > 0:
                    relevant.append((score, chunk))
                    print(f"   ✅ Found match (score: {score}): {chunk[:50]}...")
        
        print(f"📚 Total relevant chunks found: {len(relevant)}")
        
        # Sort by score and get top k
        relevant.sort(key=lambda x: x[0], reverse=True)
        return [chunk for _, chunk in relevant[:top_k]]
