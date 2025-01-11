# Admin Route (app/api/routes/admin.py)
# Provides health checks.
from fastapi import APIRouter, HTTPException
from app.models.search_vectors_request import SearchVectorsRequest
from app.core.db_init import initialize_vectordb_service
from typing import Optional
import numpy as np
import logging

# Logger for this file
logger = logging.getLogger(__name__)

router = APIRouter()

# Create and initialize the vectordb service
vectordb_service = initialize_vectordb_service()

@router.get("/vectors")
async def list_vectors(category: Optional[str] = None):
    """
    List all vectors (metadata) with optional filtering by category.
    """
    vectors = vectordb_service.list_vectors(category)
    return {"vectors": vectors}

@router.get("/tags")
async def list_tags():
    """
    List all tags in the database.
    """
    tags = vectordb_service.list_tags()
    return {"tags": tags}


@router.get("/peek/vectordb")
async def peek_vectordb():
    """
    Peek inside the Faiss vector database.
    """
    try:
        # Get all stored vectors and their metadata
        all_vectors = vectordb_service.faiss_db.get_all_vectors()
        return {"status": "success", "data": all_vectors}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/peek/sqlite")
async def peek_sqlite():
    """
    Peek inside the SQLite metadata database.
    """
    try:
        # Fetch all metadata entries from SQLite
        all_metadata = vectordb_service.sqlite_db.get_all_metadata()
        return {"status": "success", "data": all_metadata}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/embedding/{vector_id}")
async def get_embedding(vector_id: int):
    """
    Get the requested embedding if exists.
    """
    try:
        # Ensure vector_id is explicitly converted to an integer
        vector_id = int(vector_id)

        logger.info(f"Endpoint /admin/embedding called with id {vector_id}")
        
        # Pass the correct vector_id to the service
        embedding = vectordb_service.get_vector(vector_id)

        logger.debug(f"Received embedding {embedding}")
        # Ensure embedding is converted to a JSON-serializable format
        if embedding is not None:
            embedding = embedding.tolist()
            return {"status": "success", "id": vector_id, "embedding": embedding}
        else:
            return {"status": "not found"}

    except ValueError:
        logger.error(f"Invalid vector_id provided: {vector_id}")
        raise HTTPException(status_code=400, detail="Vector ID must be an integer.")
    except Exception as e:
        logger.error(f"Error while retrieving embedding for vector ID {vector_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    

"""
Reset Database
Route: /admin/reset
Method: POST
Purpose: Clear all data from the vector database (admin-only operation).
[Stub] NOT IMPLEMENTED
"""
@router.post("/reset")
async def reset_database():
    """
    Reset the vector database by clearing all data.
    """
    vectordb_service.reset_database()
    return {"status": "success", "message": "Vector database reset successfully."}


"""
Health Check
Route: /admin/health
Method: GET
Purpose: Check the status of the vector database service.
[Stub] NOT IMPLEMENTED
"""
@router.get("/health")
async def health_check():
    """
    Check the health of the vector database service.
    """
    is_healthy = vectordb_service.check_health()
    return {"status": "healthy" if is_healthy else "unhealthy"}

"""
Get Metadata
Route: /admin/metadata
Method: GET
Purpose: Retrieve metadata about the vector database (e.g., number of vectors, embedding dimension).
[Stub] NOT IMPLEMENTED
"""
@router.get("/metadata")
async def get_metadata():
    """
    Retrieve metadata about the vector database.
    """
    metadata = vectordb_service.get_metadata()
    return {"metadata": metadata}

"""
[Stub] NOT IMPLEMENTED
"""
@router.get("/list")
async def list_vectors():
    try:
        vectors = vectordb_service.list_all_vectors()
        return {"status": "success", "vectors": vectors}
    except Exception as e:
        logger.exception("Failed to list vectors")
        return {"status": "error", "message": str(e)}
