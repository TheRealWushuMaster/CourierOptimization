import pulp

# Define data for items: (price, weight, name)
items = [(21.95, 0.1, "Fossil watch"),
         (139.99, 0.2, "Samsung Galaxy S21"),
         (24.6, 1.6, "Redragon Devarajas K556"),
         (24.98, 0.2, "Fossil Diver watch"),
         (118.45, 0.3, "Samsung Galaxy S21 FE"),
         (22.6, 0.3, "Cougar Forza Essential 50")]

# Number of items and max packages
num_items = len(items)
max_packages = num_items  # At most, each item in its own package

def solve_with_exemptions(num_exemptions):
    # Create MILP problem
    prob = pulp.LpProblem(
        f"Minimize_Total_Cost_With_{num_exemptions}_Exemptions", pulp.LpMinimize)

    # Decision variables (same as before)
    x = [[pulp.LpVariable(f"x_{i}_{j}", cat="Binary")
          for j in range(max_packages)] for i in range(num_items)]
    y = [pulp.LpVariable(f"y_{j}", cat="Binary") for j in range(max_packages)]
    w = [pulp.LpVariable(f"w_{j}", lowBound=0) for j in range(
        max_packages)]  # Total weight in each package
    z = [pulp.LpVariable(f"z_{j}", cat="Binary")
         for j in range(max_packages)]  # Exemption indicator

    # Objective function: Minimize total cost
    prob += pulp.lpSum([
        5 * y[j] +
        pulp.LpVariable(f"weight_cost_{j}", lowBound=0) +
        (1 - z[j]) * 0.6 * pulp.lpSum([x[i][j] * items[i][0]
                                       for i in range(num_items)])  # Import fee
        for j in range(max_packages)
    ]), "Minimize_Total_Cost"

    # Constraints (same as before)
    for i in range(num_items):
        prob += pulp.lpSum([x[i][j] for j in range(max_packages)]
                           ) == 1, f"One_Package_for_Item_{i}"

    for j in range(max_packages):
        prob += pulp.lpSum([x[i][j] * items[i][0] for i in range(num_items)]
                           ) <= 200 * y[j], f"Price_Limit_Package_{j}"
        prob += pulp.lpSum([x[i][j] * items[i][1] for i in range(num_items)]
                           ) <= 20 * y[j], f"Weight_Limit_Package_{j}"
        prob += w[j] == pulp.lpSum([x[i][j] * items[i][1]
                                   for i in range(num_items)]), f"Weight_Calculation_Package_{j}"

    # Exemption limit constraint
    prob += pulp.lpSum([z[j] for j in range(max_packages)]
                       ) <= num_exemptions, f"Exemption_Limit_{num_exemptions}"

    # Exemptions valid only for existing packages
    for j in range(max_packages):
        prob += z[j] <= y[j], f"Exemption_Valid_Package_{j}"

    # Solve the problem
    prob.solve()

    # Return the total cost and package configuration
    total_cost = pulp.value(prob.objective)
    package_configurations = []
    for j in range(max_packages):
        if pulp.value(y[j]) > 0:
            items_in_package = [i for i in range(
                num_items) if pulp.value(x[i][j]) > 0]
            package_configurations.append(
                (items_in_package, pulp.value(w[j]), bool(pulp.value(z[j]))))

    return total_cost, package_configurations

# Solve for different exemption limits
for exemptions in range(4):  # 0 to 3 exemptions
    total_cost, packages = solve_with_exemptions(exemptions)
    print(f"Total cost with {exemptions} exemptions: {total_cost}")
    print(f"Package configurations: {packages}")
