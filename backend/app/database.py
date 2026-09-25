import os
import certifi
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
backend_env_path = Path(__file__).resolve().parent.parent / ".env"
atlas_env_path = Path(__file__).resolve().parent.parent.parent / "atlas-credentials.env"

if backend_env_path.exists():
    load_dotenv(backend_env_path)
elif atlas_env_path.exists():
    load_dotenv(atlas_env_path)

MONGO_URI = os.getenv(
    "MONGO_URI",
    os.getenv("MONGODB_URI", "mongodb://localhost:27017")
)
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "document_uploader")

_client = None
_db = None
_collection = None

def get_client():
    """Get active MongoDB client, connecting to Atlas or falling back to mongomock if unreachable."""
    global _client, _db, _collection
    if _client is not None:
        return _client

    try:
        kwargs = {"serverSelectionTimeoutMS": 3000}
        if "mongodb+srv://" in MONGO_URI or "tls=true" in MONGO_URI.lower():
            kwargs["tlsCAFile"] = certifi.where()

        candidate_client = MongoClient(MONGO_URI, **kwargs)
        # Verify connection
        candidate_client.admin.command("ping")
        print("[Database] Successfully connected to MongoDB Atlas!")
        _client = candidate_client
        _db = _client[MONGO_DB_NAME]
        _collection = _db["documents"]
        return _client
    except Exception as e:
        print(f"[Database] Atlas connection not available ({e}). Using in-memory MongoDB fallback.")
        import mongomock
        _client = mongomock.MongoClient()
        _db = _client[MONGO_DB_NAME]
        _collection = _db["documents"]
        return _client

def get_db():
    get_client()
    return _db

def get_documents_collection():
    get_client()
    return _collection

def serialize_doc(doc: dict) -> dict:
    """Convert MongoDB document to JSON-serializable dictionary."""
    if not doc:
        return doc
    doc_dict = dict(doc)
    if "_id" in doc_dict:
        doc_dict["_id"] = str(doc_dict["_id"])
    return doc_dict
