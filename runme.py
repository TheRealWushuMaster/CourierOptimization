from brute_force_optimizer import *
from minlp_optimizer import *
from courier_services import *
from purchased_items import *

# BRUTE FORCE OPTIMIZATION
# ========================
optimal_solution, all_solutions = brute_force_optimization(items=purchased_items,
                                                           transport_cost_func=couriers[courier_service]["cost_function"],
                                                           max_exempt_packages=fee_exemptions)
# print_results(optimal_solution,
#               all_solutions,
#               courier_service)
display_solution(optimal_solution)

# MINLP OPTIMIZATION
# ==================
# solution = minlp_optimization(courier="USX",
#                               items=purchased_items,
#                               max_packages=None,
#                               max_exemptions=1)
# display_solution(solution)