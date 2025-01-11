# VitalEdge Vector DB

VitalEdge Vector DB is a microservice for managing embeddings and their associated metadata, specifically designed to support **Retrieval-Augmented Generation (RAG)** workflows. It uses **Faiss** for efficient vector similarity searches and **SQLite** for relational metadata storage, ensuring a lightweight, fast, and adaptable solution for embedding management in healthcare and beyond.

---

## **Features**

- **Efficient Vector Search**: 
  - Powered by **Faiss IndexFlatL2** for fast similarity search.
  - Handles high-dimensional embeddings (e.g., 384 dimensions for `all-MiniLM-L6-v2`).

- **Rich Metadata Support**:
  - Store metadata such as `text`, `tags`, `category`, and `external_id` in SQLite.
  - Easily extendable for additional metadata requirements.

- **RAG Workflow Support**:
  - Seamless integration with LangChain and other frameworks.
  - Optimized for genomic, clinical, and other domain-specific use cases.

- **Three Sets of Endpoints**:
  - `/admin/*`: Diagnostics and metadata operations.
  - `/populate/*`: Bulk insertion of embeddings and metadata.
  - `/search/*`: Vector similarity search with metadata retrieval.

---

## **Getting Started**

### **Installation**

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/vitaledge-vectordb.git
   cd vitaledge-vectordb
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file based on the provided `.env.example`.

4. Run the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```

---

### **Endpoints**

#### **Admin Endpoints**
| **Endpoint**               | **Description**                                                |
|----------------------------|----------------------------------------------------------------|
| `/admin/vectors`           | List all vectors (metadata) with optional category filtering. |
| `/admin/tags`              | List all tags in the database.                                |
| `/admin/peek/vectordb`     | Peek into the Faiss index.                                    |
| `/admin/peek/sqlite`       | Peek into the SQLite database.                                |
| `/admin/embedding/{id}`    | Retrieve an embedding by its ID.                              |

#### **Populate Endpoint**
| **Endpoint**               | **Description**                                               |
|----------------------------|----------------------------------------------------------------|
| `/populate/populate`       | Bulk insert embeddings and metadata into the database.        |

#### **Search Endpoint**
| **Endpoint**               | **Description**                                               |
|----------------------------|----------------------------------------------------------------|
| `/search/search`           | Perform similarity search and return results with metadata.   |

---

## **Architecture**

### **High-Level Overview**
The system is composed of three layers:

1. **API Layer**:
   - Built with **FastAPI**.
   - Routes for `/admin`, `/populate`, and `/search`.

2. **Service Layer**:
   - `VectorDBService` orchestrates interactions between Faiss and SQLite.

3. **Core Database Layer**:
   - **FaissDB**: Manages embeddings and similarity searches using `IndexFlatL2`.
   - **SQLiteDB**: Stores metadata such as `text`, `tags`, and `category`.

---

### **RAG Workflow**

1. **Input**: Patient identifier, phenotype tags, and a user prompt.
2. **Step 1**: Query **Datalake** for patient-specific data.
3. **Step 2**: Generate query embedding using the **Embedding Generator**.
4. **Step 3**: Perform similarity search in **VectorDB**:
   - Fetch embeddings from Faiss.
   - Retrieve metadata from SQLite.
5. **Step 4**: Combine Datalake results, VectorDB metadata, and user prompt.
6. **Step 5**: Process through **OpenAI API** or **local LLM**.

---

## **Core Components**

### **FaissDB (app/core/faiss_db.py)**
- **Index Type**: `IndexFlatL2`.
- **Key Methods**:
  - `add_vector`: Add embeddings to Faiss.
  - `search_vectors`: Perform similarity searches.
  - `get_all_vectors`: Retrieve all stored embeddings.

### **SQLiteDB (app/core/sqlite_db.py)**
- **Schema**:
  - `vectors`: Stores metadata (e.g., `text`, `tags`, `category`).
  - `tags` and `vector_tags`: Manage tag relationships.
- **Key Methods**:
  - `add_vector`: Insert metadata and associate it with Faiss IDs.
  - `get_metadata_by_embed_id`: Retrieve metadata using Faiss IDs.

---

## **Deployment**

### **Local Development**
1. Run the application locally using **Uvicorn**:
   ```bash
   uvicorn app.main:app --reload
   ```

### **Production Deployment**
- Deploy on **Docker**:
  ```bash
  docker build -t vitaledge-vectordb .
  docker run -p 8000:8000 vitaledge-vectordb
  ```

- Use cloud-native services for scalability:
  - Replace **Faiss** with **Weaviate** for vector storage.
  - Use **PostgreSQL** for metadata storage.

---

## **Contributing**

We welcome contributions to improve VitalEdge Vector DB. To contribute:
1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature-branch-name
   ```
3. Commit changes:
   ```bash
   git commit -m "Add feature or fix bug"
   ```
4. Push changes:
   ```bash
   git push origin feature-branch-name
   ```
5. Open a pull request.

---

## **Future Enhancements**
- Migrate Faiss to a cloud-native solution like **Weaviate**.
- Support advanced search filters using metadata.
- Integrate full-text search in SQLite for richer metadata queries.
- Add LLM-assisted embeddings generation as part of the populate pipeline.

---

## **License**

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## **Acknowledgments**
Special thanks to the Meta (Faiss), Hugging Face, OpenAI and FastAPI communities for their invaluable tools and resources.

---
