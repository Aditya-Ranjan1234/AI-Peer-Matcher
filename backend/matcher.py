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
    # Validate that all required embedding fields exist
    required_fields = ['strengths_emb', 'weaknesses_emb']
    
    for field in required_fields:
        if field not in profile_a:
            logger.error(f"Profile {profile_a.get('id', 'UNKNOWN')} missing field: {field}")
            return 0.0
        if field not in profile_b:
            logger.error(f"Profile {profile_b.get('id', 'UNKNOWN')} missing field: {field}")
            return 0.0
    
    # Validate embeddings are not None and are lists/arrays
    if not profile_a['strengths_emb'] or not profile_a['weaknesses_emb']:
        logger.error(f"Profile {profile_a.get('id', 'UNKNOWN')} has null embeddings")
        return 0.0
    if not profile_b['strengths_emb'] or not profile_b['weaknesses_emb']:
        logger.error(f"Profile {profile_b.get('id', 'UNKNOWN')} has null embeddings")
        return 0.0
    
    try:
        # A's strengths help B's weaknesses
        score_1 = cosine_sim(profile_a['strengths_emb'], profile_b['weaknesses_emb'])
        
        # B's strengths help A's weaknesses
        score_2 = cosine_sim(profile_b['strengths_emb'], profile_a['weaknesses_emb'])
        
        # Average of both directions
        avg_score = (score_1 + score_2) / 2.0
        
        # Ensure score is in valid range [0, 1]
        return max(0.0, min(1.0, avg_score))
    except Exception as e:
        logger.error(f"Error calculating complementary score: {e}")
        return 0.0


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


def find_team_of_4(
    student_id: str,
    profiles: Dict[str, Dict]
) -> Tuple[List[Dict], float]:
    """
    Form a team of 4 people who complement each other.
    Greedy approach to find 3 additional members.
    """
    if student_id not in profiles:
        return [], 0.0

    # Check for fixed teams assignment
    try:
        # Assuming fixed_teams.json is in project root (parent of backend)
        fixed_teams_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fixed_teams.json')
        if os.path.exists(fixed_teams_path):
            import json
            with open(fixed_teams_path, 'r') as f:
                fixed_map = json.load(f)
            
            if student_id in fixed_map:
                logger.info(f"Using fixed team for {student_id}")
                assignment = fixed_map[student_id]
                team_members_ids = assignment["team_members"]
                
                team_profiles = []
                for mid in team_members_ids:
                    if mid in profiles:
                        team_profiles.append(profiles[mid])
                
                # Format result
                result_members = []
                for p in team_profiles:
                    result_members.append({
                        "student_id": p['id'],
                        "name": p['name'],
                        "score": assignment["score"], 
                        "strengths": p['strengths'],
                        "weaknesses": p['weaknesses']
                    })
                return result_members, assignment["score"]
    except Exception as e:
        logger.error(f"Error loading fixed teams: {e}")
    
    team_ids = [student_id]
    # Keep track of profiles for the result
    team_profiles = [profiles[student_id]]
    
    # We need 3 more members
    for _ in range(3):
        best_peer_id = None
        best_avg_score = -1.0
        
        for pid, profile in profiles.items():
            if pid in team_ids:
                continue
            
            # Calculate average complementary score with everyone currently in the team
            total_score = 0.0
            for member_profile in team_profiles:
                total_score += complementary_score(member_profile, profile)
            
            avg_score = total_score / len(team_profiles)
            
            if avg_score > best_avg_score:
                best_avg_score = avg_score
                best_peer_id = pid
                
        if best_peer_id:
            team_ids.append(best_peer_id)
            team_profiles.append(profiles[best_peer_id])
    
    # Calculate overall team complementarity score (average of all unique pairs)
    total_pair_score = 0.0
    pair_count = 0
    import itertools
    for p1, p2 in itertools.combinations(team_profiles, 2):
        total_pair_score += complementary_score(p1, p2)
        pair_count += 1
    
    overall_score = total_pair_score / pair_count if pair_count > 0 else 0.0
    
    # Convert to standard format for frontend
    result_members = []
    for p in team_profiles:
        result_members.append({
            "student_id": p['id'],
            "name": p['name'],
            "score": overall_score, # For simplicity, each gets the team score
            "strengths": p['strengths'],
            "weaknesses": p['weaknesses']
        })
        
    return result_members, overall_score


def calculate_project_relevance(
    user_strengths_emb: List[float],
    project_desc_emb: List[float]
) -> float:
    """
    Calculate how relevant a project is to a user's strengths.
    Uses cosine similarity between strengths and project description.
    """
    if not user_strengths_emb or not project_desc_emb:
        return 0.0
        
    score = cosine_sim(user_strengths_emb, project_desc_emb)
    # Map from [-1, 1] to [0, 1]
    return max(0.0, (score + 1.0) / 2.0)
