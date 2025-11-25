# backend/database.py
"""MongoDB connection helper for the AI Peer Matcher backend.

Provides a FastAPI‑compatible dependency that returns a reference to the
MongoDB database (or collection) using the async Motor driver.
The connection string is read from the environment variable ``MONGODB_URL``
which you have already added to Render's environment.
"""

import os
from motor.motor_asyncio import AsyncIOMotorClient

# Retrieve the connection string from the environment. Render will inject it.
MONGODB_URL = os.getenv("MONGODB_URL")
if not MONGODB_URL:
    raise RuntimeError("MONGODB_URL environment variable is not set. Please configure it in Render.")

# Create a single client instance that will be reused across requests.
client = AsyncIOMotorClient(MONGODB_URL)

# ``get_default_database`` extracts the database name from the URI.
# If the URI does not contain a database name, you can replace this with
# ``client["my_database"]``.
_db = client.get_default_database()

def get_db():
    """FastAPI dependency that returns the MongoDB database.

    Usage in an endpoint::

        async def endpoint(db = Depends(get_db)):
            collection = db["profiles"]
            ...
    """
    return _db
