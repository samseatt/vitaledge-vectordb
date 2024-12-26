# app/models/search_vectors_request.py
from pydantic import BaseModel
from typing import List

class SearchVectorsRequest(BaseModel):
    query_vector: List[float]
    top_k: int
