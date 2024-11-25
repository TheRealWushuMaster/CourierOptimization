from math import ceil
import pulp
from app.services.routines import *

def cost_result(fixed_rate, variable_rate, total=True):
    package_cost = TransportCost(handling=fixed_rate,
                                 freight=variable_rate)
    if total:
        return package_cost.total
    else:
        return package_cost

def return_rate(weight_steps, total_weight, increments=0):
    for min_weight, max_weight, rate, type in weight_steps:
        if min_weight <= total_weight < max_weight:
            if type == 'f':  # Fixed cost for that range
                return rate
            else:
                if increments>0:
                    total_weight = ceil_in_increments(number=total_weight,
                                                      increments=increments)
                return total_weight * rate

def return_fixed_step_threshold(weight_steps):
    return sum(1 for step in weight_steps if step[3] == 'f')

def package_cost_urubox(total_weight, prob=None, book_cd=False, total=True):
    handling_rate = 5
    weight_steps = [( 0.0,  0.2, 10.9, 'f'),
                    ( 0.2,  0.5, 15.9, 'f'),
                    ( 0.5,  0.7, 18.9, 'f'),
                    ( 0.7,    1, 20.9, 'f'),   # Up to this step, the rate is fixed by step
                    ( 1.0,    5, 19.9, 'l'),   # From this step onwards, the rate
                    ( 5.0, 10.0, 17.9, 'l'),   #   is linear with the total weight
                    (10.0, 20.0, 16.5, 'l'),
                    (20.0, 40.0, 15.9, 'l')]
    num_steps = len(weight_steps)
    if isinstance(total_weight, (int, float)):
        if total_weight == 0:
            return cost_result(fixed_rate=0,
                               variable_rate=0,
                               total=total)
        if book_cd:
            weight_rate = round(max(total_weight, 1)*9.9, COST_DECIMALS)
        else:
            weight_rate = return_rate(weight_steps=weight_steps,
                                      total_weight=total_weight)
        return cost_result(fixed_rate=handling_rate,
                           variable_rate=weight_rate,
                           total=total)
    elif isinstance(total_weight, pulp.LpVariable):
        fixed_step_threshold = return_fixed_step_threshold(weight_steps=weight_steps)
        prob, rates, w_active_vars, w_vars = configure_restrictions(weight_steps=weight_steps,
                                                                    total_weight=total_weight,
                                                                    prob=prob,
                                                                    ceil=False)
        fixed_rate_sum = handling_rate * pulp.lpSum(w_active_vars)
        fixed_step_rate_sum = pulp.lpSum([rates[i] * w_active_vars[i] for i in range(fixed_step_threshold)])
        linear_rate_sum = pulp.lpSum([rates[i] * w_vars[i] for i in range(fixed_step_threshold, num_steps)])
        return fixed_rate_sum + fixed_step_rate_sum + linear_rate_sum

def package_cost_miami_box(total_weight, prob=None, book_cd=False, total=True):
    weight_steps = [( 0.0,  0.4, 10.00, 'f'),
                    ( 0.4, 10.0, 25.90, 'l'),
                    (10.0, 20.0, 23.31, 'l'),
                    (20.0, 30.0, 20.72, 'l')]
    num_steps = len(weight_steps)
    if isinstance(total_weight, (int, float)):
        if total_weight == 0:
            return cost_result(fixed_rate=0,
                               variable_rate=0,
                               total=total)
        if book_cd:
            handling_rate = 2.5
            weight_rate = round(total_weight*9.9, 2)
        else:
            handling_rate = 6
            weight_rate = return_rate(weight_steps=weight_steps,
                                      total_weight=total_weight,
                                      increments=0.1)
        return cost_result(fixed_rate=handling_rate,
                           variable_rate=weight_rate,
                           total=total)
    elif isinstance(total_weight, pulp.LpVariable):
        handling_rate = 6
        fixed_step_threshold = return_fixed_step_threshold(weight_steps=weight_steps)
        prob, rates, w_active_vars, w_vars = configure_restrictions(weight_steps=weight_steps,
                                                                    total_weight=total_weight,
                                                                    prob=prob,
                                                                    ceil=True)
        fixed_rate_sum = handling_rate * pulp.lpSum(w_active_vars)
        fixed_step_rate_sum = rates[0] * w_active_vars[0]
        linear_rate_sum = pulp.lpSum([rates[i] * w_vars[i] for i in range(fixed_step_threshold, num_steps)])
        return fixed_rate_sum + fixed_step_rate_sum + linear_rate_sum

