import logging
import re
from typing import List, Set, Dict

logger = logging.getLogger(__name__)

class KnowledgeGraphService:
    """
    Service for Graph-based skill matching.
    Uses an ontology of skills to determine structural similarity.
    """
    
    # Simple Ontology: Maps specific skills to their parent categories and related concepts
    ONTOLOGY = {
        # Web Development
        "fastapi": {"web development", "backend", "python", "api"},
        "django": {"web development", "backend", "python"},
        "flask": {"web development", "backend", "python"},
        "react": {"web development", "frontend", "javascript"},
        "node.js": {"web development", "backend", "javascript"},
        "javascript": {"programming", "frontend", "web development"},
        "html": {"web development", "frontend"},
        "css": {"web development", "frontend"},
        
        # Programming Languages
        "python": {"programming", "data science", "ai", "backend"},
        "c++": {"programming", "system programming"},
        "java": {"programming", "backend", "enterprise"},
        "c": {"programming", "system programming"},
        
        # AI & Data Science
        "machine learning": {"ai", "data science", "statistics", "mathematics"},
        "deep learning": {"ai", "machine learning", "neural networks"},
        "data science": {"ai", "statistics", "programming", "data analysis"},
        "statistics": {"mathematics", "data science"},
        "neural networks": {"ai", "deep learning"},
        
        # Core Engineering & Science
        "mathematics": {"science", "engineering"},
        "physics": {"science", "engineering"},
        "chemistry": {"science"},
        "biology": {"science"},
        
        # General Categories (Root Nodes)
        "web development": set(),
        "programming": set(),
        "ai": set(),
        "science": set(),
        "engineering": set(),
        "mathematics": set(),
        "backend": {"web development"},
        "frontend": {"web development"}
    }

    def _extract_entities(self, text: str) -> Set[str]:
        """Simple keyword-based entity extraction from text."""
        if not text:
            return set()
        
        found = set()
        text_lower = text.lower()
        
        # Check for each key in ontology using regex for word boundaries
        for skill in self.ONTOLOGY.keys():
            # Escape skill for regex (e.g. c++)
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found.add(skill)
        
        return found

    def _expand_nodes(self, nodes: Set[str]) -> Set[str]:
        """Expand found nodes to include their parent categories from ontology."""
        expanded = set(nodes)
        for node in nodes:
            if node in self.ONTOLOGY:
                expanded.update(self.ONTOLOGY[node])
                # Go one level deeper for root categories if needed
                for parent in self.ONTOLOGY[node]:
                    if parent in self.ONTOLOGY:
                        expanded.update(self.ONTOLOGY[parent])
        return expanded

    def calculate_graph_score(self, text_a: str, text_b: str) -> float:
        """
        Calculate Jaccard similarity between expanded sets of graph nodes.
        Higher overlap in concepts = higher score.
        """
        entities_a = self._extract_entities(text_a)
        entities_b = self._extract_entities(text_b)
        
        if not entities_a or not entities_b:
            return 0.0
            
        nodes_a = self._expand_nodes(entities_a)
        nodes_b = self._expand_nodes(entities_b)
        
        intersection = nodes_a.intersection(nodes_b)
        union = nodes_a.union(nodes_b)
        
        if not union:
            return 0.0
            
        return len(intersection) / len(union)

    def get_complementary_graph_score(self, profile_a: Dict, profile_b: Dict) -> float:
        """
        Calculate how well A's strengths help B's weaknesses (Graph-based).
        """
        # Direction 1: A strengths (A has it) matches B weaknesses (B needs it)
        score_1 = self.calculate_graph_score(profile_a.get("strengths", ""), profile_b.get("weaknesses", ""))
        
        # Direction 2: B strengths (B has it) matches A weaknesses (A needs it)
        score_2 = self.calculate_graph_score(profile_b.get("strengths", ""), profile_a.get("weaknesses", ""))
        
        return (score_1 + score_2) / 2.0
