from app.core.config import *
#from app.utils.helpers import format_table
import app.utils.helpers
import json

class Package:
    def __init__(self, items, total_price, total_weight, transport_cost,
                 import_fee, import_fee_exemption):
        self.items = items  # List of tuples (name, price, weight)
        self.total_price = total_price
        self.total_weight = total_weight
        self.transport_cost = transport_cost
        self.import_fee = import_fee
        self.import_fee_exempted = import_fee_exemption  # Boolean: whether the package is exempted or not
        self.total_package_cost = transport_cost.total + import_fee

class PackageSolution:
    def __init__(self, courier_id, courier, status="", solutions=0, time_spent=0):
        self.packages = []              # List of Package objects
        self.total_weight = 0           # Total weight of all packages
        self.total_price = 0            # Total price of all packages
        self.total_transport_cost = TransportCost.zero()
                                        # Total transport cost of all packages
        self.total_import_fee = 0       # Total import fees of all packages
        self.total_cost = 0             # Total cost including transport and import fees
        self.courier_id = courier_id
        self.courier = courier
        self.solutions = solutions
        self.status = status
        self.time_spent = time_spent
    
    def add_package(self, package):
        self.packages.append(package)
        self.total_weight += package.total_weight
        self.total_price += package.total_price
        self.total_transport_cost += package.transport_cost
        self.total_import_fee += package.import_fee
        self.total_cost += package.transport_cost.total + package.import_fee
    
    def __str__(self):
        result  = f"{self.status} solution found for courier '{self.courier}' ({self.courier_id})\n\n"
        result += f"- Time spent: {self.time_spent:.2f} seconds\n"
        num_packages = len(self.packages)
        result += f"- Packages: {num_packages}\n\n"
        result += 'PACKAGE DETAILS\n\n'
        for i, package in enumerate(self.packages):
            result += f"* Package {i+1}" + (f" of {num_packages}" if num_packages>1 else "") + ":\n"
            result +=  "  ==========" + ("="*(4+len(str(num_packages))) if num_packages>1 else "") + "\n"
            result += '\n'
            result +=  "  - Items included:\n\n"
            result = app.utils.helpers.add_result_table(data=package.items,
                                                        result=result,
                                                        type="items")
            result += '\n'
            result +=  "  - Costs information:\n\n"
            result = app.utils.helpers.add_result_table(data=package,
                                                        result=result,
                                                        type="cost")
            result += '\n'
        result += "---\n"
        result += "Totals:\n"
        result += "=======\n\n"
        result += f"Total price:         USD {self.total_price:.2f}\n"
        result += f"Total weight:            {self.total_weight:.2f} kg\n"
        result += '\n'
        result +=  "Total transport costs:\n\n"
        result = app.utils.helpers.add_result_table(data=self,
                                                    result=result,
                                                    type="total_cost")
        if self.solutions > 0:
            result += '\n'
            result += f"Solutions analyzed:  {self.solutions}"
        return result
    
    def show(self):
        print(self)
    
    def save_to_file(self, filename='solution_details.log'):
        try:
            with open("output\\"+filename, 'w') as file:
                print(self, file=file)
            print(f"File '{filename}' saved successfully.")
        except IOError as e:
            print(f"Error saving file '{filename}': {e}")
    
    def to_json(self, pretty=False):
        result = {
            "status": self.status,
            "time_spent": self.time_spent,
            "packages": [
                {
                    "package_id": i+1,
                    "items": [
                        {
                            "name": item[0], "price": item[1], "weight": item[2]
                        }
                        for item in pkg.items],
                    "price": round(pkg.total_price, COST_DECIMALS),
                    "weight": pkg.total_weight,
                    "handling": pkg.transport_cost.handling,
                    "freight": pkg.transport_cost.freight,
                    "subtotal": pkg.transport_cost.subtotal,
                    "tax": pkg.transport_cost.tax,
                    "tfspu": pkg.transport_cost.TFSPU,
                    "transport": pkg.transport_cost.total,
                    "import_fee": pkg.import_fee,
                    "cost": pkg.total_package_cost
                }
                for i, pkg in enumerate(self.packages)
            ],
            "total_price": round(self.total_price, COST_DECIMALS),
            "total_weight": self.total_weight,
            "total_handling": self.total_transport_cost.handling,
            "total_freight": self.total_transport_cost.freight,
            "total_subtotal": self.total_transport_cost.subtotal,
            "total_tax": self.total_transport_cost.tax,
            "total_tfspu": self.total_transport_cost.TFSPU,
            "total_transport": self.total_transport_cost.total,
            "total_import_fee": self.total_import_fee,
            "total_cost": self.total_cost
        }
        if pretty:
            result = json.dumps(result, indent=4)
        return result

class TransportCost:
    def __init__(self, handling, freight):
        if isinstance(handling, (int, float)) and isinstance(freight, (int, float)):
            self.handling = round(handling, COST_DECIMALS)
            self.freight = round(freight, COST_DECIMALS)
            self.subtotal = self.handling + self.freight
            self.tax = round(TAX_ON_FREIGHT * freight, COST_DECIMALS)
            self.TFSPU = round(self.freight * TFSPU_RATE, COST_DECIMALS)
            self.total = round(self.subtotal + self.tax + self.TFSPU, COST_DECIMALS)
        else:
            self.handling = handling
            self.freight = freight
            self.subtotal = self.handling + self.freight
            self.tax = TAX_ON_FREIGHT * freight
            self.TFSPU = self.freight * TFSPU_RATE
            self.total = self.subtotal + self.tax + self.TFSPU
    
    @classmethod
    def zero(cls):
        return cls(handling=0, freight=0)
    
    def __add__(self, other):
        if not isinstance(other, TransportCost):
            raise TypeError(f"Unsupported operand type(s) for +: '{type(self).__name__}' and '{type(other).__name__}'")
        addition = object.__new__(TransportCost)
        addition.handling = round(self.handling + other.handling, COST_DECIMALS)
        addition.freight = round(self.freight + other.freight, COST_DECIMALS)
        addition.subtotal = round(self.subtotal + other.subtotal, COST_DECIMALS)
        addition.tax = round(self.tax + other.tax, COST_DECIMALS)
        addition.TFSPU = round(self.TFSPU + other.TFSPU, COST_DECIMALS)
        addition.total = round(self.total + other.total, COST_DECIMALS)
        return addition

    def __str__(self):
        output  = f'- Handling: USD {self.handling}\n'
        output += f'- Freight:  USD {self.freight}\n'
        output += f'- Subtotal: USD {self.subtotal}\n'
        output +=  '  =========\n'
        output += f'- Tax:      USD {self.tax}\n'
        output += f'- TFSPU:    USD {self.TFSPU}\n'
        output += f'- Total:    USD {self.total}'
        return output 

    def show(self):
        print(self)
