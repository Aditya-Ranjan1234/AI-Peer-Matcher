from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URL"))
db = client.peer_matcher
projects = db.projects

p = projects.find_one({"title": "Sustainable Packaging Prototype"})
if p:
    print(f"Title: {p.get('title')}")
    print(f"Description: {p.get('description')}")
    print(f"Stack: {p.get('stack')}")
else:
    print("Project not found")
