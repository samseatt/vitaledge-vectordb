# scripts/test_search.py
# Script to test vector search
import numpy as np
from app.services.vectordb import FaissService

def test_search():
    """Test searching in the Faiss index."""
    query_text = "What are the symptoms of diabetes?"
    # Assuming fetch_embeddings() returns a single embedding for the query
    query_embedding = fetch_embeddings([query_text])
    faiss_service = FaissService()
    distances, indices, texts = faiss_service.search_vectors(query_embedding, k=3)
    print("Search Results:")
    print(f"Distances: {distances}")
    print(f"Indices: {indices}")
    print(f"Texts: {texts}")

if __name__ == "__main__":
    test_search()
