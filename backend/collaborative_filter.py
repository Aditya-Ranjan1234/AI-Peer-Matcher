"""
Collaborative Filtering for Peer Matching
Uses user-item matrix and similarity-based recommendations
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class CollaborativeFilterService:
    """
    Memory-based collaborative filtering service
    Uses user-user similarity based on collaboration ratings
    """
    
    def build_user_item_matrix(
        self, 
        collaborations: List[Dict]
    ) -> Tuple[np.ndarray, Dict[str, int], Dict[int, str]]:
        """
        Build user-item matrix from collaboration data
        
        Args:
            collaborations: List of collaboration documents from DB
            
        Returns:
            - matrix: NxN numpy array where matrix[i][j] = rating from user i to user j
            - user_to_idx: Dict mapping student_id -> matrix index
            - idx_to_user: Dict mapping matrix index -> student_id
        """
        # Get unique users
        all_users = set()
        for c in collaborations:
            all_users.add(c['student_a'])
            all_users.add(c['student_b'])
        
        # Create mappings
        user_to_idx = {user: idx for idx, user in enumerate(sorted(all_users))}
        idx_to_user = {idx: user for user, idx in user_to_idx.items()}
        
        n = len(all_users)
        matrix = np.zeros((n, n))
        
        # Fill matrix with ratings
        for c in collaborations:
            i = user_to_idx[c['student_a']]
            j = user_to_idx[c['student_b']]
            matrix[i][j] = c['rating']
        
        logger.info(f"Built user-item matrix: {n}x{n} with {len(collaborations)} ratings")
        return matrix, user_to_idx, idx_to_user
    
    def calculate_user_similarity(
        self, 
        matrix: np.ndarray
    ) -> np.ndarray:
        """
        Calculate user-user similarity using cosine similarity
        
        Args:
            matrix: User-item rating matrix
            
        Returns:
            Similarity matrix where sim[i][j] = similarity between user i and user j
        """
        # Handle zero vectors (users with no ratings)
        # Add small epsilon to avoid division by zero
        epsilon = 1e-10
        matrix_normalized = matrix + epsilon
        
        # Cosine similarity between users (rows)
        similarity = cosine_similarity(matrix_normalized)
        
        # Set diagonal to 0 (don't recommend yourself)
        np.fill_diagonal(similarity, 0)
        
        return similarity
    
    def get_collaborative_score(
        self,
        target_user: str,
        candidate_user: str,
        collaborations: List[Dict]
    ) -> float:
        """
        Calculate collaborative filtering score for a candidate peer
        
        Algorithm:
        1. Build user-item matrix
        2. Find users similar to target user
        3. Weight candidate's average rating by similarity of users who rated them
        
        Args:
            target_user: Student ID seeking matches
            candidate_user: Student ID being evaluated
            collaborations: All collaboration data
            
        Returns:
            Collaborative score (0-1 scale, normalized from 1-5 ratings)
        """
        if not collaborations or len(collaborations) < 3:
            return 0.0  # Not enough data
        
        matrix, user_to_idx, idx_to_user = self.build_user_item_matrix(collaborations)
        
        if target_user not in user_to_idx or candidate_user not in user_to_idx:
            return 0.0
        
        target_idx = user_to_idx[target_user]
        candidate_idx = user_to_idx[candidate_user]
        
        # Calculate user similarities
        similarity_matrix = self.calculate_user_similarity(matrix)
        
        # Get similar users to target (excluding target themselves)
        similar_users = similarity_matrix[target_idx]
        
        # Find users who have rated the candidate
        rated_candidate = matrix[:, candidate_idx] > 0
        
        if not np.any(rated_candidate):
            return 0.0  # No one has rated this candidate
        
        # Weighted average: ratings weighted by similarity to target user
        weighted_sum = 0.0
        similarity_sum = 0.0
        
        for i in range(len(similar_users)):
            if rated_candidate[i] and i != target_idx:
                weighted_sum += similar_users[i] * matrix[i][candidate_idx]
                similarity_sum += abs(similar_users[i])
        
        if similarity_sum == 0:
            # Fallback to simple average
            return np.mean(matrix[rated_candidate, candidate_idx]) / 5.0
        
        predicted_rating = weighted_sum / similarity_sum
        
        # Normalize to 0-1 scale (from 1-5 scale)
        normalized_score = max(0.0, min(1.0, (predicted_rating - 1.0) / 4.0))
        
        logger.debug(f"CF score for {target_user} -> {candidate_user}: {normalized_score:.3f}")
        return normalized_score
    
    def get_top_collaborative_matches(
        self,
        target_user: str,
        all_users: List[str],
        collaborations: List[Dict],
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Get top K matches based purely on collaborative filtering
        
        Args:
            target_user: Student ID seeking matches
            all_users: List of all student IDs to consider
            collaborations: All collaboration data
            top_k: Number of top matches to return
            
        Returns:
            List of (student_id, score) tuples sorted by score
        """
        scores = []
        
        for candidate in all_users:
            if candidate == target_user:
                continue
            
            score = self.get_collaborative_score(target_user, candidate, collaborations)
            scores.append((candidate, score))
        
        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]


# Initialize service
cf_service = CollaborativeFilterService()
