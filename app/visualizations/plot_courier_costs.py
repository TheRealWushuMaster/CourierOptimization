import courier_costs
from numpy import linspace
from matplotlib import pyplot as plt

weights_list = []
for weight in range(100, 20000, 1):
    weights_list.append(weight/1000)

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
costs_exur = compute_total_cost(courier_costs.package_cost_exur, weights_list)
costs_punto_mio = compute_total_cost(courier_costs.package_cost_punto_mio, weights_list)

plt.figure(figsize=(10, 6))
plt.plot(weights_list, costs_urubox, label='Urubox')
plt.plot(weights_list, costs_miami_box, label='Miami-Box')
plt.plot(weights_list, costs_aerobox, label='Aerobox')
plt.plot(weights_list, costs_gripper, label='Gripper')
plt.plot(weights_list, costs_uruguay_cargo, label='Uruguay Cargo')
plt.plot(weights_list, costs_usx, label='USX')
plt.plot(weights_list, costs_exur, label='Exur')
plt.plot(weights_list, costs_punto_mio, label='Punto Mío')

plt.title('Costo de envío por peso para compras gravadas')
plt.xlabel('Peso (kg)')
plt.ylabel('Costo (USD)')
plt.xlim((0, 20))
plt.ylim((0, None))
plt.legend()
plt.grid(True)

plt.show()