from math import ceil
import pulp
from routines import *

def return_result(fixed_rate, variable_rate, sum=True):
    if sum:
        return fixed_rate + variable_rate
    else:
        return fixed_rate, variable_rate

def package_cost_test(total_weight, prob=None, promo=False, sum=True):
    fixed_rate = 0
    if isinstance(total_weight, float):
        if total_weight==0:
            return return_result(0, 0, sum)
        elif total_weight <= 1:
            variable_rate = 5
        elif total_weight <= 2:
            variable_rate = 5 + (total_weight - 1) * 4
        else:
            variable_rate = 5 + 4 + (total_weight - 2) * 3.5
        return return_result(fixed_rate, variable_rate, sum)
    elif isinstance(total_weight, pulp.LpVariable):
        w1 = pulp.LpVariable(f'w1_{total_weight}', lowBound=0, upBound=1)
        aux1 = pulp.LpVariable(f'w1_{total_weight}_aux', cat='Binary')
        w2 = pulp.LpVariable(f'w2_{total_weight}', lowBound=0, upBound=1)
        aux2 = pulp.LpVariable(f'w2_{total_weight}_aux', cat='Binary')
        w2_active = pulp.LpVariable(f'w2_{total_weight}_active', cat='Binary')
        w3 = pulp.LpVariable(f'w3_{total_weight}', lowBound=0)
        aux3 = pulp.LpVariable(f'w3_{total_weight}_aux', cat='Binary')
        w3_active = pulp.LpVariable(f'w3_{total_weight}_active', cat='Binary')
        prob += total_weight == w1 + w2 + w3  # Ensure weight constraints
        prob = add_linear_constraints_min(result=w1,
                                          value1=1,
                                          value2=total_weight,
                                          auxiliary_var=aux1,
                                          prob=prob)
        prob = add_linear_constraints_var_greater_than_value(result=w2_active,
                                                             var=total_weight,
                                                             value=1,
                                                             prob=prob)
        prob = add_linear_constraints_min(result=w2,
                                          value1=1*w2_active,
                                          value2=total_weight-1 + M *
                                          (1 - w2_active),
                                          auxiliary_var=aux2,
                                          prob=prob)
        prob = add_linear_constraints_var_greater_than_value(result=w3_active,
                                                             var=total_weight,
                                                             value=2,
                                                             prob=prob)
        prob = add_linear_constraints_min(result=w3,
                                          value1=1*w3_active,
                                          value2=total_weight-2 + M *
                                          (1 - w3_active),
                                          auxiliary_var=aux3,
                                          prob=prob)
        return 5 * w1 + 4 * w2 + 3.5 * w3

def package_cost_urubox(total_weight, prob=None, promo=False, sum=True):
    fixed_rate = 5
    fixed_step_threshold = 4
    weight_steps = [( 0.0,  0.2, 10.9),
                    ( 0.2,  0.5, 15.9),
                    ( 0.5,  0.7, 18.9),
                    ( 0.7,    1, 20.9),   # Up to this step, the rate is fixed by step
                    ( 1.0,    5, 19.9),   # From this step onwards, the rate
                    ( 5.0, 10.0, 17.9),   #   is linear with the total weight
                    (10.0, 20.0, 16.5),
                    (20.0, 40.0, 15.9)]
    num_steps = len(weight_steps)
    weight_threshold = 1
    if isinstance(total_weight, (int, float)):
        if total_weight == 0:
            return return_result(fixed_rate=0,
                                 variable_rate=0,
                                 sum=sum)
        if promo:
            return return_result(fixed_rate=fixed_rate,
                                 variable_rate=round(max(total_weight, 1)*9.9, 2),
                                 sum=sum)
        for min_weight, max_weight, rate in weight_steps:
            if min_weight <= total_weight < max_weight:
                variable_rate = rate if total_weight < weight_threshold else total_weight * rate
                return return_result(fixed_rate=fixed_rate,
                                     variable_rate=variable_rate,
                                     sum=sum)
    elif isinstance(total_weight, pulp.LpVariable):
        prob, rates, w_active_vars, w_vars = configure_restrictions(weight_steps=weight_steps,
                                                                    total_weight=total_weight,
                                                                    prob=prob,
                                                                    ceil=False)
        fixed_rate_sum = fixed_rate * pulp.lpSum(w_active_vars)
        fixed_step_rate_sum = pulp.lpSum([rates[i] * w_active_vars[i] for i in range(fixed_step_threshold)])
        linear_rate_sum = pulp.lpSum([rates[i] * w_vars[i] for i in range(fixed_step_threshold, num_steps)])
        return fixed_rate_sum + fixed_step_rate_sum + linear_rate_sum

def package_cost_miami_box(total_weight, prob=None, promo=False, sum=True):
    fixed_rate = 6
    cost_per_100_gr = 2.59
    fixed_step_threshold = 1
    weight_steps = [( 0.0,  0.4, 10.0),
                    ( 0.4, 10.0,  1.0),
                    (10.0, 20.0,  0.9),
                    (20.0, 30.0,  0.8)]
    num_steps = len(weight_steps)
    if isinstance(total_weight, (int, float)):
        if promo:
            return return_result(fixed_rate=2.5,
                                variable_rate=round(total_weight*9.9, 2),
                                sum=sum)
        if total_weight >= 30:
            return return_result(fixed_rate=0,
                                variable_rate=0,
                                sum=sum)
        elif total_weight < 0.4:
            return return_result(fixed_rate=fixed_rate,
                                variable_rate=weight_steps[0][2],
                                sum=sum)
        variable_rate = ceil(total_weight / 0.1) * cost_per_100_gr
        if total_weight >= 20:
            variable_rate *= 0.8
        elif total_weight >= 10:
            variable_rate *= 0.9
        return return_result(fixed_rate=fixed_rate,
                            variable_rate=round(variable_rate, 2),
                            sum=sum)
    elif isinstance(total_weight, pulp.LpVariable):
        prob, rates, w_active_vars, w_vars = configure_restrictions(weight_steps=weight_steps,
                                                                    total_weight=total_weight,
                                                                    prob=prob,
                                                                    ceil=True)
        fixed_rate_sum = fixed_rate * pulp.lpSum(w_active_vars)
        fixed_step_rate_sum = rates[0] * w_active_vars[0] #pulp.lpSum([rates[i] * w_active_vars[i] for i in range(fixed_step_threshold)])
        linear_rate_sum = pulp.lpSum([10*cost_per_100_gr*rates[i] * w_vars[i] for i in range(fixed_step_threshold, num_steps)])
        return fixed_rate_sum + fixed_step_rate_sum + linear_rate_sum

def package_cost_aerobox(total_weight, promo=False, sum=True):
    if promo:
        return 0, round(total_weight*11.99, 2)
    fixed_rate = 5*1.22
    fixed_step_threshold = 2
    weight_threshold = 0.601
    weight_steps = [( 0.001,  0.501, 11.99),
                    ( 0.501,  0.601, 15.50),
                    ( 0.601,  5.001, 23.50),
                    ( 5.001, 10.001, 20.50),
                    (10.001, 20.001, 17.50)]
    num_steps = len(weight_steps)
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
    weight_steps = [
        ( 0.001, 0.899, 19.80),
        ( 0.900,     5, 21.90),
        ( 5.001,    20, 16.50),
        (20.001,    40, 13.20),
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
