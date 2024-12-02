from math import ceil
import pulp
from app.services.routines import *

# ROUTINES
# ========
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

# COST FUNCTIONS
# ==============
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
                                                                    ceil=None)
        fixed_rate_sum = handling_rate * pulp.lpSum(w_active_vars)
        fixed_step_rate_sum = pulp.lpSum([rates[i] * w_active_vars[i] for i in range(fixed_step_threshold)])
        linear_rate_sum = pulp.lpSum([rates[i] * w_vars[i] for i in range(fixed_step_threshold, num_steps)])
        return cost_result(fixed_rate=fixed_rate_sum,
                           variable_rate=fixed_step_rate_sum + linear_rate_sum,
                           total=total)

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
                                                                    ceil=0.1)
        fixed_rate_sum = handling_rate * pulp.lpSum(w_active_vars)
        fixed_step_rate_sum = rates[0] * w_active_vars[0]
        linear_rate_sum = pulp.lpSum([rates[i] * w_vars[i] for i in range(fixed_step_threshold, num_steps)])
        return cost_result(fixed_rate=fixed_rate_sum,
                            variable_rate=fixed_step_rate_sum + linear_rate_sum,
                            total=total)

def package_cost_aerobox(total_weight, prob=None, book_cd=False, total=True):
    if book_cd:
        return 0, round(total_weight*11.99, 2)
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
        else:
            handling_rate = 5 * (1 + VAT_RATE)
        weight_rate = return_rate(weight_steps=weight_steps,
                                  total_weight=total_weight,
                                  increments=0.1)
        return cost_result(fixed_rate=handling_rate,
                           variable_rate=weight_rate,
                           total=total)
    elif isinstance(total_weight, pulp.LpVariable):
        handling_rate = 5 * (1 + VAT_RATE)
        fixed_step_threshold = return_fixed_step_threshold(weight_steps=weight_steps)
        prob, rates, w_active_vars, w_vars = configure_restrictions(weight_steps=weight_steps,
                                                                    total_weight=total_weight,
                                                                    prob=prob,
                                                                    ceil=0.1)
        fixed_rate_sum = handling_rate * pulp.lpSum(w_active_vars)
        fixed_step_rate_sum = pulp.lpSum([rates[i] * w_vars[i] for i in range(fixed_step_threshold)])
        linear_rate_sum = pulp.lpSum([rates[i] * w_vars[i] for i in range(fixed_step_threshold, num_steps)])
        return cost_result(fixed_rate=fixed_rate_sum,
                           variable_rate=fixed_step_rate_sum + linear_rate_sum,
                           total=total)

def package_cost_gripper(total_weight, prob=None, book_cd=False, total=True):
    weight_steps = [( 0.001,  0.901, 19.80, 'f'),
                    ( 0.900,  5.001, 21.90, 'l'),
                    ( 5.001, 20.001, 16.50, 'l'),
                    (20.001, 40.000, 13.20, 'l')]
    num_steps = len(weight_steps)
    if isinstance(total_weight, (int, float)):
        if total_weight == 0:
            return cost_result(fixed_rate=0,
                               variable_rate=0,
                               total=total)
        if book_cd:
            handling_rate = 0
            weight_rate = round(max(total_weight, 0.6)*12.0, COST_DECIMALS)
        else:
            handling_rate = 5
            weight_rate = return_rate(weight_steps=weight_steps,
                                      total_weight=total_weight)
        return cost_result(fixed_rate=handling_rate,
                           variable_rate=weight_rate,
                           total=total)
    elif isinstance(total_weight, pulp.LpVariable):
        handling_rate = 5
        fixed_step_threshold = return_fixed_step_threshold(weight_steps=weight_steps)
        prob, rates, w_active_vars, w_vars = configure_restrictions(weight_steps=weight_steps,
                                                                    total_weight=total_weight,
                                                                    prob=prob)
        fixed_rate_sum = handling_rate * pulp.lpSum(w_active_vars)
        fixed_step_rate_sum = pulp.lpSum([rates[i] * w_vars[i] for i in range(fixed_step_threshold)])
        linear_rate_sum = pulp.lpSum([rates[i] * w_vars[i] for i in range(fixed_step_threshold, num_steps)])
        return cost_result(fixed_rate=fixed_rate_sum,
                           variable_rate=fixed_step_rate_sum + linear_rate_sum,
                           total=total)

