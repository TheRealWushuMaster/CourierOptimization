import courier_costs
from numpy import linspace
from matplotlib import pyplot as plt

weights = linspace(100, 20000, 200)
weights_list = []
for value in weights:
    weights_list.append((value-2)/1000)
    weights_list.append((value+2)/1000)

def compute_total_cost(cost_func, weights):
    costs = []
    for w in weights:
        cost = cost_func(w)
        if cost is not None:
            costs.append(sum(cost))  # sum fixed and variable parts
        else:
            costs.append(0)  # Handle case where cost is None
    return costs

costs_urubox = compute_total_cost(courier_costs.package_cost_urubox, weights_list)
costs_miami_box = compute_total_cost(courier_costs.package_cost_miami_box, weights_list)
costs_aerobox = compute_total_cost(courier_costs.package_cost_aerobox, weights_list)
costs_gripper = compute_total_cost(courier_costs.package_cost_gripper, weights_list)
costs_uruguay_cargo = compute_total_cost(courier_costs.package_cost_uruguay_cargo, weights_list)
costs_usx = compute_total_cost(courier_costs.package_cost_usx, weights_list)

plt.figure(figsize=(10, 6))
plt.plot(weights_list, costs_urubox, label='Urubox')
plt.plot(weights_list, costs_miami_box, label='Miami-Box')
plt.plot(weights_list, costs_aerobox, label='Aerobox')
plt.plot(weights_list, costs_gripper, label='Gripper')
plt.plot(weights_list, costs_uruguay_cargo, label='Uruguay Cargo')
plt.plot(weights_list, costs_usx, label='USX')

plt.title('Precio de envío por peso')
plt.xlabel('Peso total (kg)')
plt.ylabel('Costo total (USD)')
plt.xlim((0, 20))
plt.ylim((0, None))
plt.legend()
plt.grid(True)

plt.show()