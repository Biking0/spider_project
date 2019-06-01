import json

def get_currency():
    load_f = open(r'utils/dy_process_currency/depport_currency.json', 'r')
    dep_currency = json.load(load_f)
    return dep_currency