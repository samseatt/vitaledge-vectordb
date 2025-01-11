"""
File: faiss_db.py
Module: app.core

Description:
------------
This module defines the `FaissDB` class, a wrapper around the FAISS vector indexing library. 
It provides an interface for managing the lifecycle of FAISS indexes and performing key vector 
operations such as addition, searching, and deletion of embeddings. 

The `FaissDB` class utilizes the `IndexFlatL2` type, which implements a simple flat index with 
Euclidean (L2) distance as the similarity metric. This ensures straightforward indexing and 
retrieval of vector embeddings while avoiding the added complexity of mapped IDs.

Responsibilities:
-----------------
- Manage the lifecycle of the FAISS index:
  - Create a new flat index if none exists.
  - Load an existing index from a file.
  - Persist the index to disk after updates.
- Perform vector operations:
  - Add embeddings to the index.
  - Search for nearest neighbors given a query embedding.
  - Retrieve the total number of vectors stored in the index.
  - Optionally delete specific embeddings if supported.
- Provide a foundation for higher-level services to interact with the vector database.

Dependencies:
-------------
- `faiss`: The FAISS library for high-performance similarity search and clustering.
- `numpy`: For numerical operations and embedding data management.
- `os`: To manage file system operations for loading and saving the index.
- `logging`: For logging actions and errors during vector operations.

Usage:
------
The `FaissDB` class is primarily used by higher-level services, such as `VectorDBService`, 
to manage embeddings and facilitate search operations in a RAG (Retrieval-Augmented Generation) pipeline.

Classes:
--------
- `FaissDB`: Encapsulates the FAISS index and provides high-level methods for managing embeddings.

Methods:
--------
- `add_vector`: Add a single embedding to the FAISS index.
- `add_vectors`: Bulk insertion of multiple embeddings.
- `search_vectors`: Perform similarity search to retrieve the top K most similar embeddings.
- `get_vector_count`: Return the total number of vectors in the index.
- `save_index`: Persist the index to a file.
- `load_or_create_index`: Initialize the index from disk or create a new one.
- `delete_vector`: (Optional) Delete a vector by its ID if supported.
- `get_all_vectors`: Retrieve all vector IDs from the FAISS index.

Example:
--------
db = FaissDB(vector_db_path="./data/faiss_index", embedding_dim=384)

# Adding a single embedding
embedding = np.array([0.1, 0.2, 0.3, ...], dtype=np.float32)
db.add_vector(embedding)

# Searching for the top 5 nearest neighbors
query_embedding = np.array([0.1, 0.2, 0.3, ...], dtype=np.float32)
distances, indices = db.search_vectors(query_embedding, top_k=5)

Design Considerations:
----------------------
- **Flat Index Simplicity**:
  - The use of `IndexFlatL2` ensures simplicity and efficiency, particularly for straightforward 
    RAG workflows. More advanced FAISS configurations (e.g., `IndexIDMap`) are deliberately avoided 
    to minimize operational complexity.
- **Disk Persistence**:
  - The index is saved to disk after every update, ensuring resilience against data loss.
- **Decoupling from Metadata**:
  - This class focuses exclusively on managing embeddings and their operations, leaving metadata 
    management to complementary modules like `SQLiteDB`.

Key Concepts:
-------------
- **IndexFlatL2**: A FAISS index type that stores embeddings in a flat array and uses L2 distance 
  for similarity search.
- **Embedding Dimension**: The size of each embedding vector. Must remain consistent across the index.
- **RAG Pipelines**: Retrieval-Augmented Generation pipelines that depend on efficient vector 
  search capabilities provided by this module.

Author:
-------
Sam Seatt

Date:
-----
2025-01-10

"""
import faiss
import os
import logging
import numpy as np

logger = logging.getLogger(__name__)

