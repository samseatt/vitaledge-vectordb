# scripts/populate_faiss.py
# Script to fetch embeddings from the VitalEdge Embeddings service and populate Faiss
# with sample data.
import requests
import numpy as np
from app.services.vectordb import FaissService

EMBEDDINGS_URL = "http://localhost:8007/embeddings/generate"
faiss_service = FaissService()

def fetch_embeddings(texts):
    """Fetch embeddings from VitalEdge Embeddings microservice."""
    response = requests.post(EMBEDDINGS_URL, json={"texts": texts})
    response.raise_for_status()
    return np.array(response.json()["embeddings"])

def populate_faiss():
    """Populate Faiss index with sample data."""
    texts = [
        "What are the symptoms of diabetes?",
        "How do you treat a cold?",
        "What is the capital of France?",
    ]
    embeddings = fetch_embeddings(texts)
    ids = np.arange(len(texts))  # Simple numeric IDs for demonstration
    faiss_service.add_vectors(embeddings, ids)
    print("Faiss index populated.")

if __name__ == "__main__":
    populate_faiss()
