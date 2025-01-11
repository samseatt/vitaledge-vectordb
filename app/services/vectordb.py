"""
File: vectordb.py
Module: app.services

Description:
------------
This module implements the `FaissService` class, which provides a higher-level
abstraction layer for interacting with the FAISS vector database. The service
is designed to support key operations like adding vectors, searching for
similar vectors, and managing the vector index in the database. It serves as
the main interface between the application routes and the underlying FAISS
index.

Responsibilities:
-----------------
- Add vectors to the FAISS index with IDs.
- Perform similarity searches using the FAISS index.
- Act as an intermediary between API routes and the core FAISS database logic.
- Handle any application-specific preprocessing or business logic related to
  vectors and embeddings.

Dependencies:
-------------
- `numpy`: For handling numerical operations and embedding data.
- `faiss`: The FAISS library for managing the vector database.
- `app.core.faiss_db`: The underlying FAISS database implementation.
- `app.core.config`: Provides the configuration values like embedding dimension and index path.

Usage:
------
This module is typically used by API routes to interact with the FAISS vector
database. Example usages include adding new embeddings, searching for similar
vectors, or deleting vectors.

Classes:
--------
- `FaissService`: Encapsulates vector database operations.

Functions:
----------
This module does not define standalone functions; all operations are encapsulated
in the `FaissService` class.

Example:
--------
service = FaissService()
service.add_vectors(embeddings=[[0.1, 0.2, 0.3]], ids=[1])
distances, indices = service.search_vectors(query_vector=[0.1, 0.2, 0.3], k=5)
"""

import numpy as np
from typing import Optional, List
from app.core.faiss_db import FaissDB
from app.core.sqlite_db import SQLiteDB
from app.core.weaviate_db import WeaviateDB
import logging

logger = logging.getLogger(__name__)

class VectorDBService:
    def __init__(self, faiss_db: FaissDB, sqlite_db: SQLiteDB, weaviate_db: WeaviateDB = None):
        self.faiss_db = faiss_db
        self.sqlite_db = sqlite_db
        self.weaviate_db = weaviate_db  # Optional for future use

    def add_vector(self, embedding: list, text: str, external_id: Optional[str] = None, category: Optional[str] = None, tags: List[str] = None) -> int:
        """
        Adds a vector embedding and its metadata.

        Args:
            embedding (list): The embedding to add.
            text (str): Metadata text associated with the embedding.
            external_id (Optional[str]): External identifier for the vector.
            category (Optional[str]): Category of the vector.
            tags (List[str]): Associated tags.

        Returns:
            int: The ID of the added vector.
        """
        try:
            # Add embedding to Faiss and retrieve the assigned embed_id
            logger.info(f"Adding vector metadata to faiss for text: {text}")
            embed_id = self.faiss_db.add_vector(np.array(embedding, dtype=np.float32))

            # Insert metadata into SQLite and retrieve the vector_id
            logger.info(f"Adding vector metadata to sqlite for embedding id: {embed_id}")
            vector_id = self.sqlite_db.add_vector(text, embed_id, external_id, category, tags or [])

            logger.info(f"Vector addition succeeded with vector_id {vector_id}, and embed_id: {embed_id}")
            return vector_id
        except Exception as e:
            logger.exception(f"Error while adding vector: {str(e)}")
            raise

        # logger.info(f"Called add_vector for text: {text}")
        # logger.info(f"Adding vector metadata to sqlite for: {text}")
        # vector_id = self.sqlite_db.add_vector(text, external_id, category, tags or [])
        # logger.info(f"Adding vector metadata to faiss for: {vector_id}")
        # self.faiss_db.add_vector(embedding)
        # logger.info(f"Vector added successfully: {vector_id}")
        # # self.sqlite_db.add_vector(text, external_id, category, tags or [])
        # return vector_id

    """
    Author: Sam Seatt
    List vectors from sqlite
    """
    def list_vectors(self, category: Optional[str] = None):
        return self.sqlite_db.get_vectors(category)

    """
    Author: Sam Seatt
    List all the meta tags in a database
    """
    def list_tags(self):
        return self.sqlite_db.get_tags()
    
    def search_vectors(self, query_vector, top_k: int) -> List[dict]:
        """
        Searches for similar vectors in the Faiss index and retrieves enriched metadata.

        Args:
            query_vector (list): The query embedding.
            top_k (int): Number of top results to return.

        Returns:
            List[dict]: Search results including distances, Faiss IDs, and metadata.
        """
        query_np = np.array([query_vector], dtype=np.float32)
        distances, indices = self.faiss_db.search_vectors(query_np, top_k)
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx == -1:
                continue  # Skip invalid results

            # Retrieve metadata from SQLite
            logger.info(f"Getting metadata form sqlite for id: {idx}")
            metadata = self.sqlite_db.get_metadata(idx)  # Updated to enrich metadata
            results.append({
                "id": idx,  # Faiss ID
                "distance": dist,
                "metadata": metadata  # Enriched with text, external_id, tags
            })

        return results

    def get_vector(self, vector_id: int):
        """
        Service method to retrieve a vector without metadata.
        """
        try:
            logger.info(f"Embedding requested for vector ID {vector_id}")
            embedding = self.faiss_db.get_vector_by_id(vector_id)
            return embedding
        except ValueError as ve:
            raise ve
        except Exception as e:
            raise RuntimeError(f"Error fetching vector {vector_id}: {str(e)}") from e
