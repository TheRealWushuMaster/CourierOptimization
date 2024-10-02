from math import ceil

# Confirmar cómo aplicar el IVA en cada uno

tasa_postal_internacional = 0.1

def package_cost_urubox(total_weight, promo=False):
    fixed_rate = 5
    if promo:
        return fixed_rate, round(max(total_weight, 1)*9.9, 2)
    weight_threshold = 1
    weight_steps = [
        (0.0, 0.199, 10.9),
        (0.2, 0.499, 15.9),
        (0.5, 0.699, 18.9),
        (0.7, 0.999, 20.9),
        (1.0, 4.999, 19.9),
        (5.0, 9.999, 17.9),
        (10.0, 19.999, 16.5),
        (20.0, float('inf'), 15.9)
    ]
    for min_weight, max_weight, rate in weight_steps:
        if min_weight <= total_weight <= max_weight:
            variable_rate = rate if total_weight < weight_threshold else total_weight * rate
            return fixed_rate, round(variable_rate*(1+tasa_postal_internacional), 2)

def package_cost_miami_box(total_weight, promo=False):
    fixed_rate = 6
    if promo:
        return 2.5, round(total_weight*9.9*(1+tasa_postal_internacional), 2)
    if total_weight >= 30:
        return 0, 0
    elif total_weight < 0.4:
        return fixed_rate, 10
    cost_per_100_gr = 2.59
    variable_rate = ceil(total_weight / 0.1) * cost_per_100_gr
    if total_weight >= 20:
        variable_rate *= 0.8
    elif total_weight >= 10:
        variable_rate *= 0.9
    return fixed_rate, round(variable_rate*(1+tasa_postal_internacional), 2)

def package_cost_aerobox(total_weight, promo=False):
    if promo:
        return 0, round(total_weight*11.99*(1+tasa_postal_internacional), 2)
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
            return fixed_rate, round(variable_rate*(1+tasa_postal_internacional), 2)

def package_cost_gripper(total_weight, promo=False):
    if promo:
        return 0, round(max(total_weight, 0.6)*12*(1+tasa_postal_internacional), 2)
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
            return fixed_rate, round(variable_rate*(1+tasa_postal_internacional), 2)

def package_cost_punto_mio(total_weight, promo=False):
    return 0

def package_cost_uruguay_cargo(total_weight, promo=False):
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

def package_cost_usx(total_weight, promo=False):
    variable_rate = round(ceil(total_weight / 0.1) / 10 * 17.5, 2)
    return 0, variable_rate