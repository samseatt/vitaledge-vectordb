# app/api/routes/vectors.py

import numpy as np
from fastapi import APIRouter
from typing import List
from app.models.add_vectors_request import AddVectorsRequest
from app.models.delete_vectors_request import DeleteVectorsRequest
from app.models.search_vectors_request import SearchVectorsRequest
from app.services.vectordb import FaissService

router = APIRouter()

faiss_service = FaissService()

@router.post("/add")
async def add_vectors(data: AddVectorsRequest):
    """
    Add a single vector to the vector database.
    """
    # Convert the single vector into an array with one element
    embedding = np.array([data.embedding], dtype=np.float32)
    faiss_service.add_vectors(embedding, [data.id])
    return {"status": "success", "message": f"Vector with ID {data.id} added successfully."}

"""
Delete Vectors
Route: /vectors/delete
Method: POST
Purpose: Delete specific vectors from the database by their IDs.
[Stubbed out for future use]
"""
@router.post("/delete")
async def delete_vectors(data: DeleteVectorsRequest):
    """
    Delete vectors from the vector database by their IDs.
    """
    faiss_service.delete_vectors(data.vector_ids)
    return {"status": "success", "deleted_count": len(data.vector_ids)}

"""
Update Vector
Route: /vectors/update
Method: POST
Purpose: Update an existing vector by providing its new embedding and ID.
[Stub]
"""
@router.post("/update")
async def update_vector(vector_id: int, new_embedding: List[float]):
    """
    Update an existing vector in the database.
    """
    faiss_service.update_vector(vector_id, new_embedding)
    return {"status": "success", "message": f"Vector with ID {vector_id} updated successfully."}


"""
Get Vector by ID
Route: /vectors/get
Method: GET
Purpose: Retrieve a vector from the database by its ID.
[Stub]
"""
@router.get("/get/{vector_id}")
async def get_vector(vector_id: int):
    """
    Retrieve a vector by its ID.
    """
    vector = faiss_service.get_vector(vector_id)
    return {"vector_id": vector_id, "embedding": vector.tolist()}

"""
Bulk Search
Route: /bulk_search
Method: POST
Purpose: Perform multiple vector similarity searches at once.
[Stub]
"""
@router.post("/bulk_search")
async def bulk_search_vectors(queries: List[SearchVectorsRequest]):
    """
    Perform bulk similarity searches in the vector database.
    """
    results = [faiss_service.search_vectors(np.array([query.query_vector], dtype=np.float32), query.k) for query in queries]
    return {"results": results}

"""
Export Vectors
Route: /vectors/export
Method: GET
Purpose: Export all vectors and their IDs for backup or migration.
[Stub]
"""
@router.get("/export")
async def export_vectors():
    """
    Export all vectors and their IDs.
    """
    vectors = faiss_service.export_vectors()
    return {"vectors": vectors}

"""
Import Vectors
Route: /vectors/import
Method: POST
Purpose: Import vectors and their IDs from a backup.
[Stub]
"""
@router.post("/import")
async def import_vectors(vectors: List[dict]):
    """
    Import vectors and their IDs into the database.
    """
    faiss_service.import_vectors(vectors)
    return {"status": "success", "imported_count": len(vectors)}


# from fastapi import APIRouter
# from app.models.add_vectors_request import AddVectorsRequest
# from app.models.search_vectors_request import SearchVectorsRequest
# from app.services.vectordb import FaissService
# from app.core.faiss_db import FaissDB
# from app.core.config import config
# import numpy as np

# router = APIRouter()

# # Load FaissDB
# faiss_db = FaissDB(config.VECTOR_DB_PATH, config.EMBEDDING_DIM)
# faiss_service = FaissService()

# # @router.post("/add")
# # async def add_vectors(data: AddVectorsRequest):
# #     vectors = np.array(data.vectors)
# #     ids = np.array(data.ids)
# #     faiss_service.add_vectors(vectors, ids)
# #     return {"status": "success"}

# @router.post("/add")
# async def add_vectors(data: AddVectorsRequest):
#     faiss_service.add_vectors([data.embedding], [data.id])
#     return {"status": "success", "message": f"Vector with ID {data.id} added successfully."}

# @router.post("/search")
# async def search_vectors(data: SearchVectorsRequest):
#     query_vector = np.array(data.query_vector)
#     distances, indices = faiss_service.search_vectors(query_vector, data.k)
#     return {"distances": distances.tolist(), "indices": indices.tolist()}
