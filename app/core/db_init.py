from app.core.faiss_db import FaissDB
from app.core.sqlite_db import SQLiteDB
from app.services.vectordb import VectorDBService
from app.core.config import config

def initialize_vectordb_service():
    """
    Initialize and return the VectorDBService instance.
    """
    faiss_db = FaissDB(config.VECTOR_DB_PATH, config.EMBEDDING_DIM)
    sqlite_db = SQLiteDB(config.SQLITE_DB_PATH)
    return VectorDBService(faiss_db, sqlite_db)
