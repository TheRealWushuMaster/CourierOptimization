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
    key: str
    purchases: List[Item]
    courier_service: str
    import_fee_exemptions: int
    discount_rate: float

class OptimizationResult(BaseModel):
    status: str
    time_spent: float
    packages: List[Package]
    total_price: float
    total_weight: float
    total_handling: float
    total_freight: float
    total_subtotal: float
    total_tax: float
    total_tfspu: float
    total_transport: float
    total_import_fee: float
    total_cost: float

class Courier(BaseModel):
    id: str
    name: str

class GetInitialConfig(BaseModel):
    couriers: List[Courier]
    max_items: int
    max_optim_time: int
