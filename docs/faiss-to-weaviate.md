# Porting from Faiss + SQLite to Weaviate (or Weaviate + SQLite) on Cloud

## Overview
This document outlines the preparation, steps, and changes required to port the current implementation of a VectorDB service from a Faiss + SQLite-based architecture to Weaviate, a cloud-native vector database. The document also discusses whether a hybrid approach using Weaviate + SQLite would be beneficial, and what changes would be needed in this case.

## Why Weaviate?
Weaviate provides several advantages over Faiss:
1. **Cloud-Native Architecture**: Supports distributed, scalable, and managed deployments.
2. **Integrated Metadata**: Allows embedding metadata natively, reducing reliance on external databases like SQLite.
3. **RESTful API**: Simplifies interaction with the database, eliminating low-level management.
4. **Hybrid Search**: Combines vector similarity and symbolic filtering for enhanced queries.
5. **Scalability**: Handles large-scale embeddings and multi-node clusters seamlessly.
6. **Plug-in Options**: Built-in options for pre-trained embeddings and cloud-based integrations.

## Preparation
### Assess Current Architecture
- **Core Components**:
  - **FaissDB (FlatL2)**: Handles embeddings and vector similarity search.
  - **SQLite**: Stores metadata (e.g., `text`, `tags`, `external_id`, `category`).
  - **VectorDBService**: Bridges FaissDB and SQLite.
- **Endpoints**:
  - `/populate`: Adds embeddings and metadata.
  - `/search`: Searches embeddings and retrieves metadata.
  - Admin routes for peeking, deleting, and inspecting the databases.

### Map Functionalities to Weaviate
Weaviate natively supports:
- Embeddings insertion.
- Metadata storage with embedded vectors.
- Hybrid queries (vector + symbolic filtering).

### Changes Summary
- Replace FaissDB operations with Weaviate API calls.
- Reassess the role of SQLite:
  - **Option 1 (Weaviate-only)**: Eliminate SQLite, and store metadata entirely in Weaviate.
  - **Option 2 (Weaviate + SQLite)**: Retain SQLite for metadata querying and indexing flexibility.
- Update `VectorDBService` to integrate Weaviate functionality.

## Changes Needed
### Step 1: Introduce Weaviate Core Wrapper (`app/core/weaviate.py`)
- **Responsibilities**:
  - Wrap RESTful API calls for vector and metadata operations.
  - Abstract complexities of interacting with Weaviate.
- **Methods**:
  - `add_vector`: Add embeddings and metadata.
  - `search_vector`: Perform similarity searches.
  - `delete_vector`: Remove embeddings and metadata.
  - `get_vector_metadata`: Retrieve metadata by vector ID.

**Example Code:**
```python
import weaviate
import logging

logger = logging.getLogger(__name__)

class WeaviateDB:
    def __init__(self, url: str, api_key: str):
        self.client = weaviate.Client(
            url=url,
            auth_client_secret=weaviate.AuthApiKey(api_key)
        )

    def add_vector(self, class_name: str, data: dict):
        """
        Add a vector and its metadata.
        """
        try:
            self.client.data_object.create(data, class_name)
            logger.info("Successfully added vector.")
        except Exception as e:
            logger.error(f"Failed to add vector: {str(e)}")
            raise

    def search_vector(self, class_name: str, query_embedding: list, top_k: int):
        """
        Search for similar vectors.
        """
        try:
            result = self.client.query.get(class_name).with_near_vector({"vector": query_embedding}).with_limit(top_k).do()
            return result
        except Exception as e:
            logger.error(f"Failed to search vector: {str(e)}")
            raise

    def delete_vector(self, class_name: str, uuid: str):
        """
        Delete a vector by UUID.
        """
        try:
            self.client.data_object.delete(uuid)
            logger.info("Successfully deleted vector.")
        except Exception as e:
            logger.error(f"Failed to delete vector: {str(e)}")
            raise

    def get_vector_metadata(self, class_name: str, uuid: str):
        """
        Retrieve metadata for a given vector ID.
        """
        try:
            obj = self.client.data_object.get(uuid)
            return obj
        except Exception as e:
            logger.error(f"Failed to get metadata: {str(e)}")
            raise
```

### Step 2: Update VectorDBService (`app/services/vectordb.py`)
- Replace `FaissDB` calls with `WeaviateDB` methods.
- Decide whether to retain SQLite for metadata storage.
  - If retained, ensure metadata syncing with Weaviate.

**Key Changes:**
- **Add Vector:**
  - Push embedding + metadata to Weaviate.
  - Optionally save metadata in SQLite.
- **Search Vector:**
  - Perform vector similarity search in Weaviate.
  - Retrieve metadata (directly from Weaviate or via SQLite).
- **Delete Vector:**
  - Remove from Weaviate.
  - Optionally delete metadata from SQLite.

**Example Code:**
```python
def add_vector(self, embedding: list, text: str, external_id: str, category: str, tags: list):
    data = {
        "text": text,
        "external_id": external_id,
        "category": category,
        "tags": tags,
        "vector": embedding
    }
    self.weaviate_db.add_vector(class_name="Vector", data=data)
    if self.sqlite_db:
        self.sqlite_db.add_vector(text, external_id, category, tags)
```

### Step 3: Adjust API Endpoints
- Replace low-level Faiss interactions with Weaviate queries.
- Update `/populate` and `/search` endpoints to:
  - Accept and process embeddings and metadata.
  - Leverage Weaviate for hybrid queries.

### Step 4: Migrate Data
- Export existing Faiss embeddings and SQLite metadata.
- Convert them into Weaviate-compatible objects.
- Import using Weaviate's REST API.

**Migration Script Example:**
```python
from app.core.faiss_db import FaissDB
from app.core.sqlite_db import SQLiteDB
from app.core.weaviate import WeaviateDB

# Initialize databases
faiss_db = FaissDB("./data/faiss_index", 384)
sqlite_db = SQLiteDB("./data/metadata.db")
weaviate_db = WeaviateDB(url="https://weaviate-instance", api_key="your_api_key")

# Export from Faiss and SQLite
for vector in faiss_db.get_all_vectors():
    metadata = sqlite_db.get_metadata(vector["id"])
    weaviate_db.add_vector(class_name="Vector", data={
        "vector": vector["embedding"],
        **metadata
    })
```

### Step 5: Test and Validate
- Verify existing functionality for:
  - Adding vectors.
  - Searching vectors.
  - Retrieving metadata.
- Validate against sample RAG flows.
- Ensure scalability and response time benchmarks meet requirements.

### Step 6: Optimize for Cloud
- Evaluate Weaviate managed vs. self-hosted options.
- Configure authentication (API keys, OAuth).
- Scale Weaviate nodes based on expected traffic.

## Considerations
### Retaining SQLite
- **Advantages**:
  - Flexible querying of metadata.
  - Independent of Weaviate outages or migrations.
- **Disadvantages**:
  - Increased complexity and redundancy.

### Weaviate-Only Approach
- **Advantages**:
  - Simplified architecture.
  - Unified source of truth for embeddings and metadata.
- **Disadvantages**:
  - Dependency on Weaviate availability.
  - Potential cost implications for large-scale metadata.

## Conclusion
Porting to Weaviate (or Weaviate + SQLite) offers scalability, hybrid search capabilities, and a modern cloud-based architecture. While moving to a Weaviate-only setup simplifies the architecture, retaining SQLite provides additional flexibility and resilience. This document outlines the necessary steps to facilitate the transition and ensure a robust implementation.

