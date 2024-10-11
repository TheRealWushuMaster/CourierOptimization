# CLASSES
# =======
class Package:
    def __init__(self, items, total_price, total_weight, transport_cost,
                 import_fee, import_fee_exemption):
        self.items = items  # List of tuples (name, price, weight)
        self.total_price = total_price
        self.total_weight = total_weight
        self.transport_cost = transport_cost
        self.import_fee = import_fee
        self.import_fee_exempted = import_fee_exemption  # Boolean: whether the package is exempted or not
        self.total_package_cost = transport_cost + import_fee

class PackageSolution:
    def __init__(self, courier):
        self.packages = []  # List of Package objects
        self.total_weight = 0           # Total weight of all packages
        self.total_price = 0            # Total price of all packages
        self.total_transport_cost = 0   # Total transport cost of all packages
        self.total_import_fee = 0       # Total import fees of all packages
        self.total_cost = 0             # Total cost including transport and import fees
        self.courier = courier
    
    def add_package(self, package):
        self.packages.append(package)
        self.total_weight += package.total_weight
        self.total_price += package.total_price
        self.total_transport_cost += package.transport_cost
        self.total_import_fee += package.import_fee
        self.total_cost += package.transport_cost + package.import_fee

# METHODS
# =======
def display_solution(solution):
    print(f"Optimal solution found for courier {solution.courier}:")
    print()
    for i, package in enumerate(solution.packages):
        print(f"* Package {i+1}:")
        print("  ==========")
        print()
        print("  - Items included:")
        for n, item in enumerate(package.items):
            print(f"      {n+1}. {item[0]} (USD {item[1]}, {item[2]} kg)")
        print()
        print("  - Package information:")
        print(f"    Total price:     USD {package.total_price:.2f}")
        print(f"    Total weight:        {package.total_weight:.2f} kg")
        print()
        print("  - Costs information:")
        print(f"    Transport cost:  USD {package.transport_cost:.2f}")
        print(f"    Import fee:      USD {package.import_fee:.2f}"+(" (fee exempted)" if package.import_fee_exempted else ""))
        print()
        print(f"    Total cost:      USD {package.total_package_cost:.2f}")
        print()
    print("---")
    print("Totals:")
    print(f"Total price:           USD {solution.total_price:.2f}")
    print(f"Total weight:              {solution.total_weight:.2f} kg")
    print()
    print(f"Total transport cost:  USD {solution.total_transport_cost:.2f}")
    print(f"Total import fee:      USD {solution.total_import_fee:.2f}")
    print()
    print(f"Total cost:            USD {solution.total_cost:.2f}")
