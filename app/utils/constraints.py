from app.core.config import *
import pulp

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