def package_cost_aerobox(total_weight, prob=None, book_cd=False, total=True):
    if book_cd:
        return 0, round(total_weight*11.99, 2)
    fixed_rate = 5*1.22
    fixed_step_threshold = 2
    weight_threshold = 0.601
    weight_steps = [( 0.001,  0.501, 11.99, 'f'),
                    ( 0.501,  0.601, 15.50, 'f'),
                    ( 0.601,  5.001, 23.50, 'l'),
                    ( 5.001, 10.001, 20.50, 'l'),
                    (10.001, 20.001, 17.50, 'l')]
    num_steps = len(weight_steps)
    if isinstance(total_weight, (int, float)):
        if total_weight == 0:
            return cost_result(fixed_rate=0,
                               variable_rate=0,
                               total=total)
        if book_cd:
            handling_rate = 0
            weight_rate = round(max(total_weight, 1)*9.9, COST_DECIMALS)
        else:
            handling_rate = 5 * (1 + VAT_RATE)
            weight_rate = return_rate(weight_steps=weight_steps,
                                      total_weight=total_weight,
                                      increments=0.1)
        return cost_result(fixed_rate=handling_rate,
                           variable_rate=weight_rate,
                           total=total)
    
    
    
    if isinstance(total_weight, (int, float)):
        for min_weight, max_weight, rate in weight_steps:
            if min_weight <= total_weight < max_weight:
                variable_rate = rate if total_weight < weight_threshold else total_weight * rate
                return fixed_rate, round(variable_rate, 2)
    elif isinstance(total_weight, pulp.LpVariable):
        rates = [step[2] for step in weight_steps]
        lowbounds = [step[0] for step in weight_steps]
        upbounds = [step[1] for step in weight_steps]
        w_vars = []
        w_lb_vars = []
        w_ub_vars = []
        w_active_vars = []
        for i in range(num_steps):
            w_var = pulp.LpVariable(f'w{i+1}_{total_weight}', lowBound=0)
            w_lb_var = pulp.LpVariable(f'w{i+1}_{total_weight}_lb', cat='Binary')
            w_ub_var = pulp.LpVariable(f'w{i+1}_{total_weight}_ub', cat='Binary')
            w_active_var = pulp.LpVariable(f'w{i+1}_{total_weight}_active', cat='Binary')
            w_vars.append(w_var)
            w_lb_vars.append(w_lb_var)
            w_ub_vars.append(w_ub_var)
            w_active_vars.append(w_active_var)
        prob += pulp.lpSum(w_active_vars) <= 1
        for i in range(num_steps):
            prob = add_linear_constraints_var_within_limits(result=w_active_vars[i], var=total_weight,
                                                            var_low=w_lb_vars[i], var_high=w_ub_vars[i],
                                                            limit_low=lowbounds[i],
                                                            limit_high=upbounds[i], prob=prob,
                                                            avoid_low_limit=True if i==0 else False)
            prob = add_linear_constraints_prod_bin_cont(result=w_vars[i], bin_var=w_active_vars[i],
                                                        cont_var=total_weight, prob=prob)
        fixed_rate_sum = fixed_rate * pulp.lpSum(w_active_vars)
        fixed_step_rate_sum = pulp.lpSum([rates[i] * w_active_vars[i] for i in range(fixed_step_threshold)])
        linear_rate_sum = pulp.lpSum([rates[i] * w_vars[i] for i in range(fixed_step_threshold, num_steps)])
        return fixed_rate_sum + fixed_step_rate_sum + linear_rate_sum

def package_cost_gripper(total_weight, promo=False, sum=True):
    if promo:
        return 0, round(max(total_weight, 0.6)*12, 2)
    fixed_rate = 5
    weight_threshold = 0.899
    weight_steps = [( 0.001,  0.900, 19.80, 'f'),
                    ( 0.900,  5.001, 21.90, 'l'),
                    ( 5.001, 20.001, 16.50, 'l'),
                    (20.001, 40.001, 13.20, 'l'),
    ]
    for min_weight, max_weight, rate in weight_steps:
        if min_weight <= total_weight <= max_weight:
            variable_rate = rate if total_weight <= weight_threshold else total_weight * rate
            return fixed_rate, round(variable_rate, 2)

