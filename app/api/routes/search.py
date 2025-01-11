# Search Route (app/api/routes/search.py)
# Handles vector similarity searches.
from fastapi import APIRouter, HTTPException
from app.models.search_vectors_request import SearchVectorsRequest
from app.core.db_init import initialize_vectordb_service
import numpy as np
import logging

# Logger for this file
logger = logging.getLogger(__name__)

router = APIRouter()

# Create and initialize the vectordb service
vectordb_service = initialize_vectordb_service()

@router.post("/search")
async def search_vectors(data: SearchVectorsRequest):
    """
    Perform a similarity search in the vector database.
    """
    try:
        logger.debug(f"search_vectors called")

        # Validate the embedding dimension
        if len(data.query_vector) != vectordb_service.faiss_db.embedding_dim:
            raise HTTPException(status_code=400, detail="Embedding dimension mismatch")

        # Search vectors
        raw_results = vectordb_service.search_vectors(data.query_vector, data.top_k)

        # Convert results to JSON-serializable format
        results = [
            {
                "id": int(result["id"]),
                "distance": float(result["distance"]),
                "metadata": result["metadata"]
            }
            for result in raw_results
        ]

        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))