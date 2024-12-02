from app.services.brute_force_optimizer import *
from app.services.milp_optimizer import *
from app.utils.courier_services import *
from app.data.purchased_items import items

# PARAMETERS
# ==========
purchased_items, selected_courier, fee_exemptions = read_json_input(items)

# OPTIMIZATION STRATEGY
# =====================
optimization_strategy = 1   # 0 = brute force, 1 = MILP

if optimization_strategy==0:
    method = brute_force_optimization
elif optimization_strategy==1:
    method = milp_optimization

# OPTIMIZE
# ========
optimal_solution = method(items=purchased_items,
                          courier=selected_courier,
                          max_exemptions=fee_exemptions)

# DISPLAY/SAVE THE RESULTS
# ========================
optimal_solution.show()
optimal_solution.save_to_file()