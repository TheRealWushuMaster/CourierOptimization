from brute_force_optimizer import *
from milp_optimizer import *
from courier_services import *
from purchased_items import *

# BRUTE FORCE OPTIMIZATION
# ========================
#optimal_solution, all_solutions = brute_force_optimization(items=purchased_items,
#                                                           courier=selected_courier,
#                                                           max_exemptions=fee_exemptions)

# MILP OPTIMIZATION
# ==================
optimal_solution = minlp_optimization(courier=selected_courier,
                                      items=purchased_items,
                                      max_packages=None,
                                      max_exemptions=fee_exemptions)

# DISPLAY THE RESULTS
# ===================
display_solution(optimal_solution, filename='solution_details.log')