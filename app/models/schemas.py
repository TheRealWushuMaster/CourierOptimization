from pydantic import BaseModel
from typing import List

class Item(BaseModel):
    name: str
    price: float
    weight: float

class Package(BaseModel):
    package_id: int
    items:List[Item]
    price: float
    weight: float
    handling: float
    freight: float
    subtotal: float
    tax: float
    tfspu: float
    transport: float
    import_fee: float
    cost: float

class OptimizationRequest(BaseModel):
    items: List[Item]
    courier_service: str
    import_fee_exemptions: int

class OptimizationResult(BaseModel):
    packages: List[Package]
    total_price: float
    total_weight: float
    total_handling: float
    total_total_freight: float
    total_subtotal: float
    total_tax: float
    total_tfspu: float
    total_transport: float
    total_import_fee: float
    total_cost: float
