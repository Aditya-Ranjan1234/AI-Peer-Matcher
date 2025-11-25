"""
NLP and Matching Logic for Peer Learning Matcher
Uses Sentence Transformers for semantic embeddings and cosine similarity for matching.
"""

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Dict, Tuple
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Singleton service for generating text embeddings using Sentence Transformers.
    Uses cached model from backend/model_cache for faster cold starts (no download needed).
    """
    _model = None
    
    def get_model(self):
        """Get or initialize the Sentence Transformer model from cache"""
        if self._model is None:
            # Use preloaded model from cache to avoid download on cold start
            cache_folder = os.path.join(os.path.dirname(__file__), 'model_cache')
            logger.info(f"Loading Sentence Transformer model from cache: {cache_folder}")
            
            self._model = SentenceTransformer(
                'all-MiniLM-L6-v2',
                cache_folder=cache_folder
            )
            logger.info("Model loaded successfully from cache!")
        return self._model
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding vector for input text
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        if not text or not text.strip():
            # Return zero vector for empty text
            return [0.0] * 384  # all-MiniLM-L6-v2 produces 384-dim vectors
        
        model = self.get_model()
        embedding = model.encode(text.strip(), convert_to_numpy=True)
        return embedding.tolist()


def cosine_sim(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors
    
    Args:
        vec1: First embedding vector
        vec2: Second embedding vector
        
    Returns:
        Similarity score between -1 and 1 (higher is more similar)
    """
    vec1_np = np.array(vec1).reshape(1, -1)
    vec2_np = np.array(vec2).reshape(1, -1)
    
    # Handle zero vectors
    if np.all(vec1_np == 0) or np.all(vec2_np == 0):
        return 0.0
    
    similarity = cosine_similarity(vec1_np, vec2_np)[0][0]
    return float(similarity)


def complementary_score(profile_a: Dict, profile_b: Dict) -> float:
    """
    Calculate complementary matching score between two student profiles
    
    The score measures how well students can help each other:
    - A's strengths should align with B's weaknesses
    - B's strengths should align with A's weaknesses
    
    Args:
        profile_a: First student profile with embeddings
        profile_b: Second student profile with embeddings
        
    Returns:
        Average complementary similarity score (0 to 1)
    """
    # A's strengths help B's weaknesses
    score_1 = cosine_sim(profile_a['strengths_emb'], profile_b['weaknesses_emb'])
    
    # B's strengths help A's weaknesses
    score_2 = cosine_sim(profile_b['strengths_emb'], profile_a['weaknesses_emb'])
    
    # Average of both directions
    avg_score = (score_1 + score_2) / 2.0
    
    # Ensure score is in valid range [0, 1]
    return max(0.0, min(1.0, avg_score))


def find_best_matches(
    student_id: str,
    profiles: Dict[str, Dict],
    top_k: int = 3
) -> List[Tuple[str, str, float, str, str]]:
    """
    Find the best matching students for a given student
    
    Args:
        student_id: ID of the target student
        profiles: Dictionary of all student profiles
        top_k: Number of top matches to return
        
    Returns:
        List of tuples: (student_id, name, score, strengths, weaknesses)
    """
    if student_id not in profiles:
        return []
    
    target_student = profiles[student_id]
    scores = []
    
    for pid, profile in profiles.items():
        if pid == student_id:
            continue  # Skip self
        
        score = complementary_score(target_student, profile)
        scores.append((
            pid,
            profile['name'],
            score,
            profile['strengths'],
            profile['weaknesses']
        ))
    
    # Sort by score (descending) and return top K
    scores.sort(key=lambda x: x[2], reverse=True)
    return scores[:top_k]
