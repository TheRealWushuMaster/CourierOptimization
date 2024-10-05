from optimizer import *
from courier_services import *
from purchased_items import *

# Name of the courier used
courier_service = "Urubox"

# Maximum number of import fee exemptions to use
fee_exemptions = 2

# RUN OPTIMIZATION AND PRINT RESULTS
# ==================================
optimal_solution, all_solutions = optimize_packaging(items=purchased_items,
                                                     transport_cost_func=couriers[courier_service]["cost_function"],
                                                     max_exempt_packages=fee_exemptions)
print_results(optimal_solution,
              all_solutions,
              courier_service)