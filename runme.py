from optimizer import *
from courier_services import *

# PARAMETERS
# ==========
# Purchased items in a list of tuples (name, price, weight in kg)
purchased_items = [("Fossil watch", 21.95, 0.1),
                   ("Samsung Galaxy S21", 139.99, 0.2),
                   ("Redragon Devarajas K556", 24.6, 1.6),
                   ("Fossil Diver watch", 24.98, 0.2),
                   ("Samsung Galaxy S21 FE", 118.45, 0.3),
                   ("Cougar Forza Essential 50", 22.6, 0.3)]

# Name of the courier used
courier_service = "Urubox"

# Maximum number of import fee exemptions to use
fee_exemptions = 2


# OPTIMIZE AND PRINT RESULTS
# ==========================
optimal_solution, all_solutions = optimize_packaging(items=purchased_items,
                                                     transport_cost_func=couriers[courier_service]["cost_function"],
                                                     max_exempt_packages=fee_exemptions)
print_results(optimal_solution, all_solutions)