from fastapi import APIRouter
from app.models.schemas import OptimizationRequest, OptimizationResult
from app.services.milp_optimizer import milp_optimization
from app.services.brute_force_optimizer import brute_force_optimization

router = APIRouter()

@router.post("/optimize", response_model=OptimizationResult)
async def optimize(data: OptimizationRequest):
    """
    Endpoint to optimize package transport.
    """
    result = milp_optimization(data.items, data.courier)    # Consider case for brute force
    return result