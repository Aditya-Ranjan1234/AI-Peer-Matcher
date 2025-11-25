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
    load_dotenv()
except ImportError:
    pass

MONGODB_URL = os.getenv("MONGODB_URL")
if not MONGODB_URL:
    raise RuntimeError("MONGODB_URL environment variable is not set. Set it in a .env file or in the deployment environment.")

# Create a single client instance that will be reused across requests.
client = AsyncIOMotorClient(MONGODB_URL)

# ``get_default_database`` extracts the database name from the URI.
_db = client.get_default_database()

def get_db():
    """FastAPI dependency that returns the MongoDB database.

    Usage in an endpoint::

        async def endpoint(db = Depends(get_db)):
            collection = db["profiles"]
            ...
    """
    return _db
