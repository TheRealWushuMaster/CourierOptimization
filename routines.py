from settings import M, MIN_TOLERANCE

# CLASSES
# =======
class Package:
    def __init__(self, items, total_price, total_weight, transport_cost,
                 import_fee, import_fee_exemption):
        self.items = items  # List of tuples (name, price, weight)
        self.total_price = total_price
        self.total_weight = total_weight
        self.transport_cost = transport_cost
        self.import_fee = import_fee
        self.import_fee_exempted = import_fee_exemption  # Boolean: whether the package is exempted or not
        self.total_package_cost = transport_cost + import_fee

class PackageSolution:
    def __init__(self, courier, solutions=0):
        self.packages = []              # List of Package objects
        self.total_weight = 0           # Total weight of all packages
        self.total_price = 0            # Total price of all packages
        self.total_transport_cost = 0   # Total transport cost of all packages
        self.total_import_fee = 0       # Total import fees of all packages
        self.total_cost = 0             # Total cost including transport and import fees
        self.courier = courier
        self.solutions = solutions
    
    def add_package(self, package):
        self.packages.append(package)
        self.total_weight += package.total_weight
        self.total_price += package.total_price
        self.total_transport_cost += package.transport_cost
        self.total_import_fee += package.import_fee
        self.total_cost += package.transport_cost + package.import_fee

# METHODS
# =======
def display_solution(solution, filename=None):
    if filename!=None:
        print(f"Saving solution details to {filename}")
        filename = open(filename, "w")
    print(f"Optimal solution found for courier {solution.courier}:", file=filename)
    print("", file=filename)
    for i, package in enumerate(solution.packages):
        print(f"* Package {i+1}:", file=filename)
        print("  ==========", file=filename)
        print("", file=filename)
        print("  - Items included:", file=filename)
        for n, item in enumerate(package.items):
            print(f"      {n+1}. {item[0]} (USD {item[1]}, {item[2]} kg)", file=filename)
        print("", file=filename)
        print("  - Package information:", file=filename)
        print(f"    Total price:     USD {package.total_price:.2f}", file=filename)
        print(f"    Total weight:        {package.total_weight:.2f} kg", file=filename)
        print("", file=filename)
        print("  - Costs information:", file=filename)
        print(f"    Transport cost:  USD {package.transport_cost:.2f}", file=filename)
        print(f"    Import fee:      USD {package.import_fee:.2f}"+(" (fee exempted)" if package.import_fee_exempted else ""), file=filename)
        print("", file=filename)
        print(f"    Total cost:      USD {package.total_package_cost:.2f}", file=filename)
        print("", file=filename)
    print("---", file=filename)
    print("Totals:", file=filename)
    print(f"Total price:           USD {solution.total_price:.2f}", file=filename)
    print(f"Total weight:              {solution.total_weight:.2f} kg", file=filename)
    print("", file=filename)
    print(f"Total transport cost:  USD {solution.total_transport_cost:.2f}", file=filename)
    print(f"Total import fee:      USD {solution.total_import_fee:.2f}", file=filename)
    print("", file=filename)
    print(f"Total cost:            USD {solution.total_cost:.2f}", file=filename)
    if solution.solutions > 0:
        print("", file=filename)
        print(f"Solutions analyzed:    {solution.solutions}", file=filename)

# ADD RESTRAINTS FOR COMMON CONDITIONS
# ====================================
def add_linear_constraints_max(result, value1, value2, auxiliary_var, prob):
    # result = max(value1, value2)
    prob += result >= value1
    prob += result >= value2
    prob += result <= value1 + M * (1 - auxiliary_var)
    prob += result <= value2 + M * auxiliary_var
    return prob

def add_linear_constraints_min(result, value1, value2, auxiliary_var, prob):
    # result = min(value1, value2)
    prob += result <= value1
    prob += result <= value2
    prob += result >= value1 - M * (1 - auxiliary_var)
    prob += result >= value2 - M * auxiliary_var
    return prob

def add_linear_constraints_prod_bin_cont(result, bin_var, cont_var, prob):
    # result = bin_var * cont_var
    prob += result >= cont_var - M * (1 - bin_var)
    return prob

def add_linear_constraints_var_greater_than_value(result, var, value, prob):
    prob += var - value <= M * result
    return prob

def add_linear_constraints_var_less_than_value(result, var, value, prob):
    prob += value - var <= M * result
    return prob

def add_linear_constraints_var_greater_than_or_equal_value(result, var, value, prob):
    prob += var + MIN_TOLERANCE - value <= M * result
    return prob

def add_linear_constraints_var_less_than_or_equal_value(result, var, value, prob):
    prob += value - var - MIN_TOLERANCE <= M * result
    return prob

def add_linear_constraints_ceil(result, var, prob):
    # result = ceil(var)
    prob += result >= var
    prob += result <= var + 0.999
    return prob

def add_linear_constraints_floor(result, var, prob):
    # result = floor(var)
    prob += result >= var - 0.999
    prob += result <= var
    return prob

def add_linear_contraints_multiply_binary_vars(result, var1, var2, prob):
    # result = var1 * var2
    prob += result <= var1
    prob += result <= var2
    prob += result >= var1 + var2 - 1
    return prob
