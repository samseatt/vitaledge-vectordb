"""
File: faiss_db.py
Module: app.core

Description:
------------
This module defines the `FaissDB` class, which provides a low-level interface
for directly interacting with the FAISS vector database. It is responsible for
managing the lifecycle of the FAISS index, including its creation, loading,
saving, and performing vector operations like addition and searching.

Responsibilities:
-----------------
- Manage the FAISS index lifecycle:
  - Create a new index when none exists.
  - Load an existing index from a file.
  - Save the current state of the index to a file.
- Add embeddings and IDs to the FAISS index.
- Search the FAISS index for similar vectors based on query embeddings.
- Provide low-level vector database functionality for higher-level services.

Dependencies:
-------------
- `faiss`: The FAISS library for managing vector operations.
- `numpy`: For handling numerical operations and embedding data.
- `app.core.config`: Provides configuration values like embedding dimension and
  index file path.

Usage:
------
This module is typically used by higher-level services like `FaissService` to
interact with the FAISS vector database.

Classes:
--------
- `FaissDB`: Handles direct FAISS operations like adding embeddings, searching
  vectors, and saving/loading the index.

Functions:
----------
This module does not define standalone functions; all operations are encapsulated
in the `FaissDB` class.

Example:
--------
db = FaissDB(index_path="./data/faiss_index", embedding_dim=384)
db.add_embeddings(embeddings=np.array([[0.1, 0.2, 0.3]], dtype=np.float32), ids=[1])
results = db.search(query_embedding=np.array([[0.1, 0.2, 0.3]], dtype=np.float32), top_k=5)

Key Concepts:
-------------
- `IndexFlatL2`: A FAISS index type that uses the L2 (Euclidean) distance for
  similarity search.
- `IndexIDMap`: A wrapper around the FAISS index to allow mapping between vector
  embeddings and unique IDs.
- `Embedding Dimension`: The size of the embedding vectors. Must match across
  all vectors in the database.

"""

import faiss
import numpy as np
import pickle
from typing import List, Tuple
import logging

# Logger for this file
logger = logging.getLogger(__name__)

class FaissDB:
    def __init__(self, index_path="./data/faiss_index", embedding_dim=384):
        self.index_path = index_path
        self.embedding_dim = embedding_dim
        self.index = self._load_index()
        self.text_map = {}  # Dictionary to store ID -> text mapping

    def _load_index(self):
        """
        Load the FAISS index from file or initialize a new one if not found.
        """
        try:
            logging.debug(f"Reading FAISS index from {self.index_path}")
            index = faiss.read_index(self.index_path)

            # Ensure the index is wrapped with IndexIDMap
            if not isinstance(index, faiss.IndexIDMap):
                index = faiss.IndexIDMap(index)
                logging.debug("Index wrapped with IndexIDMap.")
            logging.debug(f"Loaded FAISS index of type {type(index)}")

            # Load the text map
            text_map_path = f"{self.index_path}_text_map.pkl"
            with open(text_map_path, "rb") as f:
                self.text_map = pickle.load(f)
            logging.debug(f"Text map loaded from {text_map_path}")

        except Exception:
            # Initialize a new index and empty text map if files don't exist
            index = faiss.IndexFlatL2(self.embedding_dim)
            index = faiss.IndexIDMap(index)
            self.text_map = {}
            logging.debug(f"Initialized new FAISS index with dim {self.embedding_dim} and empty text map")
        return index

    def save_index(self):
        """
        Save the FAISS index to the file system.
        """
        faiss.write_index(self.index, self.index_path)
        logging.debug(f"FAISS index saved to {self.index_path}")

        # Save the text map using pickle
        text_map_path = f"{self.index_path}_text_map.pkl"
        with open(text_map_path, "wb") as f:
            pickle.dump(self.text_map, f)
        logging.debug(f"Text map saved to {text_map_path}")

    def add_embeddings(self, embeddings: np.ndarray, ids: List[int], texts: List[str]):
        """
        Add multiple embeddings and their IDs to the FAISS index.
        """
        if len(embeddings) != len(ids):
            raise ValueError("Number of embeddings and IDs must match.")
        self.index.add_with_ids(embeddings, np.array(ids, dtype=np.int64))
        for id, text in zip(ids, texts):
            self.text_map[id] = text
        self.save_index()
        logging.debug(f"Added {len(ids)} embeddings to the FAISS index.")

    # def search(self, query_embedding: np.ndarray, top_k: int) -> Tuple[np.ndarray, np.ndarray]:
    #     """
    #     Search the FAISS index for the nearest neighbors.
    #     """
    #     return self.index.search(query_embedding, top_k)

    def search(self, query_embedding: np.ndarray, top_k: int) -> List[Tuple[int, float, str]]:
        logging.debug(f"FaissDB.search called with query: {query_embedding}, top_k: {top_k}")
        distances, indices = self.index.search(query_embedding, top_k)
        # vector_search_results = self.index.search(query_embedding, top_k)
        logging.debug(f"FaissDB search returned distances: {distances[0]}, indices: {indices[0]}")

        # Load text_map from pickle file
        text_map_path = f"{self.index_path}_text_map.pkl"
        with open(text_map_path, "rb") as f:
            self.text_map = pickle.load(f)

        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx != -1:
                text = self.text_map.get(idx, "")
                print(f"$$$$$$$$$$$$$$ text read for id {idx} was: {text}")
                results.append((idx, dist, text))
        logging.debug(f"Results obtained: {results}")
        return results

    def delete_vectors(self, ids: list):
        """
        Delete vectors from the FAISS index by their IDs.

        :param ids: List of IDs corresponding to the vectors to be removed.
        """
        if not isinstance(self.index, faiss.IndexIDMap):
            raise RuntimeError("The FAISS index is not wrapped with IndexIDMap.")

        # Convert the list of IDs to a numpy array
        ids_to_remove = np.array(ids, dtype=np.int64)

        # Remove IDs from the index
        self.index.remove_ids(ids_to_remove)
        self.save_index()
        # TODO: Delete texts from pickle text_map too
        logging.debug(f"Deleted {len(ids)} vectors from the FAISS index.")