def package_cost_punto_mio(total_weight, prob=None, book_cd=False, total=True):
    weight_steps = [( 0.001,  0.501,  8.99, 'f'),
                    ( 0.500, 40.000, 16.00, 'l')]
    num_steps = len(weight_steps)
    if isinstance(total_weight, (int, float)):
        if total_weight == 0:
            return cost_result(fixed_rate=0,
                               variable_rate=0,
                               total=total)
        if book_cd:
            handling_rate = 5
            weight_rate = round(max(ceil_in_increments(total_weight, 1), 1)*8.99, COST_DECIMALS)
        else:
            handling_rate = 5
            weight_rate = return_rate(weight_steps=weight_steps,
                                      total_weight=total_weight,
                                      increments=0.1)
            if total_weight > 0.5:
                weight_rate += 5
        return cost_result(fixed_rate=handling_rate,
                           variable_rate=weight_rate,
                           total=total)
    elif isinstance(total_weight, pulp.LpVariable):
        handling_rate = 5
        fixed_step_threshold = return_fixed_step_threshold(weight_steps=weight_steps)
        prob, rates, w_active_vars, w_vars = configure_restrictions(weight_steps=weight_steps,
                                                                    total_weight=total_weight,
                                                                    prob=prob,
                                                                    ceil=0.1)
        fixed_rate_sum = handling_rate * pulp.lpSum(w_active_vars)
        fixed_step_rate_sum = pulp.lpSum([5 * w_active_vars[i] + rates[i] * w_vars[i] for i in range(fixed_step_threshold)])
        linear_rate_sum = pulp.lpSum([5 * w_active_vars[i] + rates[i] * w_vars[i] for i in range(fixed_step_threshold, num_steps)])
        return cost_result(fixed_rate=fixed_rate_sum,
                           variable_rate=fixed_step_rate_sum + linear_rate_sum,
                           total=total)

def package_cost_uruguay_cargo(total_weight, prob=None, book_cd=False, total=True):
    # Confirmar si el handling es por cada paquete sin consolidar
    weight_steps = [( 0.001,  0.501, 14.99, 'f'),
                    ( 0.501,  5.001, 19.50, 'l'),
                    ( 5.001, 10.001, 18.99, 'l'),
                    (10.001, 20.001, 18.20, 'l')]
    num_steps = len(weight_steps)
    if isinstance(total_weight, (int, float)):
        if total_weight == 0:
            return cost_result(fixed_rate=0,
                               variable_rate=0,
                               total=total)
        if book_cd:
            handling_rate = 2.5
        else:
            handling_rate = 4
        weight_rate = return_rate(weight_steps=weight_steps,
                                  total_weight=total_weight)
        return cost_result(fixed_rate=handling_rate,
                           variable_rate=weight_rate,
                           total=total)
    elif isinstance(total_weight, pulp.LpVariable):
        handling_rate = 4
        fixed_step_threshold = return_fixed_step_threshold(weight_steps=weight_steps)
        prob, rates, w_active_vars, w_vars = configure_restrictions(weight_steps=weight_steps,
                                                                    total_weight=total_weight,
                                                                    prob=prob,
                                                                    ceil=None)
        fixed_rate_sum = handling_rate * pulp.lpSum(w_active_vars)
        fixed_step_rate_sum = pulp.lpSum([rates[i] * w_active_vars[i] for i in range(fixed_step_threshold)])
        linear_rate_sum = pulp.lpSum([rates[i] * w_vars[i] for i in range(fixed_step_threshold, num_steps)])
        return cost_result(fixed_rate=fixed_rate_sum,
                           variable_rate=fixed_step_rate_sum + linear_rate_sum,
                           total=total)

def package_cost_usx(total_weight, prob=None, book_cd=False, total=True):
    if isinstance(total_weight, (int, float)):
        if total_weight == 0:
            return cost_result(fixed_rate=0,
                               variable_rate=0,
                               total=total)
        if book_cd:
            rate = 10.5
        else:
            rate = 17.5
        weight_rate = rate * ceil_in_increments(number=total_weight,
                                                increments=0.1)
        return cost_result(fixed_rate=0,
                           variable_rate=weight_rate,
                           total=total)
    elif isinstance(total_weight, pulp.LpVariable):
        weight_steps = [( 0.001,  40, 17.5, 'l')]
        num_steps = len(weight_steps)
        prob, rates, w_active_vars, w_vars = configure_restrictions(weight_steps=weight_steps,
                                                                    total_weight=total_weight,
                                                                    prob=prob,
                                                                    ceil=None)
        linear_rate_sum = pulp.lpSum([rates[i] * w_vars[i] for i in range(num_steps)])
        return cost_result(fixed_rate=0,
                           variable_rate=linear_rate_sum,
                           total=total)

