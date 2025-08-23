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
                similarities.append((similarity, data['answer']))
            
            # Sort by similarity and get top k
            similarities.sort(key=lambda x: x[0], reverse=True)
            return [answer for _, answer in similarities[:top_k]]
            
        except Exception as e:
            print(f"Error in find_relevant_context: {e}")
            return None  # Signal to use fallback search
    
    @staticmethod
    def find_relevant_context_simple(query, conversation_data, top_k=5):
        """Simple keyword-based fallback search"""
        query_lower = query.lower()
        relevant = []
        
        for conv in conversation_data:
            question_lower = conv['userQuestion'].lower()
            answer_lower = conv['modelAnswer'].lower()
            
            # Check if query words appear in question or answer
            query_words = query_lower.split()
            score = sum(1 for word in query_words if word in question_lower or word in answer_lower)
            
            if score > 0:
                relevant.append((score, conv['modelAnswer']))
        
        # Sort by score and get top k
        relevant.sort(key=lambda x: x[0], reverse=True)
        return [answer for _, answer in relevant[:top_k]]