def package_cost_punto_mio(total_weight, promo=False, sum=True):
    if promo:
        first_tier = 8.9
        rest_tier = 8.9
        tier = 1
    else:
        first_tier = 13.0
        rest_tier = 8.0
        tier = 0.5
    handling = 5.0
    if total_weight <= 0.5:
        return handling, first_tier
    else:
        variable_cost = round((total_weight-0.5)/tier * rest_tier, 2)
        return handling, first_tier + variable_cost

def package_cost_uruguay_cargo(total_weight, promo=False, sum=True):
    # Confirmar si el handling es por cada paquete sin consolidar
    fixed_rate = 2.5 if promo else 4
    weight_threshold = 0.500
    weight_steps = [
        ( 0.001, 0.500, 14.99),
        ( 0.501,     5, 19.50),
        ( 5.001,    10, 18.99),
        (10.001,    20, 18.20),
    ]
    for min_weight, max_weight, rate in weight_steps:
        if min_weight <= total_weight <= max_weight:
            variable_rate = rate if total_weight <= weight_threshold else total_weight * rate
            return fixed_rate, round(variable_rate, 2)

def package_cost_usx(total_weight, promo=False, sum=True):
    variable_rate = round(ceil(total_weight / 0.1) / 10 * 17.5, 2)
    return 0, variable_rate

def package_cost_exur(total_weight, promo=False, sum=True):
    cost_first_lb = 18.0
    cost_rest_lbs = 7.5
    lbs_per_kg = 2.204623
    weight_lbs = round(total_weight*lbs_per_kg, 2)
    if weight_lbs <= 1:
        return 0, cost_first_lb
    else:
        variable_cost = round(ceil(weight_lbs - 1) * cost_rest_lbs, 2)
        return 0, cost_first_lb + variable_cost

def package_cost_grinbox(total_weight, book_cd=False, total=True):
    weight_steps = [( 0.0, 10.0, 22.0, 'l'),
                    (10.0, 20.0, 19.8, 'l'),
                    (20.0, 40.0, 17.6, 'l')]
    if isinstance(total_weight, (int, float)):
        if total_weight == 0:
            return cost_result(fixed_rate=0,
                               variable_rate=0,
                               total=total)
        if book_cd:
            handling_rate = 3
            weight_rate = 11.0 * total_weight
        else:
            handling_rate = 4
            weight_rate = return_rate(weight_steps=weight_steps,
                                      total_weight=total_weight)
        return cost_result(fixed_rate=handling_rate,
                           variable_rate=weight_rate,
                           total=total)
    elif isinstance(total_weight, pulp.LpVariable):
        pass

def package_cost_melotraigo(total_weight, book_cd=False, total=True):
    weight_steps = [( 0.0,  5.0, 20.9, 'l'),
                    ( 5.0, 10.0, 18.0, 'l'),
                    (10.0, 15.0, 17.0, 'l'),
                    (15.0, 40.0, 16.0, 'l')]
    if isinstance(total_weight, (int, float)):
        if total_weight == 0:
            return cost_result(fixed_rate=0,
                               variable_rate=0,
                               total=total)
        if book_cd:
            handling_rate = 0
            weight_rate = 12.0 * total_weight
        else:
            handling_rate = 5
            weight_rate = return_rate(weight_steps=weight_steps,
                                      total_weight=total_weight)
        return cost_result(fixed_rate=handling_rate,
                           variable_rate=weight_rate,
                           total=total)
    elif isinstance(total_weight, pulp.LpVariable):
        pass

def package_cost_buybox(total_weight, book_cd=False, total=True):
    weight_steps = [( 0.000,  0.501,  5.9, 'f'),
                    ( 0.501,  1.001, 21.0, 'l'),
                    ( 1.001,  3.001, 18.9, 'l'),
                    ( 3.001,  5.001, 16.9, 'l'),
                    ( 5.001, 10.001, 15.9, 'l'),
                    (10.001, 20.001, 13.9, 'l')]
    if isinstance(total_weight, (int, float)):
        if total_weight == 0:
            return cost_result(fixed_rate=0,
                               variable_rate=0,
                               total=total)
        if book_cd:
            handling_rate = 0
            weight_rate = 9.9 * total_weight
        else:
            handling_rate = 5
            weight_rate = return_rate(weight_steps=weight_steps,
                                      total_weight=total_weight)
        return cost_result(fixed_rate=handling_rate,
                           variable_rate=weight_rate,
                           total=total)
    elif isinstance(total_weight, pulp.LpVariable):
        pass

#for i in (1, 2, 5.52, 8, 12, 16, 22.35):
#    print(f"Peso = {i}: {package_cost_miami_box(total_weight=i, book_cd=False):.2f}")
