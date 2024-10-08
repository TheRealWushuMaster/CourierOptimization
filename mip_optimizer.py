import pulp
from math import ceil

# Items data: (name, price, weight)
items = [("Fossil watch", 21.95, 0.1),
         ("Samsung Galaxy S21", 139.99, 0.2),
         ("Redragon Devarajas K556", 24.6, 1.6),
         ("Fossil Diver watch", 24.98, 0.2),
         ("Samsung Galaxy S21 FE", 118.45, 0.3),
         ("Cougar Forza Essential 50", 22.6, 1.3),
         ("Razorkin Needlehead Duskmourn", 10.36, 0.2),
         ("Screaming Nemesis Duskmourn", 9.11, 0.2),
         ("20g Tube Syringe Silver Thermal Paste", 9.95, 0.3)]

# Constraints
max_price_per_package = 200
max_weight_per_package = 20

# Allow user to input the number of packages, with default being number of items
num_items = len(items)
num_packages = num_items  # Default: each item in its own package
user_defined_num_packages = None  # User can change this to a specific number if desired

if user_defined_num_packages is not None:
    num_packages = user_defined_num_packages

# Couriers and costs (stepwise functions)
def courier_cost_usx(weight, prob):
    if isinstance(weight, float):
        if weight <= 1:
            return 5
        elif weight <= 2:
            return 5 + (weight - 1) * 4
        else:
            return 5 + 4 + (weight - 2) * 3.5
    elif isinstance(weight, pulp.LpVariable):
        w1 = pulp.LpVariable(f'w1_{weight}', lowBound=0, upBound=1)
        w2 = pulp.LpVariable(f'w2_{weight}', lowBound=0, upBound=1)
        w3 = pulp.LpVariable(f'w3_{weight}', lowBound=0)
        prob += weight == w1 + w2 + w3  # Ensure weight constraints
        return 5 * w1 + 4 * w2 + 3.5 * w3

# def courier_cost_another(weight, prob):
#     if isinstance(weight, float):
#         return ceil(weight / 0.1) * 17.5
#     elif isinstance(weight, pulp.LpVariable):
#         return pulp.ceil(weight / 0.1) * 17.5

# Choose selected courier per package
courier_functions = {"USX": courier_cost_usx}#, "Another": courier_cost_another}
selected_courier = {0: "USX", 1: "USX", 2: "USX", 3: "USX", 4: "USX", 5: "USX", 6: "USX", 7: "USX", 8: "USX"}  # Example of assigning couriers to packages




# Initialize PuLP problem
prob = pulp.LpProblem("Minimize_Import_Costs", pulp.LpMinimize)

# Binary variable: whether item i is in package j
x = pulp.LpVariable.dicts("x", ((i, j) for i in range(num_items) for j in range(num_packages)), cat='Binary')

# Weight of each package
w = pulp.LpVariable.dicts("w", range(num_packages), lowBound=0)

# Price of each package
package_price = pulp.LpVariable.dicts("package_price", range(num_packages), lowBound=0)

# Binary variable for whether each package is exempt from import fee
y = pulp.LpVariable.dicts("y", range(num_packages), cat='Binary')

import_fee_cost = pulp.LpVariable.dicts("import_fee_cost", range(num_packages), lowBound=0)

M = 10000   # Big M constraint

# Price and weight constraints
for j in range(num_packages):
    prob += pulp.lpSum([items[i][1] * x[i, j] for i in range(num_items)]) == package_price[j]
    prob += package_price[j] <= max_price_per_package  # Price constraint
    prob += pulp.lpSum([items[i][2] * x[i, j] for i in range(num_items)]) == w[j]  # Weight constraint
    prob += w[j] <= max_weight_per_package  # Max weight constraint
    prob += import_fee_cost[j] >= 0
    prob += import_fee_cost[j] <= 0.6 * package_price[j]
    prob += import_fee_cost[j] >= 0.6 * package_price[j] - M * y[j]  # When not exempt y[j] == 0
    prob += import_fee_cost[j] <= M * (1 - y[j])  # Should be zero if exempt y[j] == 1


# Up to 3 packages can be exempt from import fees
prob += pulp.lpSum([y[j] for j in range(num_packages)]) <= 3


# Objective function: Minimize the total cost (courier fee + import fee)
prob += pulp.lpSum([
    courier_functions[selected_courier[j]](w[j], prob) + import_fee_cost[j]
    for j in range(num_packages)
])





# Solve the problem
prob.solve()

# Display the status of the solution
print(f"Status: {pulp.LpStatus[prob.status]}")

# Print the optimal package allocations and total cost
for j in range(num_packages):
    print(f"\nPackage {j + 1}:")
    package_items = [items[i][0]
                     for i in range(num_items) if pulp.value(x[i, j]) == 1]
    print(f"  Items: {package_items}")
    print(f"  Total weight: {pulp.value(w[j])} kg")
    print(f"  Exempt from import fee: {pulp.value(y[j]) == 1}")
    print(f"  Courier cost: {
          courier_functions[selected_courier[j]](pulp.value(w[j]), prob)}")
