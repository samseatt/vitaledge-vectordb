"""
File: config.py

Description:
------------
Central configuration for the application, including database and vector DB details.
"""

# app/core/config.py
# Manages environment variables and global configurations.
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    VECTOR_DB_PATH: str = "./data/faiss_index"
    EMBEDDING_DIM: int = 384  # For example: all-MiniLM-L6-v2 uses 384 dimensions
    SQLITE_DB_PATH: str = "data/faiss_metadata.sqlite"
    WEAVIATE_URL:str = "http://localhost:8030"
    WEAVIATE_API_KEY:str = ""


    class Config:
        env_file = ".env"

config = Config()

VECTOR_DB_PATH = "data/faiss_index"
SQLITE_DB_PATH = "data/faiss_metadata.sqlite"
EMBEDDING_DIM = 384
WEAVIATE_URL = "http://localhost:8030"
WEAVIATE_API_KEY = None


# TODO Switch to this when using Weaviate cloud
# class Config(BaseSettings):
#     WEAVIATE_HOST: str = "http://localhost:8080"
#     WEAVIATE_API_KEY: str = ""

# config = Config()
