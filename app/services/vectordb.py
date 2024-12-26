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
from app.core.faiss_db import FaissDB
from app.core.config import config

class FaissService:
    def __init__(self):
        self.faiss_db = FaissDB(config.VECTOR_DB_PATH, config.EMBEDDING_DIM)

    def add_vectors(self, embeddings: np.ndarray, ids: list, texts: str):
        """
        Add vectors to the database.
        """
        self.faiss_db.add_embeddings(embeddings, ids, texts)

    def search_vectors(self, query_vector: np.ndarray, top_k: int):
        """
        Search the database for the nearest neighbors.
        """
        return self.faiss_db.search(query_vector, top_k)

    def delete_vectors(self, ids: list):
        """
        Delete vectors to the database.
        """
        self.faiss_db.delete_vectors(ids)



# import faiss
# import os
# import numpy as np

# # Configuration for Faiss index
# INDEX_PATH = "data/faiss_index.idx"
# VECTOR_DIM = 384  # Example for all-MiniLM-L6-v2
# USE_GPU = False  # Update to True if GPU is available

# class FaissService:
#     def __init__(self):
#         # Initialize Faiss index
#         # self.index = None
#         # self.load_index()
#         self.dimension = 384  # Replace with the actual dimension of your embeddings
#         index = faiss.IndexFlatL2(self.dimension)
#         self.index = faiss.IndexIDMap(index)  # Wrap it to allow ID assignment
        
#     def create_index(self):
#         """Create a new Faiss index."""
#         if USE_GPU:
#             res = faiss.StandardGpuResources()
#             self.index = faiss.index_factory(VECTOR_DIM, "Flat", faiss.METRIC_INNER_PRODUCT)
#             self.index = faiss.index_cpu_to_gpu(res, 0, self.index)
#         else:
#             self.index = faiss.IndexFlatIP(VECTOR_DIM)

#     def add_vectors(self, vectors: np.ndarray, ids: np.ndarray):
#         """Add vectors with IDs to the index."""
#         if self.index is None:
#             self.create_index()
#         self.index.add_with_ids(vectors, ids)
#         self.save_index()

#     def search_vectors(self, query_vector: np.ndarray, k: int = 5):
#         """Search for the nearest neighbors to a query vector."""
#         if self.index is None:
#             raise ValueError("Index is not initialized.")
#         distances, indices = self.index.search(query_vector, k)
#         return distances, indices

#     def save_index(self):
#         """Save the Faiss index to disk."""
#         if self.index is not None:
#             faiss.write_index(self.index, INDEX_PATH)

#     def load_index(self):
#         """Load the Faiss index from disk."""
#         if os.path.exists(INDEX_PATH):
#             self.index = faiss.read_index(INDEX_PATH)
#         else:
#             self.create_index()
