from app.services.brute_force_optimizer import *
from app.services.milp_optimizer import *
from app.utils.courier_services import *
from app.data.purchased_items import purchased_items

# PARAMETERS
# ==========
selected_courier = "Grinbox"  # Name of the courier used
fee_exemptions = 2              # Maximum import fee exemptions to use

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