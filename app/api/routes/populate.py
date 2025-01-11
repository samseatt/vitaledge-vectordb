# Populate Route (app/api/routes/populate.py)
# Allows bulk population of embeddings.

from fastapi import APIRouter, HTTPException
from typing import List
from app.core.db_init import initialize_vectordb_service
from app.core.config import config
import numpy as np
import logging

# Logger for this file
logger = logging.getLogger(__name__)

router = APIRouter()

# Create and initialize the vectordb service
vectordb_service = initialize_vectordb_service()

@router.post("/populate")
async def populate_vectors(documents: List[dict]):
    """
    Bulk insertion of embeddings and metadata into the vector database.
    Each document should have 'id', 'embedding', 'text', 'category', and 'tags' fields.
    """
    try:
        logger.info(f"Calling populate_vectors endpoint with {len(documents)} documents")
        embeddings = [doc["embedding"] for doc in documents]
        ids = [doc["id"] for doc in documents]
        texts = [doc["text"] for doc in documents]
        categories = [doc.get("category") for doc in documents]
        tags_list = [doc.get("tags", []) for doc in documents]  # Default to empty list if tags are missing

        # Add vectors and metadata to the database
        for i in range(len(ids)):
            logger.debug(f"Calling vectordb_service.add_vector for document {i}")
            vectordb_service.add_vector(
                embeddings[i],
                texts[i],
                ids[i],
                categories[i],
                tags_list[i]
            )

        return {"status": "success", "indexed_count": len(ids)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
