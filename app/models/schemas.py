from pydantic import BaseModel
from typing import List

class Item(BaseModel):
    name: str
    price: float
    weight: float

class OptimizationRequest(BaseModel):
    items: List[Item]
    courier: str

class OptimizationResult(BaseModel):
    total_cost: float
    tax: float
    packages: List[dict]
