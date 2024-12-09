from fastapi import APIRouter
from app.models.schemas import OptimizationRequest, OptimizationResult, GetInitialConfig
from app.services.milp_optimizer import milp_optimization
from app.services.routines import read_json_input
from app.core.config import MAX_ITEMS, MAX_OPTIM_TIME
from app.utils.courier_services import courier_list

router = APIRouter()

@router.post("/optimize", response_model=OptimizationResult)
async def optimize(data: OptimizationRequest):
    purchased_items, selected_courier, fee_exemptions = read_json_input(data)
    optimal_solution = milp_optimization(items=purchased_items,
                                         courier=selected_courier,
                                         max_exemptions=fee_exemptions)
    result = optimal_solution.to_json()
    return result

@router.get("/couriers", response_model=GetInitialConfig)
async def get_couriers():
    return {"couriers": courier_list,
            "max_items": MAX_ITEMS,
            "max_optim_time": MAX_OPTIM_TIME}