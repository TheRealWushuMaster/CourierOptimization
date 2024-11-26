from app.core.config import *
import pulp
from math import ceil

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
        self.total_package_cost = transport_cost.total + import_fee

class PackageSolution:
    def __init__(self, courier, solutions=0):
        self.packages = []              # List of Package objects
        self.total_weight = 0           # Total weight of all packages
        self.total_price = 0            # Total price of all packages
        self.total_transport_cost = TransportCost.zero()
                                        # Total transport cost of all packages
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
        self.total_cost += package.transport_cost.total + package.import_fee
    
    def __str__(self):
        result  = f"Optimal solution found for courier {self.courier}:\n"
        result += '\n'
        for i, package in enumerate(self.packages):
            result += f"* Package {i+1}:\n"
            result +=  "  ==========\n"
            result += '\n'
            result +=  "  - Items included:\n"
            for n, item in enumerate(package.items):
                result += f"      {n+1}. {item[0]} (USD {item[1]}, {item[2]} kg)\n"
            result += '\n'
            result +=  "  - Package information:\n"
            result += f"    Total price:     USD {package.total_price:.2f}\n"
            result += f"    Total weight:        {package.total_weight:.2f} kg\n"
            result += '\n'
            result +=  "  - Costs information:\n"
            result +=  "    Transport costs:\n"
            result += f"      * Handling:  USD {package.transport_cost.handling:.2f}\n"
            result += f"      * Freight:   USD {package.transport_cost.freight:.2f}\n"
            result += f"      * Subtotal:  USD {package.transport_cost.subtotal:.2f}\n"
            result += f"      * Tax:       USD {package.transport_cost.tax:.2f}\n"
            result += f"      * TFSPU:     USD {package.transport_cost.TFSPU:.2f}\n"
            result += f"      * Total:     USD {package.transport_cost.total:.2f}\n"
            result += f"    Import fee:      USD {package.import_fee:.2f}"+(" (fee exempted)" if package.import_fee_exempted else "")+'\n'
            result += '\n'
            result += f"    Total cost:      USD {package.total_package_cost:.2f}\n"
            result += '\n'
        result += "---\n"
        result += "Totals:\n"
        result += f"Total price:         USD {self.total_price:.2f}\n"
        result += f"Total weight:            {self.total_weight:.2f} kg\n"
        result += '\n'
        result +=  "Total transport costs:\n"
        result += f"  * Handling:  USD {self.total_transport_cost.handling:.2f}\n"
        result += f"  * Freight:   USD {self.total_transport_cost.freight:.2f}\n"
        result += f"  * Subtotal:  USD {self.total_transport_cost.subtotal:.2f}\n"
        result += f"  * Tax:       USD {self.total_transport_cost.tax:.2f}\n"
        result += f"  * TFSPU:     USD {self.total_transport_cost.TFSPU:.2f}\n"
        result += f"  * Total:     USD {self.total_transport_cost.total:.2f}\n"
        result += f"Total import fee:    USD {self.total_import_fee:.2f}\n"
        result += '\n'
        result += f"Total cost:          USD {self.total_cost:.2f}\n"
        if self.solutions > 0:
            result += '\n'
            result += f"Solutions analyzed:  {self.solutions}"
        return result
    
    def show(self):
        print(self)
    
    def save_to_file(self, filename='solution_details.log'):
        try:
            with open(filename, 'w') as file:
                print(self, file=file)
            print(f"File '{filename}' saved successfully.")
        except IOError as e:
            print(f"Error saving file '{filename}': {e}")

class TransportCost:
    def __init__(self, handling, freight):
        self.handling = round(handling, COST_DECIMALS)
        self.freight = round(freight, COST_DECIMALS)
        self.subtotal = self.handling + self.freight
        self.tax = round(TAX_ON_FREIGHT * freight, COST_DECIMALS)
        self.TFSPU = round(self.freight * TFSPU_RATE, COST_DECIMALS)
        self.total = round(self.subtotal + self.tax + self.TFSPU, COST_DECIMALS)
    
    @classmethod
    def zero(cls):
        return cls(handling=0, freight=0)
    
    def __add__(self, other):
        if not isinstance(other, TransportCost):
            raise TypeError(f"Unsupported operand type(s) for +: '{type(self).__name__}' and '{type(other).__name__}'")
        addition = object.__new__(TransportCost)
        addition.handling = round(self.handling + other.handling, COST_DECIMALS)
        addition.freight = round(self.freight + other.freight, COST_DECIMALS)
        addition.subtotal = round(self.subtotal + other.subtotal, COST_DECIMALS)
        addition.tax = round(self.tax + other.tax, COST_DECIMALS)
        addition.TFSPU = round(self.TFSPU + other.TFSPU, COST_DECIMALS)
        addition.total = round(self.total + other.total, COST_DECIMALS)
        return addition

    def __str__(self):
        output  = f'- Handling: USD {self.handling}\n'
        output += f'- Freight:  USD {self.freight}\n'
        output += f'- Subtotal: USD {self.subtotal}\n'
        output +=  '  =========\n'
        output += f'- Tax:      USD {self.tax}\n'
        output += f'- TFSPU:    USD {self.TFSPU}\n'
        output += f'- Total:    USD {self.total}'
        return output 

    def show(self):
        print(self)

