"""
File: weaviate.py
Module: app.api.routes

Description:
------------
FastAPI routes for interacting with the Weaviate vector database. These endpoints
support adding vectors, performing searches, and managing the schema.
"""

from fastapi import APIRouter
from app.services.weaviate_service import WeaviateService
from app.models.add_vectors_request import AddVectorsRequest
from app.models.search_vectors_request import SearchVectorsRequest
from app.core.config import config

router = APIRouter()

# Initialize WeaviateService
weaviate_service = WeaviateService(host=config.WEAVIATE_HOST, api_key=config.WEAVIATE_API_KEY)

@router.post("/weaviate/add")
async def add_vector(data: AddVectorsRequest):
    """
    Add a vector to the Weaviate database.
    """
    weaviate_service.add_vector(data.id, data.text, data.embedding)
    return {"status": "success", "message": f"Vector with ID {data.id} added to Weaviate."}

@router.post("/weaviate/search")
async def search_vectors(data: SearchVectorsRequest):
    """
    Perform a vector similarity search in the Weaviate database.
    """
    results = weaviate_service.search_vectors(data.query_vector, data.k)
    return {"results": results}

@router.post("/weaviate/schema")
async def create_schema():
    """
    Create the schema for the Weaviate database.
    """
    weaviate_service.create_schema()
    return {"status": "success", "message": "Weaviate schema created."}