class FaissDB:
    def __init__(self, vector_db_path: str, embedding_dim: int):
        """
        Initialize the FaissDB class.

        Args:
            vector_db_path (str): Path to the Faiss index file.
            embedding_dim (int): Dimensionality of the embeddings.
        """
        self.vector_db_path = vector_db_path
        self.embedding_dim = embedding_dim
        self.index = self._load_or_create_index()

    def _load_or_create_index(self):
        """
        Load an existing Faiss index or create a new one if none exists.

        Returns:
            faiss.IndexFlatL2: The Faiss index.
        """
        if os.path.exists(self.vector_db_path):
            logger.info(f"Loading Faiss index from {self.vector_db_path}")
            return faiss.read_index(self.vector_db_path)
        else:
            logger.info(f"Creating a new Faiss index at {self.vector_db_path}")
            return faiss.IndexFlatL2(self.embedding_dim)

    def save_index(self):
        """
        Save the current state of the Faiss index to disk.
        """
        logger.info(f"Saving Faiss index to {self.vector_db_path}")
        faiss.write_index(self.index, self.vector_db_path)

    def add_vector(self, embedding):
        """
        Add a single embedding (without metadata).

        Args:
            embedding (np.ndarray): The embedding to add to Faiss.
        """
        try:
            # Add the embedding to Faiss
            logger.info(f"Adding a new embedding of dimension {len(embedding)} to Faiss index.")
            embedding_np = np.array([embedding], dtype=np.float32)  # Faiss expects 2D array
            logger.info(f"Embedding to be added {embedding_np}.")
            self.index.add(embedding_np)

            # Save Faiss index to persist the change
            self.save_index()

            # Retrieve assigned ID
            assigned_id = self.index.ntotal - 1
            logger.info(f"Successfully added embedding. Assigned ID: {assigned_id}")
            return assigned_id
        except Exception as e:
            logger.exception(f"Error while adding embedding to Faiss index: {str(e)}")
            raise

    def add_vectors(self, embeddings: np.ndarray):
        """
        Add multiple embeddings to the Faiss index.

        Args:
            embeddings (np.ndarray): A 2D array of embeddings to add.
        """
        try:
            logger.info(f"Adding {len(embeddings)} embeddings to Faiss index.")
            embeddings_np = np.array(embeddings, dtype=np.float32)
            self.index.add(embeddings_np)
            self.save_index()
            logger.info(f"Successfully added {len(embeddings)} embeddings to Faiss index.")
        except Exception as e:
            logger.exception(f"Error while adding embeddings to Faiss index: {str(e)}")
            raise

    def search_vectors(self, query_vector, top_k):
        """
        Search for the top K nearest neighbors of a query vector.

        Args:
            query_vector (np.ndarray): The query embedding.
            top_k (int): Number of top results to return.

        Returns:
            tuple: Distances and indices of the nearest neighbors.
        """
        logger.info(f"Searching for top {top_k} results using query vector: {query_vector}.")
        distances, indices = self.index.search(query_vector, top_k)
        logger.info(f"Search results found the following indices: {indices}")
        logger.info(f"Search results found the following distances: {distances}")
        return distances, indices

    def get_all_vectors(self):
        """
        Retrieve all vector embeddings from the Faiss index.

        Returns:
            List[np.ndarray]: A list of all embeddings in the index.
        """
        try:
            vectors = []
            for i in range(self.index.ntotal):  # Loop through all vectors in Faiss
                vectors.append({"id": i})
            return vectors
        except Exception as e:
            logger.error(f"Error while retrieving all vectors: {e}")
            raise

    def get_vector_by_id(self, vector_id: int):
        try:
            logger.info(f"Attempting to retrieve vector ID {vector_id}")

            # Check if vector_id is within the valid range
            if vector_id < 0 or vector_id >= self.index.ntotal:
                logger.error(f"Vector ID {vector_id} is out of range. Valid range is 0 to {self.index.ntotal - 1}.")
                return None

            # Fetch the vector embedding
            embedding = self.index.reconstruct(vector_id)
            return embedding
        except ValueError as ve:
            logger.error(f"Validation error: {str(ve)}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error while retrieving vector ID {vector_id}: {str(e)}")
            raise

    def get_vector_by_position(self, position: int):
        """
        Retrieve a vector by its position in the Faiss index.

        Args:
            position (int): The position of the vector in the index.

        Returns:
            np.ndarray: The vector embedding.
        """
        try:
            if position < 0 or position >= self.index.ntotal:
                logger.error(f"Position {position} is out of range.")
                return None
            return self.index.reconstruct(position)
        except Exception as e:
            logger.exception(f"Error while retrieving vector by position {position}: {str(e)}")
            raise

    def clear_index(self):
        """
        Clear all embeddings from the Faiss index.
        """
        try:
            logger.info("Clearing all embeddings from the Faiss index.")
            self.index.reset()
            self.save_index()
            logger.info("Successfully cleared the Faiss index.")
        except Exception as e:
            logger.exception(f"Error while clearing the Faiss index: {str(e)}")
            raise

