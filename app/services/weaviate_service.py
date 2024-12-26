"""
File: weaviate_service.py
Module: app.services

Description:
------------
Service module for interfacing with the Weaviate database. Provides higher-level
APIs for vector addition, schema management, and search operations.

Dependencies:
-------------
- `app.core.weaviate_db`: Underlying database client wrapper.
"""

from app.core.weaviate_db import WeaviateDB

class WeaviateService:
    """
    Service layer for interacting with Weaviate database.
    """

    def __init__(self, host: str, api_key: str):
        self.db = WeaviateDB(host, api_key)

    def add_vector(self, id: str, text: str, embedding: list):
        self.db.add_vector(id, text, embedding)

    def search_vectors(self, query_vector: list, k: int):
        return self.db.search_vector(query_vector, k)

    def create_schema(self):
        self.db.create_schema()
