"""
File: weaviate_db.py
Module: app.core

Description:
------------
This module defines the `WeaviateDB` class, a client wrapper for interacting
with the Weaviate cloud-based vector database. It provides basic operations
for schema management, adding objects, and querying vector similarity.

Dependencies:
-------------
- `weaviate-client`: Python client for interacting with Weaviate.
"""

import weaviate

class WeaviateDB:
    """
    Wrapper for Weaviate client operations.
    """

    def __init__(self, host: str, api_key: str):
        self.client = weaviate.Client(
            url=host,
            auth_client_secret=weaviate.AuthApiKey(api_key=api_key)
        )
        self.class_name = "Vector"

    def create_schema(self):
        """
        Create the schema for the vector database.
        """
        schema = {
            "class": self.class_name,
            "properties": [
                {"name": "id", "dataType": ["string"]},
                {"name": "text", "dataType": ["string"]},
                {"name": "embedding", "dataType": ["number[]"]},
            ]
        }
        self.client.schema.create_class(schema)

    def add_vector(self, id: str, text: str, embedding: list):
        """
        Add a vector to the Weaviate database.
        """
        data_object = {
            "id": id,
            "text": text,
            "embedding": embedding,
        }
        self.client.data_object.create(data_object, self.class_name)

    def search_vector(self, query_vector: list, k: int):
        """
        Search for the top-k most similar vectors.
        """
        return self.client.query.get(self.class_name, ["id", "text", "_additional {certainty}"]).with_near_vector(
            {"vector": query_vector}
        ).with_limit(k).do()
