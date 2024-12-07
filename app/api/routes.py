from fastapi import APIRouter
from app.models.schemas import OptimizationRequest, OptimizationResult
from app.services.milp_optimizer import milp_optimization
from app.services.routines import read_json_input

router = APIRouter()

@router.post("/optimize", response_model=OptimizationResult)
async def optimize(data: OptimizationRequest):
    purchased_items, selected_courier, fee_exemptions = read_json_input(data)
    optimal_solution = milp_optimization(items=purchased_items,
                                         courier=selected_courier,
                                         max_exemptions=fee_exemptions)
    result = optimal_solution.to_json()
    return result
