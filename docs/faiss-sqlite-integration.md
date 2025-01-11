# Technical Document: Integration of Faiss, SQLite, and FlatL2 Index

## Overview
This document explains the underlying architecture and theoretical concepts behind the integration of Faiss (Facebook AI Similarity Search), SQLite, and the FlatL2 index. It aims to provide a developer-centric perspective on how these components work together to manage and query high-dimensional vector data efficiently. The integration supports use cases such as semantic search, RAG (Retrieval-Augmented Generation), and metadata management.

---

## Core Components

### 1. **Faiss**
#### **Purpose**:
Faiss is a library designed for efficient similarity search and clustering of dense vectors. It enables rapid searches in high-dimensional spaces using optimized algorithms and data structures.

#### **Key Concepts**:
- **Vector Embeddings**:
  Vectors represent semantic information (e.g., text, images) in high-dimensional space.
- **IndexFlatL2**:
  A flat index for nearest neighbor search based on L2 (Euclidean) distance.
  - **Characteristics**:
    - Simple to implement and use.
    - No compression or approximation (full accuracy).
    - Suitable for smaller datasets (<10 million vectors).
  - **Operations**:
    - **Add**: Insert vectors into the index.
    - **Search**: Retrieve the nearest neighbors of a query vector.
    - **Delete**: Remove vectors by ID (though this can result in ID compaction).

#### **Advantages**:
- High performance for exact matches.
- Easy integration with Python and other systems.
- Support for both GPU and CPU.

#### **Limitations**:
- Lack of built-in metadata management.
- Compacting indices upon deletions (IDs may shift).

---

### 2. **SQLite**
#### **Purpose**:
SQLite serves as the metadata storage layer, managing information such as textual descriptions, categories, external IDs, and tags for each vector stored in Faiss.

#### **Key Concepts**:
- **Relational Database**:
  Data is structured in tables with relationships and constraints.
- **Schema**:
  - **Vectors Table**:
    Stores metadata such as `id`, `text`, `external_id`, `category`, and timestamps.
    ```sql
    CREATE TABLE vectors (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      text TEXT NOT NULL,
      external_id TEXT UNIQUE,
      category TEXT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ```
  - **Tags Table**:
    Manages user-defined tags.
    ```sql
    CREATE TABLE tags (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      tag TEXT UNIQUE
    );
    ```
  - **Vector-Tags Relationship**:
    Links vectors to tags for richer metadata.
    ```sql
    CREATE TABLE vector_tags (
      vector_id INTEGER,
      tag_id INTEGER,
      PRIMARY KEY (vector_id, tag_id),
      FOREIGN KEY (vector_id) REFERENCES vectors (id) ON DELETE CASCADE,
      FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
    );
    ```

#### **Advantages**:
- Provides a rich metadata layer for semantic search.
- Simple to query and manage.
- Lightweight and embedded, requiring no external server.

---

### 3. **Integration via FlatL2 Index**

#### **Faiss and SQLite Complementarity**:
- **Faiss**:
  Efficient for similarity search but lacks metadata storage.
- **SQLite**:
  Manages rich metadata but cannot handle high-dimensional vector operations.

The combination allows each system to handle what it does best:
- Faiss manages the vectors and performs similarity searches.
- SQLite provides the metadata layer for contextual and semantic enrichment.

#### **Operational Workflow**:
1. **Population**:
   - Embeddings are added to the Faiss index.
   - Corresponding metadata is stored in SQLite.
   - `vector_id` in SQLite aligns with the position of the vector in Faiss.

2. **Search**:
   - A query embedding is passed to Faiss.
   - Faiss returns the nearest neighbors (vector IDs and distances).
   - Vector IDs are used to retrieve metadata from SQLite.

3. **Metadata Enrichment**:
   - Tags, categories, and external IDs enrich the search results for downstream use cases like RAG flows.

---

## Key Classes and Methods

### 1. **FaissDB Class**
#### Responsibilities:
- Manages the lifecycle of the Faiss index.
- Provides methods for adding, searching, and retrieving vectors.

#### Key Methods:
- `add_vector(embedding: np.ndarray)`:
  Adds a single embedding to the Faiss index.
- `search_vectors(query_vector: np.ndarray, top_k: int)`:
  Searches for the top K nearest neighbors.
- `get_all_vectors()`:
  Retrieves all vectors stored in the Faiss index.

---

### 2. **SQLiteDB Class**
#### Responsibilities:
- Manages the lifecycle of the SQLite database.
- Handles metadata operations.

#### Key Methods:
- `add_vector(text: str, external_id: Optional[str], category: Optional[str], tags: List[str]) -> int`:
  Adds metadata for a vector and returns its ID.
- `get_metadata(vector_id: int)`:
  Retrieves metadata associated with a vector ID.
- `get_all_metadata()`:
  Retrieves all metadata entries.

---

### 3. **VectorDBService Class**
#### Responsibilities:
- Acts as an intermediary between FaissDB and SQLiteDB.
- Simplifies operations for higher-level API routes.

#### Key Methods:
- `add_vector(embedding: list, text: str, external_id: Optional[str], category: Optional[str], tags: List[str]) -> int`:
  Adds a vector and its metadata.
- `search_vectors(query_vector: list, top_k: int) -> List[dict]`:
  Searches Faiss and enriches results with metadata.
- `delete_vector(vector_id: int)`:
  Deletes a vector and its metadata.

---

## Common Challenges and Resolutions

### **ID Compacting in Faiss**:
- **Challenge**: Deletions in Faiss may lead to ID compaction.
- **Solution**: Avoid deletions or periodically repopulate Faiss from a canonical SQLite source.

### **Metadata Synchronization**:
- **Challenge**: Misalignment between Faiss and SQLite data.
- **Solution**: Use `search_vectors()` to validate alignment by searching embeddings and cross-checking with metadata.

---

## Summary
The integration of Faiss and SQLite leverages the strengths of each system to provide a scalable, efficient, and rich vector database. By combining Faiss’s similarity search with SQLite’s metadata management, the system supports advanced use cases like RAG and semantic search while maintaining simplicity and robustness. Understanding the theory and operations outlined in this document will empower developers to troubleshoot and extend the system effectively.

