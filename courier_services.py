from courier_costs import *

couriers = {"Urubox": {"cost_function": package_cost_urubox},
            "Miami-Box": {"cost_function": package_cost_miami_box},
            "Aerobox": {"cost_function": package_cost_aerobox},
            "Gripper": {"cost_function": package_cost_gripper},
            "Punto Mío": {"cost_function": package_cost_punto_mio},
            "Uruguay Cargo": {"cost_function": package_cost_uruguay_cargo},
            "USX": {"cost_function": package_cost_usx},
            "Exur": {"cost_function": package_cost_exur},
            "Test": {"cost_function": package_cost_test}
            }