# # app/core/faiss_db.py
# # Handles Faiss operations like indexing and searching.

# import faiss
# import numpy as np
# from typing import List, Tuple

# # class FaissDB:
# #     def __init__(self, index_path: str, embedding_dim: int):
# #         self.index_path = index_path
# #         self.embedding_dim = embedding_dim
# #         self.index = self._load_index()

# #     def _load_index(self):
# #         try:
# #             print(f"$$$$$$$$$$$$ Reading index with embeddings of {self.embedding_dim}")
# #             index = faiss.read_index(self.index_path)
# #             print(f"$$$$$$$$$$$$ Index read successfully of type {type(index)}")
# #             if not isinstance(index, faiss.IndexIDMap):
# #                 # Wrap it with IndexIDMap if it's not already
# #                 print(f"Index loaded from {self.index_path}, wrapping it with IndexIDMap.")
# #                 index = faiss.IndexIDMap(index)
# #             print(f"Loaded FAISS index of type {type(index)} from {self.index_path}")
# #         except Exception as e:
# #             print(f"Exception {str(e)} occurred")
# #             index = faiss.IndexFlatL2(self.embedding_dim)  # Create a new index
# #             index = faiss.IndexIDMap(index)  # Wrap it with IndexIDMap
# #             print(f"Initialized new FAISS index with dim {self.embedding_dim}")
# #         return index

# class FaissDB:
#     def __init__(self, index_path="./data/faiss_index", embedding_dim=384):
#         self.index_path = index_path
#         self.embedding_dim = embedding_dim
#         self.index = self._load_index()

#     def _load_index(self):
#         try:
#             print(f"$$$$$$$$$$$$ Reading index with embeddings of {self.embedding_dim}")
#             index = faiss.read_index(self.index_path)
#             print(f"$$$$$$$$$$$$ Index read successfully of type {type(index)}")
#             if isinstance(index, faiss.IndexIDMap):
#                 print("Index is already an IndexIDMap.")
#             else:
#                 # Ensure the index is wrapped if not already
#                 print("Index is not an IndexIDMap. Wrapping it.")
#                 index = faiss.IndexIDMap(index)
#             print(f"Loaded FAISS index of type {type(index)} from {self.index_path}")
#         except Exception as e:
#             print(f"Exception {str(e)} occurred")
#             index = faiss.IndexFlatL2(self.embedding_dim)  # Create a new flat index
#             index = faiss.IndexIDMap(index)  # Wrap it with IndexIDMap
#             print(f"Initialized new FAISS index with dim {self.embedding_dim}")
#         return index

#     def save_index(self):
#         print(f"index: {self.index}; index path: {self.index_path}")
#         faiss.write_index(self.index, self.index_path)

#     def add_embeddings(self, embeddings, ids):
#         """
#         Add embeddings and their IDs to the FAISS index.
#         """
#         print(f"Adding embeddings of shape {embeddings.shape}")
#         if isinstance(self.index, faiss.IndexIDMap):
#             self.index.add_with_ids(embeddings, np.array(ids, dtype=np.int64))
#         else:
#             raise RuntimeError("The FAISS index is not wrapped with IndexIDMap.")
#         self.save_index()
#         print(f"Added {len(ids)} embeddings to the FAISS index.")

#     # def add_embeddings(self, embeddings: np.ndarray, ids: List[str]):
#     #     id_map = faiss.IndexIDMap(self.index)
#     #     id_map.add_with_ids(embeddings, np.array(ids, dtype=np.int64))

#     def search(self, query_embedding: np.ndarray, top_k: int) -> List[Tuple[int, float]]:
#         distances, indices = self.index.search(query_embedding, top_k)
#         return list(zip(indices[0], distances[0]))