# METHODS
# =======
def ceil_in_increments(number, increments):
    return ceil(number / increments) * increments

# ADD RESTRAINTS FOR COMMON CONDITIONS
# ====================================
def configure_restrictions(weight_steps, total_weight, prob, ceil=None):
    rates = [step[2] for step in weight_steps]
    lowbounds = [step[0] for step in weight_steps]
    upbounds = [step[1] for step in weight_steps]
    num_steps = len(weight_steps)
    w_vars = []
    w_lb_vars = []
    w_ub_vars = []
    w_active_vars = []
    w_ceil_int_vars = []
    if ceil:
        w_ceil_vars = []
    for i in range(num_steps):
        w_var = pulp.LpVariable(f'w{i+1}_{total_weight}', lowBound=0)
        w_lb_var = pulp.LpVariable(
            f'w{i+1}_{total_weight}_lb', cat='Binary')
        w_ub_var = pulp.LpVariable(
            f'w{i+1}_{total_weight}_ub', cat='Binary')
        w_active_var = pulp.LpVariable(
            f'w{i+1}_{total_weight}_active', cat='Binary')
        w_vars.append(w_var)
        w_lb_vars.append(w_lb_var)
        w_ub_vars.append(w_ub_var)
        w_active_vars.append(w_active_var)
        if ceil:
            w_ceil_int_var = pulp.LpVariable(f'w{i+1}_{total_weight}_ceil_int', lowBound=0, cat='Integer')
            w_ceil_var = pulp.LpVariable(f'w{i+1}_{total_weight}_ceil', lowBound=0)
            w_ceil_int_vars.append(w_ceil_int_var)
            w_ceil_vars.append(w_ceil_var)
    prob += pulp.lpSum(w_active_vars) <= 1
    for i in range(num_steps):
        if ceil:
            prob = add_linear_constraints_ceil(result=w_ceil_vars[i], var=total_weight,
                                               int_var=w_ceil_int_vars[i], prob=prob, precision=ceil)
            prob = add_linear_constraints_prod_bin_cont(result=w_vars[i], bin_var=w_active_vars[i],
                                                        cont_var=w_ceil_vars[i], prob=prob)
        else:
            prob = add_linear_constraints_prod_bin_cont(result=w_vars[i], bin_var=w_active_vars[i],
                                                        cont_var=total_weight, prob=prob)
        prob = add_linear_constraints_var_within_limits(result=w_active_vars[i], var=total_weight,
                                                        var_low=w_lb_vars[i], var_high=w_ub_vars[i],
                                                        limit_low=lowbounds[i],
                                                        limit_high=upbounds[i], prob=prob,
                                                        avoid_low_limit=True if i == 0 else False)
    return prob, rates, w_active_vars, w_vars

def add_linear_constraints_var_within_limits(result, var, var_low, var_high,
                                             limit_low, limit_high, prob,
                                             avoid_low_limit=False):
    # If avoid_low = True: result = True if limit_low < var < limit_high
    # If avoid_low = False: result = True if limit_low <= var < limit_high
    if avoid_low_limit:
        prob = add_linear_constraints_var_greater_than_value(result=var_low, var=var,
                                                              value=limit_low, prob=prob)
    else:
        prob = add_linear_constraints_var_greater_than_or_equal_value(result=var_low, var=var,
                                                                      value=limit_low, prob=prob)
    prob = add_linear_constraints_var_less_than_value(result=var_high, var=var,
                                                      value=limit_high, prob=prob)
    prob = add_linear_contraints_multiply_binary_vars(result=result, var1=var_low,
                                                      var2=var_high, prob=prob)
    return prob

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
    # result = True if var > value
    prob += var - value <= M * result
    return prob

def add_linear_constraints_var_less_than_value(result, var, value, prob):
    # result = True if var < value
    prob += value - var <= M * result
    return prob

def add_linear_constraints_var_greater_than_or_equal_value(result, var, value, prob):
    # result = True if var >= value, assuming a tolerance
    prob += var - (value - MIN_TOLERANCE) <= M * result
    return prob

def add_linear_constraints_var_less_than_or_equal_value(result, var, value, prob):
    # result = True if var <= value, assuming a tolerance
    prob += value - (var + MIN_TOLERANCE) <= M * result
    return prob

def add_linear_constraints_ceil(result, var, int_var, prob, precision=1):
    # result = ceil(var)
    prob += int_var >= var * 1/precision
    prob += int_var <= var * 1/precision + 1 - MIN_TOLERANCE
    prob += result == int_var * precision
    return prob

def add_linear_constraints_floor(result, var, int_var, prob, precision=1):
    # result = floor(var)
    prob += int_var <= var * 1/precision
    prob += int_var >= var * 1/precision - 1 + MIN_TOLERANCE
    prob += result == int_var * precision
    return prob

def add_linear_contraints_multiply_binary_vars(result, var1, var2, prob):
    # result = var1 * var2
    prob += result <= var1
    prob += result <= var2
    prob += result >= var1 + var2 - 1
    return prob
