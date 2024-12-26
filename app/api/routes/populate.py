# Populate Route (app/api/routes/populate.py)
# Allows bulk population of embeddings.

from fastapi import APIRouter
from typing import List
from app.core.faiss_db import FaissDB
from app.core.config import config
import numpy as np

router = APIRouter()

faiss_db = FaissDB(config.VECTOR_DB_PATH, config.EMBEDDING_DIM)

@router.post("/populate")
async def populate_vectors(documents: List[dict]):
    """
    Bulk insertion of embeddings into the vector database.
    """
    embeddings = [doc["embedding"] for doc in documents]
    ids = [int(doc["id"]) for doc in documents]
    texts = [doc["text"] for doc in documents]

    embeddings_np = np.array(embeddings, dtype=np.float32)
    faiss_db.add_embeddings(embeddings_np, ids, texts)
    faiss_db.save_index()

    return {"status": "success", "indexed_count": len(ids)}



# from fastapi import APIRouter
# from typing import List
# from app.core.faiss_db import FaissDB
# from app.core.config import config

# import numpy as np

# router = APIRouter()

# # Load FaissDB
# faiss_db = FaissDB(config.VECTOR_DB_PATH, config.EMBEDDING_DIM)

# @router.post("/populate")
# async def populate_vectors(documents: List[dict]):
#     embeddings = []
#     ids = []

#     for doc in documents:
#         embeddings.append(doc["embedding"])
#         ids.append(int(doc["id"]))

#     embeddings_np = np.array(embeddings, dtype=np.float32)
#     print(f"Embedding shape: {embeddings_np.shape}")  # Should be (n, 384) where `n` is the number of embeddings
#     faiss_db.add_embeddings(embeddings_np, ids)
#     faiss_db.save_index()

#     return {"status": "success", "indexed_count": len(ids)}
