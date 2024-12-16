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
