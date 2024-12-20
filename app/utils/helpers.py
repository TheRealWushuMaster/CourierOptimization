from app.core.config import *
from app.models.schemas import OptimizationRequest
import json
from app.utils.courier_services import courier_exists

def read_json_input(json_input):
    if isinstance(json_input, OptimizationRequest):
        key = json_input.key
        purchased_items = [(item.name, item.price, item.weight) for item in json_input.purchases]
        selected_courier = json_input.courier_service
        fee_exemptions = json_input.import_fee_exemptions
        discount_rate = json_input.discount_rate
    elif isinstance(json_input, dict):
        key = json_input["key"]
        purchased_items = [(item['name'], item['price'], item['weight']) for item in json_input['purchases']]
        selected_courier = json_input['courier_service']
        fee_exemptions = json_input['import_fee_exemptions']
        discount_rate = json_input["discount_rate"]
    if fee_exemptions<0:
        fee_exemptions = 0
    elif fee_exemptions>MAX_EXEMPTIONS_PER_YEAR:
        fee_exemptions = MAX_EXEMPTIONS_PER_YEAR
    return key, purchased_items, selected_courier, fee_exemptions, discount_rate

def json_pretty(json_input):
    return json.dumps(json_input, indent=4)

def input_is_valid(key, items, courier, fee_exemptions, discount_rate):
    if not items_are_valid(items):
        return None
    if not key_valid(key):
        return None
    if not courier_exists(courier):
        return None
    return True

def key_valid(key):
    return True

def items_are_valid(items):
    if len(items) > MAX_ITEMS:
        return False
    for item in items:
        if not item_is_valid(item):
            return False
    return True

def item_is_valid(item):
    if not isinstance(item[0], str):
        return False
    if not isinstance(item[1], float):
        return False
    else:
        if item[1] < 0:
            return False
    if not isinstance(item[2], float):
        return False
    else:
        if item[2] < 0:
            return False
    return True

def format_table(data, column_formats, headers):
    column_widths = []
    for col_idx, fmt in enumerate(column_formats):
        max_width = len(headers[col_idx])  # Start with header length
        for row in data:
            value = row[col_idx]
            if 'f' in fmt and isinstance(value, (float, int)):
                formatted_value = f"{value:{fmt}}"
            else:
                formatted_value = str(value)
            max_width = max(max_width, len(formatted_value))
        column_widths.append(max_width)
    # Build format strings for headers and rows
    header_format = "  ".join([f"{{:<{width}}}" for width in column_widths])
    row_format = "  ".join([f"{{:>{width}.{fmt.split('.')[1]}}}" if 'f' in fmt
                            else f"{{:<{width}}}" for width, fmt in zip(column_widths, column_formats)])
    # Generate table
    table = []
    table.append(header_format.format(*headers))  # Add headers
    # Add separator
    table.append("=" * (sum(column_widths) + len(column_widths) * 2 - 2))
    # Add rows
    for row in data:
        formatted_row = []
        for col_idx, value in enumerate(row):
            fmt = column_formats[col_idx]
            if 'f' in fmt and isinstance(value, (float, int)):
                formatted_row.append(
                    f"{value:{column_widths[col_idx]}.{fmt.split('.')[1]}}")
            else:
                formatted_row.append(f"{value:<{column_widths[col_idx]}}")
        table.append("  ".join(formatted_row))
    return table

def print_table(table):
    """Prints formatted table line by line."""
    for line in table:
        print(line)

def add_table_to_string(input_str, table, leading_chars=None):
    for line in table:
        input_str += leading_chars + line + "\n"
    return input_str

def add_result_table(data, type, result, leading_chars="    "):
    items_list = []
    if type=="items":
        column_formats=["<3", "<20", "10.2f", "10.2f"]
        headers=["#", "Item", "Price (USD)", "Weight (kg)"]
        total_price = 0
        total_weight = 0
        for n, item in enumerate(data):
            items_list.append((n+1, item[0], item[1], item[2]))
            total_price += item[1]
            total_weight += item[2]
        items_list.append(("", "---", "", ""))
        items_list.append(("", "Total", total_price, total_weight))
    elif type=="cost":
        column_formats = ["<15", "10.2f"]
        headers = ["Cost Item", "Cost (USD)"]
        items_list = [("Transport costs", data.transport_cost.total),
                      ("  * Handling", data.transport_cost.handling),
                      ("  * Freight", data.transport_cost.freight),
                      ("  * Tax", data.transport_cost.tax),
                      ("  * TFSPU", data.transport_cost.TFSPU),
                      ("Import fee"+(" (exempted)" if data.import_fee_exempted else ""), data.import_fee),
                      ("---", ""),
                      ("Total", data.total_package_cost)]
    elif type=="total_cost":
        column_formats = ["<15", "10.2f"]
        headers = ["Cost Item", "Cost (USD)"]
        items_list = [("Total transport costs", data.total_transport_cost.total),
                      ("  * Handling", data.total_transport_cost.handling),
                      ("  * Freight", data.total_transport_cost.freight),
                      ("  * Tax", data.total_transport_cost.tax),
                      ("  * TFSPU", data.total_transport_cost.TFSPU),
                      ("Total import fee", data.total_import_fee),
                      ("---", ""),
                      ("Total", data.total_cost)]
    item_table = format_table(data=items_list,
                              column_formats=column_formats,
                              headers=headers)
    result = add_table_to_string(input_str=result,
                                 table=item_table,
                                 leading_chars=leading_chars)
    return result
