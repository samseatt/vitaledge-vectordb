# Admin Route (app/api/routes/admin.py)
# Provides health checks.
from fastapi import APIRouter

router = APIRouter()

# @router.get("/health")
# async def health_check():
#     return {"status": "ok"}

"""
Reset Database
Route: /admin/reset
Method: POST
Purpose: Clear all data from the vector database (admin-only operation).
[Stub]
"""
@router.post("/reset")
async def reset_database():
    """
    Reset the vector database by clearing all data.
    """
    faiss_service.reset_database()
    return {"status": "success", "message": "Vector database reset successfully."}


"""
Health Check
Route: /admin/health
Method: GET
Purpose: Check the status of the vector database service.
[Stub]
"""
@router.get("/health")
async def health_check():
    """
    Check the health of the vector database service.
    """
    is_healthy = faiss_service.check_health()
    return {"status": "healthy" if is_healthy else "unhealthy"}

"""
Get Metadata
Route: /admin/metadata
Method: GET
Purpose: Retrieve metadata about the vector database (e.g., number of vectors, embedding dimension).
[Stub]
"""
@router.get("/metadata")
async def get_metadata():
    """
    Retrieve metadata about the vector database.
    """
    metadata = faiss_service.get_metadata()
    return {"metadata": metadata}


