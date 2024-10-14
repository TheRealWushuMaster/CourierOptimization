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
    weight_steps = [(0.0, 0.2, 10.9),
                    (0.2, 0.5, 15.9),
                    (0.5, 0.7, 18.9),
                    (0.7,   1, 20.9),   # Up to this step, the rate is fixed by step
                    (1.0,   5, 19.9),   # From this step onwards, the rate
                    (5.0,  10, 17.9),   #   is linear with weight
                    (10.0, 20, 16.5),
                    (20.0, float('inf'), 15.9)]
    weight_threshold = 1
    if isinstance(total_weight, (int, float)):  # Float input (immediate calculation)
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
        rate_step1 = weight_steps[0][2]
        rate_step2 = weight_steps[1][2]
        rate_step3 = weight_steps[2][2]
        rate_step4 = weight_steps[3][2]
        rate_step5 = weight_steps[4][2]
        rate_step6 = weight_steps[5][2]
        rate_step7 = weight_steps[6][2]
        rate_step8 = weight_steps[7][2]
        lowbound_step1 = weight_steps[0][0]
        lowbound_step2 = weight_steps[1][0]
        lowbound_step3 = weight_steps[2][0]
        lowbound_step4 = weight_steps[3][0]
        lowbound_step5 = weight_steps[4][0]
        lowbound_step6 = weight_steps[5][0]
        lowbound_step7 = weight_steps[6][0]
        lowbound_step8 = weight_steps[7][0]
        upbound_step1 = weight_steps[0][1]
        upbound_step2 = weight_steps[1][1]
        upbound_step3 = weight_steps[2][1]
        upbound_step4 = weight_steps[3][1]
        upbound_step5 = weight_steps[4][1]
        upbound_step6 = weight_steps[5][1]
        upbound_step7 = weight_steps[6][1]
        upbound_step8 = weight_steps[7][1]
        w1 = pulp.LpVariable(f'w1_{total_weight}', lowBound=lowbound_step1, upBound=upbound_step1)
        aux1 = pulp.LpVariable(f'w1_{total_weight}_aux', cat='Binary')
        w1_active = pulp.LpVariable(f'w1_{total_weight}_active', cat='Binary')
        w2 = pulp.LpVariable(f'w2_{total_weight}', lowBound=lowbound_step2, upBound=upbound_step2)
        aux2 = pulp.LpVariable(f'w2_{total_weight}_aux', cat='Binary')
        w2_active = pulp.LpVariable(f'w2_{total_weight}_active', cat='Binary')
        w3 = pulp.LpVariable(f'w3_{total_weight}', lowBound=lowbound_step3, upBound=upbound_step3)
        aux3 = pulp.LpVariable(f'w3_{total_weight}_aux', cat='Binary')
        w3_active = pulp.LpVariable(f'w3_{total_weight}_active', cat='Binary')
        w4 = pulp.LpVariable(f'w4_{total_weight}', lowBound=lowbound_step4, upBound=upbound_step4)
        aux4 = pulp.LpVariable(f'w4_{total_weight}_aux', cat='Binary')
        w4_active = pulp.LpVariable(f'w4_{total_weight}_active', cat='Binary')
        w5 = pulp.LpVariable(f'w5_{total_weight}', lowBound=lowbound_step5, upBound=upbound_step5)
        aux5 = pulp.LpVariable(f'w5_{total_weight}_aux', cat='Binary')
        w5_active = pulp.LpVariable(f'w5_{total_weight}_active', cat='Binary')
        w6 = pulp.LpVariable(f'w6_{total_weight}', lowBound=lowbound_step6, upBound=upbound_step6)
        aux6 = pulp.LpVariable(f'w6_{total_weight}_aux', cat='Binary')
        w6_active = pulp.LpVariable(f'w6_{total_weight}_active', cat='Binary')
        w7 = pulp.LpVariable(f'w7_{total_weight}', lowBound=lowbound_step7, upBound=upbound_step7)
        aux7 = pulp.LpVariable(f'w7_{total_weight}_aux', cat='Binary')
        w7_active = pulp.LpVariable(f'w7_{total_weight}_active', cat='Binary')
        w8 = pulp.LpVariable(f'w8_{total_weight}', lowBound=lowbound_step8, upBound=upbound_step8)
        aux8 = pulp.LpVariable(f'w8_{total_weight}_aux', cat='Binary')
        w8_active = pulp.LpVariable(f'w8_{total_weight}_active', cat='Binary')
        prob += total_weight == w1 + w2 + w3 + w4 + w5 + w6 + w7 + w8
        # First step
        prob = add_linear_constraints_var_greater_than_value(result=w1_active,
                                                             var=total_weight,
                                                             value=lowbound_step1,
                                                             prob=prob)
        prob = add_linear_constraints_min(result=w1,
                                          value1=(upbound_step1-lowbound_step1)*w1_active,
                                          value2=total_weight-lowbound_step1 + M *
                                            (1 - w1_active),
                                          auxiliary_var=aux1,
                                          prob=prob)
        # Second step
        prob = add_linear_constraints_var_greater_than_value(result=w2_active,
                                                             var=total_weight,
                                                             value=lowbound_step2,
                                                             prob=prob)
        prob = add_linear_constraints_min(result=w2,
                                          value1=(upbound_step2-lowbound_step2)*w2_active,
                                          value2=total_weight-lowbound_step2 + M *
                                            (1 - w2_active),
                                          auxiliary_var=aux2,
                                          prob=prob)
        # Third step
        prob = add_linear_constraints_var_greater_than_value(result=w3_active,
                                                             var=total_weight,
                                                             value=lowbound_step3,
                                                             prob=prob)
        prob = add_linear_constraints_min(result=w3,
                                          value1=(upbound_step3-lowbound_step3)*w3_active,
                                          value2=total_weight-lowbound_step3 + M *
                                            (1 - w3_active),
                                          auxiliary_var=aux3,
                                          prob=prob)
        # Fourth step
        prob = add_linear_constraints_var_greater_than_value(result=w4_active,
                                                             var=total_weight,
                                                             value=lowbound_step4,
                                                             prob=prob)
        prob = add_linear_constraints_min(result=w4,
                                          value1=(upbound_step4-lowbound_step4)*w4_active,
                                          value2=total_weight-lowbound_step4 + M *
                                            (1 - w4_active),
                                          auxiliary_var=aux4,
                                          prob=prob)
        # Fifth step
        prob = add_linear_constraints_var_greater_than_value(result=w5_active,
                                                             var=total_weight,
                                                             value=lowbound_step5,
                                                             prob=prob)
        prob = add_linear_constraints_min(result=w5,
                                          value1=(upbound_step5-lowbound_step5)*w5_active,
                                          value2=total_weight-lowbound_step5 + M *
                                            (1 - w5_active),
                                          auxiliary_var=aux5,
                                          prob=prob)
        # Sixth step
        prob = add_linear_constraints_var_greater_than_value(result=w6_active,
                                                             var=total_weight,
                                                             value=lowbound_step6,
                                                             prob=prob)
        prob = add_linear_constraints_min(result=w6,
                                          value1=(upbound_step6-lowbound_step6)*w6_active,
                                          value2=total_weight-lowbound_step6 + M *
                                            (1 - w6_active),
                                          auxiliary_var=aux6,
                                          prob=prob)
        # Seventh step
        prob = add_linear_constraints_var_greater_than_value(result=w7_active,
                                                             var=total_weight,
                                                             value=lowbound_step7,
                                                             prob=prob)
        prob = add_linear_constraints_min(result=w7,
                                          value1=(upbound_step7-lowbound_step7)*w7_active,
                                          value2=total_weight-lowbound_step7 + M *
                                            (1 - w7_active),
                                          auxiliary_var=aux7,
                                          prob=prob)
        # Eighth step
        prob = add_linear_constraints_var_greater_than_value(result=w8_active,
                                                             var=total_weight,
                                                             value=lowbound_step8,
                                                             prob=prob)
        prob = add_linear_constraints_min(result=w8,
                                          value1=(upbound_step8-lowbound_step8)*w8_active,
                                          value2=total_weight-lowbound_step8 + M *
                                            (1 - w8_active),
                                          auxiliary_var=aux8,
                                          prob=prob)
        
        return rate_step1*w1_active + rate_step2*w2_active + rate_step3*w3_active + rate_step4*w4_active \
            + rate_step5*w5 + rate_step6*w6 + rate_step7*w7 + rate_step8*w8

def package_cost_miami_box(total_weight, promo=False, sum=True):
    fixed_rate = 6
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
                             variable_rate=10,
                             sum=sum)
    cost_per_100_gr = 2.59
    variable_rate = ceil(total_weight / 0.1) * cost_per_100_gr
    if total_weight >= 20:
        variable_rate *= 0.8
    elif total_weight >= 10:
        variable_rate *= 0.9
    return return_result(fixed_rate=fixed_rate,
                         variable_rate=round(variable_rate, 2),
                         sum=sum)

def package_cost_aerobox(total_weight, promo=False, sum=True):
    if promo:
        return 0, round(total_weight*11.99, 2)
    fixed_rate = 5*1.22
    weight_threshold = 0.601
    weight_steps = [
        ( 0.001, 0.5, 11.99),
        ( 0.501, 0.6, 15.50),
        ( 0.601,   5, 23.50),
        ( 5.001,  10, 20.50),
        (10.001,  20, 17.50),
    ]
    for min_weight, max_weight, rate in weight_steps:
        if min_weight <= total_weight <= max_weight:
            variable_rate = rate if total_weight < weight_threshold else total_weight * rate
            return fixed_rate, round(variable_rate, 2)

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
