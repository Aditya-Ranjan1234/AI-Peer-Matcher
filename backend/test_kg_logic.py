from knowledge_graph import KnowledgeGraphService

kg = KnowledgeGraphService()

user_strengths = "Mathematics, Physics, Chemistry, Biology, Environmental Science, Statistics, Problem Solving, Critical Thinking"
project_text = "Sustainable Packaging Prototype Create an eco-friendly packaging alternative using biodegradable materials. Product Design, Sustainability, Material Research"

e_user = kg._extract_entities(user_strengths)
e_proj = kg._extract_entities(project_text)

print(f"User Entities: {e_user}")
print(f"Project Entities: {e_proj}")

n_user = kg._expand_nodes(e_user)
n_proj = kg._expand_nodes(e_proj)

print(f"User Expanded: {n_user}")
print(f"Project Expanded: {n_proj}")

score = kg.calculate_graph_score(user_strengths, project_text)
print(f"Final Score: {score}")

intersection = n_user.intersection(n_proj)
union = n_user.union(n_proj)
print(f"Intersection: {intersection}")
print(f"Union: {union}")
