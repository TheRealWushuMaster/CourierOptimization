from app.utils.courier_services import couriers
from matplotlib import pyplot as plt

weights_list = []
for weight in range(100, 20000, 1):
    weights_list.append(weight/1000)

def compute_total_cost(cost_func, weights):
    costs = []
    for w in weights:
        cost = cost_func(w)
        if cost is not None:
            costs.append(cost)  # Sums fixed and variable parts
        else:
            costs.append(0)  # Handle case where cost is None
    return costs

plots = []
for courier in couriers:
    courier_costs = compute_total_cost(couriers[courier]["cost_function"], weights_list)
    plots.append((courier, courier_costs))

plt.figure(figsize=(10, 6))
for item in plots:
    plt.plot(weights_list, item[1], label=item[0])

plt.title('Costo de envío por peso para compras gravadas')
plt.xlabel('Peso (kg)')
plt.ylabel('Costo (USD)')
plt.xlim((0, 20))
plt.ylim((0, None))
plt.legend()
plt.grid(True)

plt.show()