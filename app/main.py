# Main File (app/main.py)
# Defines the FastAPI app and includes routes.

from fastapi import FastAPI
from app.api.routes.populate import router as populate_router
from app.api.routes.search import router as search_router
from app.api.routes.admin import router as admin_router
from app.utils.logging import setup_logging

# Set up logging for the application
setup_logging(log_level="DEBUG", log_file="logs/vitaledge_vectordb.log")

app = FastAPI(
    title="VitalEdge VectorDB",
    description="A microservice for managing vector databases for embeddings.",
    version="1.0.0",
)

# Register routes
app.include_router(populate_router, prefix="/populate", tags=["Populate"])
app.include_router(search_router, prefix="/search", tags=["Search"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])
