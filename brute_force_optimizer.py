from typing import List, Tuple, Callable
from itertools import combinations
from settings import *
from routines import *
from courier_services import *

Item = Tuple[str, float, float]
Pack = List[Item]
Solution = List[Pack]

def calculate_package_cost(items: List[Tuple[float, float]], 
                           transport_cost_func: Callable[[float], float],
                           is_exempt: bool) -> float:
    total_price = sum(item[1] for item in items)
    total_weight = sum(item[2] for item in items)
    transport_cost = transport_cost_func(total_weight)#[0]+transport_cost_func(total_weight)[1]
    import_fee = (max(IMPORT_FEE_PERCENT * total_price, MINIMUM_FEE_PAYMENT)) if not is_exempt else 0
    return {"transport_cost": transport_cost,
            "import_fee": import_fee,
            "total_cost": transport_cost + import_fee}

def package_valid(items: List[Tuple[float, float]]) -> bool:
    total_price = sum(item[1] for item in items)
    total_weight = sum(item[2] for item in items)
    return total_price <= MAX_PRICE_EXEMPTION and total_weight <= MAX_WEIGHT_EXEMPTION

def brute_force_optimization(items,#: List[Item],
                             courier,#: Callable[[float], float],
                             max_exemptions=MAX_EXEMPTIONS_PER_YEAR):#: int = 3) -> Tuple[dict, List[dict]]:
    n = len(items)
    best_solution = None
    best_cost = float('inf')
    transport_cost_func = couriers[courier]["cost_function"]
    valid_solutions = []

    def backtrack(index: int, current_partition: Solution):
        nonlocal best_solution, best_cost

        if index == n:
            for exempt_combination in combinations(range(len(current_partition)), min(max_exemptions, len(current_partition))):
                packages_info = []
                total_transport_cost = 0
                total_import_fee = 0
                total_price = 0
                total_weight = 0
                for i, package in enumerate(current_partition):
                    is_exempt = i in exempt_combination
                    package_price = sum(item[1] for item in package)
                    package_weight = sum(item[2] for item in package)
                    cost_breakdown = calculate_package_cost(package, transport_cost_func, is_exempt)
                    packages_info.append({"items": [{"name": item[0], "price": item[1], "weight": item[2]} for item in package],
                                          "is_exempt": is_exempt,
                                          "total_price": package_price,
                                          "total_weight": package_weight,
                                          "transport_cost": cost_breakdown["transport_cost"],
                                          "import_fee": cost_breakdown["import_fee"],
                                          "total_cost": cost_breakdown["total_cost"]})
                    total_transport_cost += cost_breakdown["transport_cost"]
                    total_import_fee += cost_breakdown["import_fee"]
                    total_price += package_price
                    total_weight += package_weight
                total_cost = total_transport_cost + total_import_fee
                solution_info = {"packages": packages_info,
                                 "total_price": total_price,
                                 "total_weight": total_weight,
                                 "total_transport_cost": total_transport_cost,
                                 "total_import_fee": total_import_fee,
                                 "total_cost": total_cost}
                valid_solutions.append(solution_info)
                if total_cost < best_cost:
                    best_cost = total_cost
                    best_solution = solution_info
            return
        for package in current_partition:
            package.append(items[index])
            if package_valid(package):
                backtrack(index + 1, current_partition)
            package.pop()
        current_partition.append([items[index]])
        backtrack(index + 1, current_partition)
        current_partition.pop()
    backtrack(0, [])
    optimal_solution = PackageSolution(courier=courier, solutions=len(valid_solutions))
    for package in best_solution["packages"]:
        assigned_items = [(items["name"], items["price"], items["weight"]) for items in package["items"]]
        total_price = package["total_price"]
        total_weight = package["total_weight"]
        transport_cost = package["transport_cost"]
        import_fee = package["import_fee"]
        import_fee_exemption = package["is_exempt"]
        package = Package(items=assigned_items,
                          total_price=total_price,
                          total_weight=total_weight,
                          transport_cost=transport_cost,
                          import_fee=import_fee,
                          import_fee_exemption=import_fee_exemption)
        optimal_solution.add_package(package)
    
    return optimal_solution, valid_solutions

def print_results(optimal_solution, all_solutions, courier_service):
    print(f"Optimization using courier {courier_service}")
    print()
    print("Optimal packaging solution:")
    print()
    for i, package in enumerate(optimal_solution["packages"]):
        print(f"* Package {i+1}:")
        print("  ==========\n")
        print("  Items included:")
        for n, item in enumerate(package["items"]):
            print(f"    {n+1}. {item['name']} (USD {item['price']}, {item['weight']} kg)")
        print()
        print(f"  Package price:       USD {package['total_price']:.2f}")
        print(f"  Package weight:          {package['total_weight']:.2f} kg")
        print(f"  Transport cost:      USD {package['transport_cost']:.2f}")
        print(f"  Import fee:          USD {package['import_fee']:.2f}"+(" (fee exempted)" if package['is_exempt'] else ""))
        print()
        print(f"  Total package cost:  USD {package['total_cost']:.2f}")
        print()
    print("---")
    print("Totals:")
    print()
    print(f"Total price:           USD {optimal_solution['total_price']:.2f}")
    print(f"Total weight:              {optimal_solution['total_weight']:.2f} kg")
    print()
    print(f"Total transport cost:  USD {optimal_solution['total_transport_cost']:.2f}")
    print(f"Total import fee:      USD {optimal_solution['total_import_fee']:.2f}")
    print()
    print(f"Total cost:            USD {optimal_solution['total_cost']:.2f}")
    print()
    print(f"Valid solutions analyzed: {len(all_solutions)}")
