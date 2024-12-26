# Search Route (app/api/routes/search.py)
# Handles vector similarity searches.
from fastapi import APIRouter, HTTPException
from app.models.search_vectors_request import SearchVectorsRequest
from app.services.vectordb import FaissService
import numpy as np
import logging

# Logger for this file
logger = logging.getLogger(__name__)

router = APIRouter()

faiss_service = FaissService()

@router.post("/search")
async def search_vectors(data: SearchVectorsRequest):
    """
    Perform a similarity search in the vector database.
    """
    logger.debug(f"search_vectors called")
    if len(data.query_vector) != faiss_service.faiss_db.embedding_dim:
        raise HTTPException(status_code=400, detail="Embedding dimension mismatch")

    query_vector = np.array([data.query_vector], dtype=np.float32)
    results = faiss_service.search_vectors(query_vector, data.top_k)
    logger.debug(f"search_vector route returning results: {results}")

    return {"results": [{"id": int(idx), "score": float(dist), "text": text} for idx, dist, text in results]}



# from fastapi import APIRouter, HTTPException
# from typing import List
# from pydantic import BaseModel
# from app.core.faiss_db import FaissDB
# from app.core.config import config

# import numpy as np

# router = APIRouter()

# class EmbeddingsRequest(BaseModel):
#     query_embedding: List[float]
#     top_k: int = 5

# # Load FaissDB
# faiss_db = FaissDB(config.VECTOR_DB_PATH, config.EMBEDDING_DIM)

# @router.post("/search")
# async def search_vectors(request: EmbeddingsRequest):
#     print(f"search_vectors called")
#     if len(request.query_embedding) != config.EMBEDDING_DIM:
#         raise HTTPException(status_code=400, detail="Embedding dimension mismatch")
    
#     query_embedding_np = np.array([request.query_embedding], dtype=np.float32)
#     results = faiss_db.search(query_embedding_np, request.top_k)

#     return {"results": [{"id": int(idx), "score": float(dist)} for idx, dist in results]}
