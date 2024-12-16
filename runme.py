from app.services.brute_force_optimizer import *
from app.services.milp_optimizer import *
from app.utils.courier_services import *
from app.data.purchased_items import items

# PARAMETERS
# ==========
key, purchased_items, selected_courier, fee_exemptions, discount_rate = read_json_input(items)

# OPTIMIZATION STRATEGY
# =====================
optimization_strategy = 1   # 0 = brute force, 1 = MILP

if optimization_strategy==0:
    method = brute_force_optimization
elif optimization_strategy==1:
    method = milp_optimization

# OPTIMIZE
# ========
optimal_solution = method(courier=selected_courier,
                          items=purchased_items,
                          discount_rate=discount_rate,
                          max_exemptions=fee_exemptions,
                          print_optimal_value=True)

# DISPLAY/SAVE THE RESULTS
# ========================
optimal_solution.show()
optimal_solution.save_to_file()