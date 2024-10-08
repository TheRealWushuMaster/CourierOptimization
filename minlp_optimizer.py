import pulp
from settings import *
from routines import *

def minlp_optimization(courier, items, max_packages=None,
                       max_exemptions=MAX_EXEMPTIONS_PER_YEAR):
    num_items = len(items)
    if max_packages == None:
        num_packages = num_items
    elif max_packages > num_items:
        num_packages = num_items
    elif max_packages < 1:
        num_packages = 1
    if max_exemptions>MAX_EXEMPTIONS_PER_YEAR:
        max_exemptions = MAX_EXEMPTIONS_PER_YEAR
    elif max_exemptions < 0:
        max_exemptions = 0

    # Couriers and costs (stepwise functions)
    def courier_cost(weight, prob):
        if isinstance(weight, float):
            if weight==0:
                return 0
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

    # Initialize PuLP problem
    prob = pulp.LpProblem("Minimize_Import_Costs", pulp.LpMinimize)
    # Binary variable: whether item i is in package j
    x = pulp.LpVariable.dicts("x", ((i, j) for i in range(num_items) for j in range(num_packages)), cat='Binary')
    # Weight of each package
    weight = pulp.LpVariable.dicts("weight", range(num_packages), lowBound=0)
    # Price of each package
    package_price = pulp.LpVariable.dicts("package_price", range(num_packages), lowBound=0)
    # Binary variable for whether each package is exempt from import fee
    import_fee_exempted = pulp.LpVariable.dicts("import_fee_exempted", range(num_packages), cat='Binary')
    # Import fee cost (will be zero if the package is exempted)
    import_fee_cost = pulp.LpVariable.dicts("import_fee_cost", range(num_packages), lowBound=0)
    nominal_import_fee = pulp.LpVariable.dicts("nominal_import_fee", range(num_packages), lowBound=0)
    import_fee_above_min = pulp.LpVariable.dicts("import_fee_above_min", range(num_packages), lowBound=0, upBound=1, cat='Integer')
    # Transport cost for each package
    transport_cost = pulp.LpVariable.dicts("transport_cost", range(num_packages), lowBound=0)
    # Total cost for each package
    total_package_cost = pulp.LpVariable.dicts("total_package_cost", range(num_packages), lowBound=0)

    M = 10000   # Big-M constraint

    # RESTRICTIONS
    # ============
    # All items must be included on a single package
    for i in range(num_items):
        prob += pulp.lpSum(x[i, j] for j in range(num_packages)) == 1
    # Price and weight constraints
    for j in range(num_packages):
        prob += package_price[j] == pulp.lpSum([items[i][1] * x[i, j]
                                                for i in range(num_items)])
        prob += package_price[j] <= MAX_PRICE_EXEMPTION # Price constraint
        prob += weight[j] == pulp.lpSum([items[i][2] * x[i, j] for i in range(num_items)])  # Weight constraint
        prob += weight[j] <= MAX_WEIGHT_EXEMPTION  # Max weight constraint
        prob += transport_cost[j] == courier_cost(weight[j], prob)
        
        prob += nominal_import_fee[j] == IMPORT_FEE_PERCENT * package_price[j]
        
                
        prob += import_fee_cost[j] >= nominal_import_fee[j]
        
        prob += import_fee_cost[j] <= IMPORT_FEE_PERCENT * package_price[j] #+ M * min_fee_active[j]
        prob += import_fee_cost[j] >= IMPORT_FEE_PERCENT * package_price[j] - M * import_fee_exempted[j]    # When not exempt import_fee_exempted[j] == 0
        prob += import_fee_cost[j] <= M * (1 - import_fee_exempted[j])  # Should be zero if exempt import_fee_exempted[j] == 1
        
        
        # prob += import_fee_cost[j] >= MINIMUM_FEE_PAYMENT - M * import_fee_exempted[j]
        # prob += import_fee_cost[j] <= nominal_import_fee[j] + M * (1 - import_fee_above_min[j])
        # prob += import_fee_cost[j] <= MINIMUM_FEE_PAYMENT + M * (1 - import_fee_above_min[j])
        # prob += import_fee_cost[j] >= MINIMUM_FEE_PAYMENT - M * (1 - import_fee_above_min[j])
        # prob += nominal_import_fee[j] - MINIMUM_FEE_PAYMENT <= M * import_fee_above_min[j]
        # prob += nominal_import_fee[j] - MINIMUM_FEE_PAYMENT >= -M * (1 - import_fee_above_min[j])
        
        # prob += import_fee_cost[j] <= nominal_import_fee[j] + M * import_fee_exempted[j]
        # prob += import_fee_cost[j] >= nominal_import_fee[j] - M * import_fee_exempted[j]
        # prob += import_fee_cost[j] <= M * (1 - import_fee_exempted[j])
        # prob += import_fee_cost[j] >= MINIMUM_FEE_PAYMENT - M * import_fee_exempted[j]
        # prob += import_fee_cost[j] <= MINIMUM_FEE_PAYMENT + M * (1 - import_fee_above_min[j])
        # prob += nominal_import_fee[j] <= MINIMUM_FEE_PAYMENT + M * import_fee_above_min[j]
        # prob += nominal_import_fee[j] >= MINIMUM_FEE_PAYMENT - M * (1 - import_fee_above_min[j])
        # prob += import_fee_above_min[j] <= 1 - import_fee_exempted[j]
        
        
        
        prob += total_package_cost[j] == transport_cost[j] + import_fee_cost[j]
    # Limit the number of import fee exemptions
    prob += pulp.lpSum([import_fee_exempted[j] for j in range(num_packages)]) <= max_exemptions
    # Objective function: Minimize the total cost (courier fee + import fee)
    prob += pulp.lpSum([transport_cost[j] + import_fee_cost[j]
                        for j in range(num_packages)])
    # Solve the problem
    prob.solve()
    # Create an object with the optimal solution
    optimal_solution = PackageSolution(courier=courier)
    for j in range(num_packages):
        assigned_items = [(items[i][0], items[i][1], items[i][2]) for i in range(num_items) if pulp.value(x[i, j]) == 1]
        if assigned_items:
            total_price = sum(item[1] for item in assigned_items)
            total_weight = sum(item[2] for item in assigned_items)
            transport_cost = pulp.value(courier_cost(total_weight, prob))
            import_fee = pulp.value(import_fee_cost[j])
            import_fee_exemption = bool(pulp.value(import_fee_exempted[j]))
            # Create a Package object
            package = Package(items=assigned_items,
                              total_price=total_price,
                              total_weight=total_weight,
                              transport_cost=transport_cost,
                              import_fee=import_fee,
                              import_fee_exemption=import_fee_exemption)
            optimal_solution.add_package(package)
    return optimal_solution

