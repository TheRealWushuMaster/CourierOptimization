import pulp
from courier_services import couriers

class CourierOptimizer:
    def __init__(self, items, courier_service, max_exemptions=3):
        """
        Initializes the optimizer class.
        
        * param items:
            List of tuples (price, weight, name) representing each purchase.
        * param courier_service:
            The courier cost function (e.g., package_cost_urubox).
        * param max_exemptions:
            Maximum number of packages exempt from import fees.
        """
        self.items = items
        self.courier_service = courier_service
        self.courier_service_cost_function = couriers[courier_service]["cost_function"]
        self.max_exemptions = max_exemptions
        self.num_items = len(items)
        self.num_packages = self.num_items  # Initial guess
        self.solution = None
        self.prob = pulp.LpProblem(name="Courier_package_optimization",
                                   sense=pulp.LpMinimize)
    
    def define_problem(self):
        self.x = [[pulp.LpVariable(f"x_{i}_{j}", cat="Binary")
                   for j in range(self.num_items)]
                   for i in range(self.num_items)]
        self.z = [pulp.LpVariable(f"z_{j}",
                                  cat="Binary")
                                  for j in range(self.num_items)]

        # Objective: Minimize total cost (including package costs, import fees)
        total_cost = 0
        for j in range(self.num_items):
            total_weight = pulp.lpSum(
                [self.items[i][1] * self.x[i][j] for i in range(self.num_items)])
            package_price = pulp.lpSum(
                [self.items[i][0] * self.x[i][j] for i in range(self.num_items)])

            # Call the courier service function to get package cost
            # fixed_cost, variable_cost = self.courier_service_cost_function(total_weight)

            # Apply exemption logic
            total_cost += self.z[j] * (fixed_cost + variable_cost)
            total_cost += (1 - pulp.lpSum(self.x[i][j]
                           for i in range(self.num_items))) * 0.6 * package_price

        self.prob += total_cost  # Set the objective to minimize total cost

        # Constraints:
        for j in range(self.num_items):
            # Constraint: total price <= $200
            self.prob += pulp.lpSum([self.items[i][0] * self.x[i][j]
                                    for i in range(self.num_items)]) <= 200 * self.z[j]

            # Constraint: total weight <= 20kg
            self.prob += pulp.lpSum([self.items[i][1] * self.x[i][j]
                                    for i in range(self.num_items)]) <= 20 * self.z[j]

        # Each item must be in exactly one package
        for i in range(self.num_items):
            self.prob += pulp.lpSum([self.x[i][j]
                                    for j in range(self.num_items)]) == 1

        return self.prob
    
    def solve(self):
        """
        Solve the optimization problem using PuLP's CBC solver.
        """
        self.define_problem()  # Set up the problem
        self.prob.solve()  # Solve the problem
        self.solution = {f"x_{i}_{j}": pulp.value(self.x[i][j]) for i in range(self.num_items) for j in range(self.num_items)}
    
    def display_solution(self):
        """
        Display the optimal packaging configuration and costs.
        """
        if self.solution is None:
            print("No solution has been computed yet.")
        else:
            print("Optimal Package Configuration:")
            for j in range(self.num_items):
                package_items = [self.items[i][2] for i in range(self.num_items) if self.solution[f"x_{i}_{j}"] == 1]
                if package_items:
                    print(f"Package {j + 1}: {', '.join(package_items)}")

    def compare_couriers(self, courier_list):
        """
        Compare multiple couriers by running the optimization for each one and comparing the results.
        
        :param courier_list: List of courier service functions to compare.
        """
        results = {}
        for courier in courier_list:
            self.courier_service = courier
            self.solve()
            total_cost = pulp.value(self.prob.objective)
            results[courier.__name__] = total_cost
        
        # Output the comparison
        print("Courier Service Comparison:")
        for courier_name, cost in results.items():
            print(f"{courier_name}: ${cost:.2f}")

# Define data for items: (price, weight, name)
items = [(21.95, 0.1, "Fossil watch"),
         (139.99, 0.2, "Samsung Galaxy S21"),
         (24.6, 1.6, "Redragon Devarajas K556"),
         (24.98, 0.2, "Fossil Diver watch"),
         (118.45, 0.3, "Samsung Galaxy S21 FE"),
         (22.6, 0.3, "Cougar Forza Essential 50")]

optimizer = CourierOptimizer(items, "Urubox")
optimizer.solve()
optimizer.display_solution()
# # Number of items and max packages
# num_items = len(items)
# max_packages = num_items  # At most, each item in its own package

# def solve_with_exemptions(num_exemptions):
#     # Create MILP problem
#     prob = pulp.LpProblem(
#         f"Minimize_Total_Cost_With_{num_exemptions}_Exemptions", pulp.LpMinimize)

#     # Decision variables (same as before)
#     x = [[pulp.LpVariable(f"x_{i}_{j}", cat="Binary")
#           for j in range(max_packages)] for i in range(num_items)]
#     y = [pulp.LpVariable(f"y_{j}", cat="Binary") for j in range(max_packages)]
#     w = [pulp.LpVariable(f"w_{j}", lowBound=0) for j in range(
#         max_packages)]  # Total weight in each package
#     z = [pulp.LpVariable(f"z_{j}", cat="Binary")
#          for j in range(max_packages)]  # Exemption indicator

#     # Objective function: Minimize total cost
#     prob += pulp.lpSum([
#         5 * y[j] +
#         pulp.LpVariable(f"weight_cost_{j}", lowBound=0) +
#         (1 - z[j]) * 0.6 * pulp.lpSum([x[i][j] * items[i][0]
#                                        for i in range(num_items)])  # Import fee
#         for j in range(max_packages)
#     ]), "Minimize_Total_Cost"

#     # Constraints (same as before)
#     for i in range(num_items):
#         prob += pulp.lpSum([x[i][j] for j in range(max_packages)]
#                            ) == 1, f"One_Package_for_Item_{i}"

#     for j in range(max_packages):
#         prob += pulp.lpSum([x[i][j] * items[i][0] for i in range(num_items)]
#                            ) <= 200 * y[j], f"Price_Limit_Package_{j}"
#         prob += pulp.lpSum([x[i][j] * items[i][1] for i in range(num_items)]
#                            ) <= 20 * y[j], f"Weight_Limit_Package_{j}"
#         prob += w[j] == pulp.lpSum([x[i][j] * items[i][1]
#                                    for i in range(num_items)]), f"Weight_Calculation_Package_{j}"

#     # Exemption limit constraint
#     prob += pulp.lpSum([z[j] for j in range(max_packages)]
#                        ) <= num_exemptions, f"Exemption_Limit_{num_exemptions}"

#     # Exemptions valid only for existing packages
#     for j in range(max_packages):
#         prob += z[j] <= y[j], f"Exemption_Valid_Package_{j}"

#     # Solve the problem
#     prob.solve()

#     # Return the total cost and package configuration
#     total_cost = pulp.value(prob.objective)
#     package_configurations = []
#     for j in range(max_packages):
#         if pulp.value(y[j]) > 0:
#             items_in_package = [i for i in range(
#                 num_items) if pulp.value(x[i][j]) > 0]
#             package_configurations.append(
#                 (items_in_package, pulp.value(w[j]), bool(pulp.value(z[j]))))

#     return total_cost, package_configurations

# # Solve for different exemption limits
# for exemptions in range(4):  # 0 to 3 exemptions
#     total_cost, packages = solve_with_exemptions(exemptions)
#     print(f"Total cost with {exemptions} exemptions: {total_cost}")
#     print(f"Package configurations: {packages}")
