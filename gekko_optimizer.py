from gekko import GEKKO
from math import ceil


# Initialize model
m = GEKKO(remote=False)

# Number of packages
max_packages = 3

# Sample data for package price and weight
package_price = [m.Param(value=100) for j in range(max_packages)]
package_weight = [m.Param(value=10) for j in range(max_packages)]

# Create a variable to represent total cost
total_cost = m.Var()

# Stepwise transport cost function
# Define stepwise transport cost using piecewise intervals


# Define stepwise transport cost using conditional constructs
def transport_cost(weight):
    # Initialize cost variable
    cost = m.Var()

    # Create piecewise conditions for the transport cost
    m.Equation(cost == 10 * (weight <= 5) +
               20 * ((weight > 5) & (weight <= 10)) +
               30 * ((weight > 10) & (weight <= 15)) +
               40 * (weight > 15))

    return cost

# Calculate transport fees for each package
transport_fees = m.sum([transport_cost(package_weight[j]) for j in range(max_packages)])

# Basic import fee (no exemptions yet)
import_fees = m.sum([0.60 * package_price[j] for j in range(max_packages)])

# Define total cost as the sum of transport fees and import fees
m.Equation(total_cost == transport_fees + import_fees)

# Set the objective to minimize total cost
m.Obj(total_cost)

# Solve the model
m.solve(disp=True)






# # Initialize Gekko model
# m = GEKKO(remote=False)

# # Number of items and their properties (price, weight)
# purchased_items = [("Fossil watch", 21.95, 0.1),
#                    ("Samsung Galaxy S21", 139.99, 0.2),
#                    ("Redragon Devarajas K556", 24.6, 1.6),
#                    ("Fossil Diver watch", 24.98, 0.2),
#                    ("Samsung Galaxy S21 FE", 118.45, 0.3),
#                    ("Cougar Forza Essential 50", 22.6, 1.3),
#                    ("Razorkin Needlehead Duskmourn", 10.36, 0.2),
#                    ("Screaming Nemesis Duskmourn", 9.11, 0.2),
#                    ("20g Tube Syringe Silver Thermal Paste", 9.95, 0.3)]
# num_items = len(purchased_items)
# max_packages = num_items  # Assume max number of packages = number of items

# # Prices and weights arrays
# prices = [item[1] for item in purchased_items]
# weights = [item[2] for item in purchased_items]

# # Binary decision variables: x[i][j] = 1 if item i is in package j
# x = [[m.Var(lb=0, ub=1, integer=True) for j in range(max_packages)]
#      for i in range(num_items)]

# # Variables for package totals (price, weight, and exemption status)
# package_price = [m.Var(lb=0) for j in range(max_packages)]
# package_weight = [m.Var(lb=0) for j in range(max_packages)]
# exempt = [m.Var(lb=0, ub=1, integer=True)
#           for j in range(max_packages)]  # Binary for import fee exemption

# # Constraints: Price and weight of each package
# for j in range(max_packages):
#     m.Equation(package_price[j] == m.sum(
#         [prices[i] * x[i][j] for i in range(num_items)]))
#     m.Equation(package_weight[j] == m.sum(
#         [weights[i] * x[i][j] for i in range(num_items)]))
#     m.Equation(package_price[j] <= 200)
#     m.Equation(package_weight[j] <= 20)

# # Ensure each item is assigned to exactly one package
# for i in range(num_items):
#     m.Equation(m.sum([x[i][j] for j in range(max_packages)]) == 1)

# # Exemptions constraint: Only 3 packages can be exempt
# m.Equation(m.sum(exempt) <= 3)

# # Transport fee (based on stepwise function of package weight)
# # Example function: cost increases by $10 for each 5kg increment


# def transport_cost(weight):
#     # Transport cost increases by $10 for each 5kg interval
#     return 10 * m.if3(weight <= 5, 1,
#                       m.if3(weight <= 10, 2,
#                             m.if3(weight <= 15, 3, 4)))


# # Objective function: minimize total cost (transport fees + import fees)
# total_cost = m.Var(lb=0)
# transport_fees = m.sum([transport_cost(package_weight[j])
#                        for j in range(max_packages)])

# # Define import fees with a minimum of $10 for non-exempt packages
# import_fee_package = [m.Var(lb=0) for j in range(max_packages)]  # Create an intermediate variable for each package's import fee

# for j in range(max_packages):
#     m.Equation(import_fee_package[j] == (1 - exempt[j]) * 0.60 * package_price[j])


# # Sum up all the import fees
# import_fees = m.sum([import_fee_package[j] for j in range(max_packages)])

# # Objective function: minimize total cost (transport fees + import fees)
# m.Equation(total_cost == transport_fees + import_fees)

# # Set objective
# m.Obj(total_cost)

# # Solve
# m.solve(disp=True)

# # Output the optimized solution
# for j in range(max_packages):
#     print(f'Package {j+1}:')
#     print(f'  Price: ${package_price[j].value[0]:.2f}')
#     print(f'  Weight: {package_weight[j].value[0]:.2f} kg')
#     print(f'  Exempt from import fee: {bool(round(exempt[j].value[0]))}')
#     print('  Items in this package:')
#     for i in range(num_items):
#         if round(x[i][j].value[0]):
#             print(f'    {purchased_items[i][0]} - ${purchased_items[i][1]}, {purchased_items[i][2]} kg')
