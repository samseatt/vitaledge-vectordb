# app/models/add_vectors_request.py
from pydantic import BaseModel
from typing import List

class AddVectorsRequest(BaseModel):
    id: int
    embedding: List[float]
