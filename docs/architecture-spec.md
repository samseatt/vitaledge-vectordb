### Architecture and Specification Document for **VitalEdge Vector DB** (vitaledge-vectordb)

---

#### **Document Version: 1.0**  
**Date:** January 10, 2025  
**Author:** Sam Seatt  

`This document captures the current architecture and roadmap for the **VitalEdge Vector DB**. Further refinements will align with RAG advancements and the project’s evolving needs. Let me know if additional details or expansions are required!`

---

### **Introduction**

The **VitalEdge Vector DB** is a microservice designed to support retrieval-augmented generation (RAG) workflows, enabling efficient vector storage and retrieval for embeddings in a healthcare-focused context. This microservice interacts with various upstream and downstream systems, providing a scalable and performant interface for managing embeddings and metadata. The service is built using **Faiss** for vector similarity search and **SQLite** for metadata storage, ensuring simplicity and adaptability for production and development environments.

---

### **Core Objectives**

1. **Efficient Vector Search**: Provide fast vector similarity search using **Faiss IndexFlatL2**.
2. **Rich Metadata Support**: Store metadata such as `text`, `tags`, `categories`, and `external_id` in a relational **SQLite** database.
3. **RAG Integration**: Facilitate integration with LangChain pipelines and other RAG workflows by supporting:
   - Bulk insertion of embeddings and metadata.
   - Search returning both vector IDs and metadata.
4. **Scalability and Simplicity**: While supporting core functionalities, maintain a design that can evolve with cloud-native solutions like **Weaviate**.
5. **Modular Design**: Use independent layers for vector storage (Faiss) and metadata (SQLite) to support potential future portability or migration.

---

### **System Architecture**

#### **High-Level Overview**

The system comprises the following key layers:

1. **API Layer**:
   - Built using **FastAPI**.
   - Provides routes for `/admin`, `/search`, and `/populate` functionalities.
2. **Service Layer**:
   - `VectorDBService` acts as a bridge between the API layer and core database modules (`faiss_db` and `sqlite_db`).
   - Handles business logic, ensuring synchronization between embeddings and metadata.
3. **Core Database Layer**:
   - `faiss_db`: Manages vector embeddings using **Faiss IndexFlatL2**.
   - `sqlite_db`: Manages associated metadata using **SQLite** relational database.

#### **Data Flow**

1. **Populate**:
   - API endpoint `/populate` receives embeddings and metadata.
   - The `VectorDBService` handles insertion:
     - Embeddings are added to Faiss.
     - Metadata is added to SQLite with the `embed_id` (Faiss index) for synchronization.
2. **Search**:
   - API endpoint `/search` processes a query embedding.
   - Faiss performs similarity search and returns vector IDs and distances.
   - The service fetches metadata from SQLite using `embed_id` and combines it with search results.
3. **Admin Operations**:
   - API endpoints under `/admin` allow diagnostics and database management.
   - Examples: `/admin/peek/sqlite`, `/admin/peek/vectordb`, and `/admin/embedding/{vector_id}`.

---

### **Components and Modules**

#### **API Endpoints**

| **Route**                  | **Description**                                         |
|----------------------------|---------------------------------------------------------|
| `/populate`                | Bulk insert embeddings and metadata.                   |
| `/search`                  | Perform similarity search in Faiss.                    |
| `/admin/vectors`           | List metadata of all vectors stored in SQLite.         |
| `/admin/tags`              | List all tags in SQLite.                               |
| `/admin/peek/vectordb`     | Peek into Faiss for stored embeddings.                 |
| `/admin/peek/sqlite`       | Peek into SQLite for stored metadata.                  |
| `/admin/embedding/{id}`    | Retrieve an embedding by its Faiss ID.                 |

---

#### **Service Layer**

The `VectorDBService` is the abstraction layer that manages Faiss and SQLite operations, ensuring synchronization between the two databases.

**Key Responsibilities:**
- Inserting embeddings (`add_vector`).
- Searching vectors (`search_vectors`).
- Fetching metadata (`list_vectors`, `list_tags`).
- Pruning vectors and metadata (if deletion is supported).

---

#### **Core Database Layer**

1. **FaissDB (app/core/faiss_db.py)**:
   - **Index Type**: `IndexFlatL2` for simplicity and efficiency.
   - **Core Methods**:
     - `add_vector`: Adds a single embedding.
     - `search_vectors`: Searches for the top-k nearest neighbors.
     - `get_all_vectors`: Returns all embeddings.
     - `delete_vector`: Deletes a vector by its Faiss ID.
   - **Behavior**:
     - Sequential indexing (no ID mapping).
     - Faiss index persists to a file for durability.

2. **SQLiteDB (app/core/sqlite_db.py)**:
   - **Schema**:
     - `vectors` table stores metadata (`text`, `tags`, `category`, `external_id`).
     - `tags` and `vector_tags` tables manage tag relationships.
   - **Core Methods**:
     - `add_vector`: Inserts metadata and associates it with `embed_id` (Faiss index).
     - `get_metadata_by_embed_id`: Retrieves metadata using `embed_id`.
     - `get_vectors`: Retrieves metadata by category or all vectors.

---

### **Key Design Considerations**

1. **Embedding Synchronization**:
   - The `embed_id` (Faiss index ID) is saved in SQLite for synchronization.
   - No deletions are allowed to avoid ID compaction issues in Faiss.

2. **Metadata Storage**:
   - SQLite stores:
     - `text`: Original unembedded content.
     - `tags`: Descriptive tags.
     - `external_id`: ID from an external data source.
     - `category`: High-level classification.

3. **Future Extensibility**:
   - Cloud-native options like Weaviate can replace Faiss, with SQLite retained for richer metadata.

---

### **RAG Workflow**

#### **Flow Diagram**

1. **Input**:
   - Query: A patient identifier, phenotype tags, and a prompt.
2. **Step 1**: Query Datalake (PostgreSQL microservice) for genomic and clinical data.
3. **Step 2**: Generate query embedding using the embedding service.
4. **Step 3**: Search VectorDB for embeddings:
   - Use Faiss for vector similarity.
   - Fetch metadata from SQLite for matched embeddings.
5. **Step 4**: Combine data:
   - Merge Datalake results, VectorDB metadata, and prompt.
6. **Step 5**: LLM Processing:
   - Local LLM refines the prompt or generates an intermediate summary.
   - OpenAI API or other LLM generates the final response.

---

### **Open Questions**

1. **Deletions**:
   - Currently unsupported to prevent ID compaction.
   - Pruning will require full repopulation.
2. **Scaling**:
   - SQLite is sufficient for metadata, but a scalable solution (e.g., PostgreSQL) may be needed.

---

### **Future Enhancements**

1. **Cloud Migration**:
   - Replace Faiss with **Weaviate** for vector storage and search.
2. **Advanced Search**:
   - Enable filtering by tags or categories during vector search.
3. **Full-text Search**:
   - Extend SQLite with full-text search for richer metadata queries.

---
