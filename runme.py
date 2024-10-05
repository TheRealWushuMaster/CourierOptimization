from optimizer import *
from courier_services import *
from purchased_items import *

# RUN OPTIMIZATION AND PRINT RESULTS
# ==================================
optimal_solution, all_solutions = optimize_packaging(items=purchased_items,
                                                     transport_cost_func=couriers[courier_service]["cost_function"],
                                                     max_exempt_packages=fee_exemptions)
print_results(optimal_solution,
              all_solutions,
              courier_service)