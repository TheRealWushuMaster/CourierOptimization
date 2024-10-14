import pulp
from settings import *
from routines import *
from courier_services import *

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
    courier_cost = couriers[courier]["cost_function"]
    # Initialize PuLP problem
    prob = pulp.LpProblem("Minimize_Import_Costs", pulp.LpMinimize)
    # Binary variable: whether item i is in package j
    x = pulp.LpVariable.dicts("x", ((i, j) for i in range(num_items) for j in range(num_packages)), cat='Binary')
    # Weight of each package
    weight = pulp.LpVariable.dicts("weight", range(num_packages), lowBound=0)
    # Price of each package
    package_price = pulp.LpVariable.dicts("package_price", range(num_packages), lowBound=0)
    package_price_is_positive = pulp.LpVariable.dicts("package_price_is_positive", range(num_packages), cat='Binary')
    # Binary variable for whether each package is exempt from import fee
    import_fee_exempted = pulp.LpVariable.dicts("import_fee_exempted", range(num_packages), cat='Binary')
    # Import fee cost (will be zero if the package is exempted)
    import_fee_cost = pulp.LpVariable.dicts("import_fee_cost", range(num_packages), lowBound=0)
    nominal_import_fee = pulp.LpVariable.dicts("nominal_import_fee", range(num_packages), lowBound=0)
    final_import_fee = pulp.LpVariable.dicts("final_import_fee", range(num_packages), lowBound=0)
    # Auxiliary variable to calculate import fee with low cap
    y = pulp.LpVariable.dicts("y", range(num_packages), lowBound=0, upBound=1, cat='Integer')
    # Transport cost for each package
    transport_cost = pulp.LpVariable.dicts("transport_cost", range(num_packages), lowBound=0)
    # Total cost for each package
    total_package_cost = pulp.LpVariable.dicts("total_package_cost", range(num_packages), lowBound=0)
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
        #prob += package_price[j] <= M * package_price_is_positive[j]
        prob = add_linear_constraints_var_greater_than_value(result=package_price_is_positive[j],
                                                             var=package_price[j],
                                                             value=0,
                                                             prob=prob)
        prob += weight[j] == pulp.lpSum([items[i][2] * x[i, j] for i in range(num_items)])  # Weight constraint
        prob += weight[j] <= MAX_WEIGHT_EXEMPTION  # Max weight constraint
        prob += transport_cost[j] == courier_cost(weight[j], prob)
        # Import fee calculation
        prob += nominal_import_fee[j] == IMPORT_FEE_PERCENT * package_price[j]
        # Import fee is lower-capped at MINIMUM_FEE_PAYMENT
        prob = add_linear_constraints_max(result=import_fee_cost[j],
                                          value1=nominal_import_fee[j],
                                          value2=MINIMUM_FEE_PAYMENT,
                                          auxiliary_var=y[j],
                                          prob=prob)
        prob += final_import_fee[j] >= import_fee_cost[j] \
            - M * import_fee_exempted[j] - M * (1 - package_price_is_positive[j]) # If package price is zero, import fee is zero
        # Calculate total package cost
        prob += total_package_cost[j] == transport_cost[j] + final_import_fee[j]
    # Limit the number of import fee exemptions
    prob += pulp.lpSum([import_fee_exempted[j] for j in range(num_packages)]) <= max_exemptions
    # Objective function: Minimize the total cost (courier fee + import fee)
    prob += pulp.lpSum([total_package_cost[j] for j in range(num_packages)])
    # Solve the problem
    prob.solve()
    print(prob)
    for var in prob.variables():
        print(var.name, "==>", var.varValue)
    print(f"Objective = {pulp.value(prob.objective)}")
    # Create an object with the optimal solution
    optimal_solution = PackageSolution(courier=courier)
    for i, pack in enumerate(optimal_solution.packages):
        print(i+1)
        print(pack)
        print()
    for j in range(num_packages):
        assigned_items = [(items[i][0], items[i][1], items[i][2]) for i in range(num_items) if pulp.value(x[i, j]) == 1]
        if assigned_items:
            total_price = sum(item[1] for item in assigned_items)
            total_weight = sum(item[2] for item in assigned_items)
            transport_cost = pulp.value(courier_cost(total_weight, prob))
            import_fee = pulp.value(final_import_fee[j])
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