def package_cost_exur(total_weight, prob=None, book_cd=False, total=True):
    if isinstance(total_weight, (int, float)):
        if total_weight == 0:
            return cost_result(fixed_rate=0,
                               variable_rate=0,
                               total=total)
        weight_lbs = round(total_weight*LBS_PER_KG, 2)
        if book_cd:
            cost_first_lb = 6.0
            cost_rest_lbs = 6.0
        else:
            cost_first_lb = 18.0
            cost_rest_lbs = 7.5
        return cost_result(fixed_rate=0,
                           variable_rate=round(cost_first_lb + max(ceil(weight_lbs-1)* cost_rest_lbs, 0), 2),
                           total=total)
    elif isinstance(total_weight, pulp.LpVariable):
        weight_steps = [(0.001,  1.001, 18.0, 'f'),
                        (1.001, 40.000,  7.5, 'l')]
        prob, rates, w_active_vars, w_vars = configure_restrictions(weight_steps=weight_steps,
                                                                    total_weight=total_weight*LBS_PER_KG,
                                                                    prob=prob,
                                                                    ceil=1)
        w_above_1 = pulp.LpVariable(f'w2_above_1_{total_weight}', lowBound=0)
        w_above_1_aux = pulp.LpVariable(f'w2_above_1_{total_weight}_aux', cat='Binary')
        prob = add_linear_constraints_max(result=w_above_1,
                                          value1=w_vars[1]-1,
                                          value2=0,
                                          auxiliary_var=w_above_1_aux,
                                          prob=prob)
        fixed_step_rate_sum = rates[0] * (w_active_vars[0] + w_active_vars[1])
        linear_rate_sum = rates[1] * w_above_1
        return cost_result(fixed_rate=0,
                           variable_rate=fixed_step_rate_sum + linear_rate_sum,
                           total=total)

def package_cost_grinbox(total_weight, prob=None, book_cd=False, total=True):
    weight_steps = [( 0.0, 10.001, 22.0, 'l'),
                    (10.0, 20.001, 19.8, 'l'),
                    (20.0, 40.000, 17.6, 'l')]
    num_steps = len(weight_steps)
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
        handling_rate = 4
        prob, rates, w_active_vars, w_vars = configure_restrictions(weight_steps=weight_steps,
                                                                    total_weight=total_weight,
                                                                    prob=prob,
                                                                    ceil=None)
        fixed_rate_sum = handling_rate * pulp.lpSum(w_active_vars)
        linear_rate_sum = pulp.lpSum([rates[i] * w_vars[i] for i in range(num_steps)])
        return cost_result(fixed_rate=fixed_rate_sum,
                           variable_rate=linear_rate_sum,
                           total=total)

def package_cost_melotraigo(total_weight, prob=None, book_cd=False, total=True):
    weight_steps = [( 0.001,  5.001, 20.9, 'l'),
                    ( 5.001, 10.001, 18.0, 'l'),
                    (10.001, 15.001, 17.0, 'l'),
                    (15.001, 40.001, 16.0, 'l')]
    num_steps = len(weight_steps)
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
        handling_rate = 5
        prob, rates, w_active_vars, w_vars = configure_restrictions(weight_steps=weight_steps,
                                                                    total_weight=total_weight,
                                                                    prob=prob,
                                                                    ceil=None)
        fixed_rate_sum = handling_rate * pulp.lpSum(w_active_vars)
        linear_rate_sum = pulp.lpSum([rates[i] * w_vars[i] for i in range(num_steps)])
        return cost_result(fixed_rate=fixed_rate_sum,
                           variable_rate=linear_rate_sum,
                           total=total)

def package_cost_buybox(total_weight, prob=None, book_cd=False, total=True):
    weight_steps = [( 0.000,  0.501,  5.9, 'f'),
                    ( 0.501,  1.001, 21.0, 'l'),
                    ( 1.001,  3.001, 18.9, 'l'),
                    ( 3.001,  5.001, 16.9, 'l'),
                    ( 5.001, 10.001, 15.9, 'l'),
                    (10.001, 20.001, 13.9, 'l')]
    num_steps = len(weight_steps)
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
        handling_rate = 5
        fixed_step_threshold = return_fixed_step_threshold(
            weight_steps=weight_steps)
        prob, rates, w_active_vars, w_vars = configure_restrictions(weight_steps=weight_steps,
                                                                    total_weight=total_weight,
                                                                    prob=prob,
                                                                    ceil=None)
        fixed_rate_sum = handling_rate * pulp.lpSum(w_active_vars)
        fixed_step_rate_sum = pulp.lpSum([rates[i] * w_active_vars[i]
                                          for i in range(fixed_step_threshold)])
        linear_rate_sum = pulp.lpSum([rates[i] * w_vars[i]
                                      for i in range(fixed_step_threshold, num_steps)])
        return cost_result(fixed_rate=fixed_rate_sum,
                           variable_rate=fixed_step_rate_sum + linear_rate_sum,
                           total=total)
