from app.utils.courier_costs import *

couriers = {
    "UBX": {"name": "Urubox",
            "cost_function": package_cost_urubox,
            "applies_taxes": False},
    "MBX": {"name": "Miami-Box",
            "cost_function": package_cost_miami_box,
            "applies_taxes": False},
    "ABX": {"name": "Aerobox",
            "cost_function": package_cost_aerobox,
            "applies_taxes": False},
    "GPR": {"name": "Gripper",
            "cost_function": package_cost_gripper,
            "applies_taxes": False},
    "PMO": {"name": "Punto Mío",
            "cost_function": package_cost_punto_mio,
            "applies_taxes": False},
    "UYC": {"name": "Uruguay Cargo",
            "cost_function": package_cost_uruguay_cargo,
            "applies_taxes": False},
    "USX": {"name": "USX",
            "cost_function": package_cost_usx,
            "applies_taxes": True},
    "XUR": {"name": "Exur",
            "cost_function": package_cost_exur,
            "applies_taxes": False},
    "GBX": {"name": "Grinbox",
            "cost_function": package_cost_grinbox,
            "applies_taxes": False},
    "MLT": {"name": "MeLoTRAIGO",
            "cost_function": package_cost_melotraigo,
            "applies_taxes": False},
    "BBX": {"name": "Buybox",
            "cost_function": package_cost_buybox,
            "applies_taxes": False}
    }
courier_list = [{"id": courier_id,
                 "name": data["name"]} for courier_id, data in couriers.items()]

def courier_exists(courier):
    if courier in couriers:
        return True
    else:
        return False

def compare_costs(weight):
    list = []
    for courier in couriers:
        cost = couriers[courier]["cost_function"](weight)
        list.append((couriers[courier]["name"], cost))
    max_name_length = max(len(name) for (name, cost) in list)
    list.sort(key=lambda x: x[1])
    print(f"** Weight = {weight:.3f} kg\n")
    print("** Total transport cost per courier:\n")
    print(f"Nº  {'Courier'.ljust(max_name_length)}  Cost")
    print("-" * 24)
    for i, (name, cost) in enumerate(list):
        print(f"{(str(i+1)+".").ljust(3)} {name.ljust(max_name_length)}  {cost:.2f}")
