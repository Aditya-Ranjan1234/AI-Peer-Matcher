"""MongoDB connection helper for the AI Peer Matcher backend.

Provides a FastAPI‑compatible dependency that returns a reference to the
MongoDB database (or collection) using the async Motor driver.
The connection string is read from the environment variable ``MONGODB_URL``.
"""

import os
from motor.motor_asyncio import AsyncIOMotorClient

# Load .env if present (python-dotenv is in requirements)
try:
    from dotenv import load_dotenv
    # Load .env from parent directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(base_dir, '.env')
    load_dotenv(env_path)
except ImportError:
    pass

MONGODB_URL = os.getenv("MONGODB_URL")
if not MONGODB_URL:
    raise RuntimeError("MONGODB_URL environment variable is not set. Set it in a .env file or in the deployment environment.")

print(f"DEBUG: Backend loaded MONGODB_URL: {MONGODB_URL.split('@')[-1] if '@' in MONGODB_URL else 'localhost/redacted'}")

# Create a single client instance that will be reused across requests.
client = AsyncIOMotorClient(MONGODB_URL)

# Use an explicit database name
_db = client["peer_matcher"]

def get_db():
    """FastAPI dependency that returns the MongoDB database.

    Usage in an endpoint::

        async def endpoint(db = Depends(get_db)):
            collection = db["profiles"]
            ...
    """
    return _db
