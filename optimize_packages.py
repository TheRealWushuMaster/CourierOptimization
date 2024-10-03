import pulp
from settings import *
from courier_services import couriers

class CourierOptimizer:
    def __init__(self, items, courier_service, max_packages=None, max_exemptions=MAX_EXEMPTIONS_PER_YEAR):
        self.items = items
        self.courier_service = courier_service
        self.courier_service_cost_function = couriers[courier_service]["cost_function"]
        self.max_packages = max_packages if max_packages is not None else len(items)
        self.model = pulp.LpProblem("CourierOptimization", pulp.LpMinimize)
        self.max_exemptions = max_exemptions
        self.setup_problem()

    def setup_problem(self):
        n_items = len(self.items)
        z = pulp.LpVariable.dicts("use_exemption",
                                  range(self.max_packages),
                                  cat='Binary')
        x = pulp.LpVariable.dicts("assign_item",
                                  (range(n_items),
                                   range(self.max_packages)),
                                  cat='Binary')
        w = pulp.LpVariable.dicts("package_weight",
                                  range(self.max_packages),
                                  lowBound=0,
                                  cat='Continuous')
        p = pulp.LpVariable.dicts("package_price",
                                  range(self.max_packages),
                                  lowBound=0,
                                  cat='Continuous')

        # Objective function: minimize total cost
        total_cost = pulp.lpSum([
            self.package_cost(j, x, z, w, p) for j in range(self.max_packages)])
        self.model += total_cost, "TotalCost"

        # Constraints
        # Ensure each item is assigned to exactly one package
        for i in range(n_items):
            self.model += pulp.lpSum([x[i][j] for j in range(self.max_packages)]) == 1

        # Purchase price and weight restrictions
        for j in range(self.max_packages):
            self.model += pulp.lpSum([x[i][j] * self.items[i][0] for i in range(n_items)]) == p[j]
            self.model += pulp.lpSum([x[i][j] * self.items[i][1] for i in range(n_items)]) == w[j]
            self.model += p[j] <= MAX_PRICE_EXEMPTION
            self.model += w[j] <= MAX_WEIGHT_EXEMPTION

        # Max packages exempt from import fees
        self.model += pulp.lpSum([z[j] for j in range(self.max_packages)]) <= self.max_exemptions

    def package_cost(self, j, x, z, w, p):
        fixed_cost, variable_cost = self.courier_service_cost_function(w[j])
        import_fees = (1 - z[j]) * 0.6 * p[j]
        return fixed_cost + variable_cost + import_fees

    def solve(self):
        self.model.solve()
        return self.get_results()

    def get_results(self):
        if pulp.LpStatus[self.model.status] != "Optimal":
            raise Exception("No optimal solution found")

        assignments = {}
        for i in range(len(self.items)):
            for j in range(self.max_packages):
                if pulp.value(self.model.variablesDict()[f'assign_item_{i}_{j}']) == 1:
                    assignments[f"Package_{j}"] = assignments.get(f"Package_{j}", []) + [f"Item_{i}"]
        return assignments

items = [(21.95, 0.1, "Fossil watch"),
         (139.99, 0.2, "Samsung Galaxy S21"),
         (24.6, 1.6, "Redragon Devarajas K556"),
         (24.98, 0.2, "Fossil Diver watch"),
         (118.45, 0.3, "Samsung Galaxy S21 FE"),
         (22.6, 0.3, "Cougar Forza Essential 50")]

optimizer = CourierOptimizer(items, "Urubox")
result = optimizer.solve()
print(result)