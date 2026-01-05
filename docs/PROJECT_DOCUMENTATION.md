# AI Peer Matcher & Project Hub - Technical Report

## 1. Project Overview
The **AI Peer Matcher** is an intelligent platform designed to facilitate peer learning and project collaboration among students. It uses Natural Language Processing (NLP) to analyze student skills and project requirements, creating optimal matches that foster complementary learning environments.

## 2. Core Architecture
The system follows a modern decoupled architecture:
- **Frontend**: A responsive web interface built with Vanilla JavaScript and CSS, optimized for high performance and visual excellence.
- **Backend**: A high-performance asynchronous API built with **FastAPI**.
- **Database**: **MongoDB Atlas**, used for persistent storage of user profiles, authentication data, and project postings.
- **ML Engine**: **Sentence Transformers** (`all-MiniLM-L6-v2`) integrated directly into the backend for real-time semantic analysis.

## 3. How Matching Works
The matching system is built on the concept of **Complementary Skill Alignment**. 

### Semantic Embeddings
Instead of simple keyword matching, the system converts text into high-dimensional vectors (embeddings) using a pre-trained Transformer model. This allows the system to understand that "Python coding" is semantically similar to "Back-end development".

### Complementary Scoring
This ensure that the pair can effectively help each other fill their knowledge gaps.

### 3.2. Knowledge Graph Matching
While semantic embeddings capture the "vibe" of skills, the **Knowledge Graph (KG)** captures the "structure".

- **Ontology**: A pre-defined hierarchy of skills (e.g., `React` -> `Frontend` -> `Web Development`).
- **Entity Extraction**: Using regex-based NER to identify specific nodes from raw user text.
- **Node Expansion**: When a skill is identified, the system automatically expands it to include its parent and related nodes in the graph.
- **Jaccard Similarity**: The graph score is calculated based on the intersection vs. union of expanded node sets from two users.

This allows the system to match a "React Developer" with a "Web Design" student even if their text embeddings are slightly different.

## 4. Team Formation (Teams of 4)
The system supports two modes of team formation:

### Dynamic Greedy Partitioning
For general users, the system uses a greedy algorithm:
1. Start with the requesting user.
2. Iteratively find the next user who maximizes the average complementary score with all existing team members.
3. Repeat until a team of 4 is formed.

### Optimized Fixed Partitioning
For specific high-priority user groups, the system supports **Pre-calculated Optimal Partitions**:
- **Algorithm**: A recursive brute-force search that explores all possible combinations of a user set (e.g., 12 users into 3 teams) to maximize the **Global Complementary Score**.
- **Enforcement**: These partitions are saved in `fixed_teams.json` and enforced by the backend to guarantee the absolute best possible outcome for those individuals.

## 5. Project Relevance Scoring
The Project Hub doesn't just list projects; it ranks them based on individual fit.
- **AI Relevance**: Cosine similarity between user strengths and project description.
- **Graph Relevance**: Concept overlap between user skills and project stack.
- **Dual Display**: Users see both an "AI %" and a "Graph %", highlighting projects that are both contextually and technically relevant.

## 6. Technical Stack Details
- **FastAPI**: Used for its speed and native support for asynchronous MongoDB operations (via Motor).
- **Sentence Transformers**: `all-MiniLM-L6-v2` produces 384-dimensional vectors that capture deep semantic meaning.
- **Cosine Similarity**: The core mathematical metric used to compare embedding vectors.
- **MongoDB**: Schema-less nature allows for flexible profile data while maintaining fast query performance.
