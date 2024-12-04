from fastapi import APIRouter
from app.models.schemas import OptimizationRequest, OptimizationResult
from app.services.milp_optimizer import milp_optimization

router = APIRouter()

@router.post("/optimize", response_model=OptimizationResult)
async def optimize(data: OptimizationRequest):
    optimal_solution = milp_optimization(data)
    result = optimal_solution.to_json()
    return result
