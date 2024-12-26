# app/models/delete_vectors_request.py
from pydantic import BaseModel
from typing import List

class DeleteVectorsRequest(BaseModel):
    vector_ids: List[int]
