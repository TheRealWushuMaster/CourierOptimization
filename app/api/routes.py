from fastapi import APIRouter
from app.models.schemas import OptimizationRequest, OptimizationResult, GetInitialConfig
from app.services.milp_optimizer import milp_optimization
from app.services.routines import read_json_input, key_valid
from app.core.config import MAX_ITEMS, MAX_OPTIM_TIME
from app.utils.courier_services import courier_list

router = APIRouter()

@router.post("/optimize", response_model=OptimizationResult)
async def optimize(data: OptimizationRequest):
    key, purchased_items, selected_courier, fee_exemptions, discount_rate = read_json_input(data)
    if key_valid(key):
        optimal_solution = milp_optimization(courier=selected_courier,
                                             items=purchased_items,
                                             max_exemptions=fee_exemptions,
                                             discount_rate=discount_rate)
        result = optimal_solution.to_json()
        return result
    else:
        return None

@router.get("/initial_config", response_model=GetInitialConfig)
async def get_initial_config():
    return {"couriers": courier_list,
            "max_items": MAX_ITEMS,
            "max_optim_time": MAX_OPTIM_TIME}