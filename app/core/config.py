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

    class Config:
        env_file = ".env"

config = Config()


# TODO Switch to this when using Weaviate cloud
# class Config(BaseSettings):
#     WEAVIATE_HOST: str = "http://localhost:8080"
#     WEAVIATE_API_KEY: str = ""

# config = Config()
