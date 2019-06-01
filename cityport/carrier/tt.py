a = [
    {
        "value": "ADL",
        "label": "adelaide (ADL)",
        "destinations": [
            "213257",
            "193671",
            "193672"
        ],
        "id": "193673",
        "selected": False,
        "url": "flights/adelaide",
        "is_redirect": "0",
        "exclude_from": "0",
        "ranking": "0",
        "name": "adelaide"
    },
    {
        "value": "BNE",
        "label": "brisbane (BNE)",
        "destinations": [
            "193673",
            "193665",
            "193662",
            "193667",
            "193671",
            "193672"
        ],
        "id": "213257",
        "selected": False,
        "url": "flights/brisbane",
        "is_redirect": "0",
        "exclude_from": "0",
        "ranking": "0",
        "name": "brisbane"
    },
    {
        "value": "CNS",
        "label": "cairns (CNS)",
        "destinations": [
            "213257",
            "193671",
            "193672"
        ],
        "id": "193665",
        "selected": False,
        "url": "flights/cairns",
        "is_redirect": "0",
        "exclude_from": "0",
        "ranking": "0",
        "name": "cairns"
    },
    {
        "value": "CBR",
        "label": "canberra (CBR)",
        "destinations": [
            "213257",
            "193671"
        ],
        "id": "193662",
        "selected": False,
        "url": "flights/canberra",
        "is_redirect": "0",
        "exclude_from": "0",
        "ranking": "0",
        "name": "canberra"
    },
    {
        "value": "CFS",
        "label": "coffs harbour (CFS)",
        "destinations": [
            "193671",
            "193672"
        ],
        "id": "193669",
        "selected": False,
        "url": "flights/coffs-harbour",
        "is_redirect": "0",
        "exclude_from": "0",
        "ranking": "0",
        "name": "coffs harbour"
    },
    {
        "value": "DRW",
        "label": "darwin (DRW)",
        "destinations": [
            "213257"
        ],
        "id": "193667",
        "selected": False,
        "url": "flights/darwin",
        "is_redirect": "0",
        "exclude_from": "0",
        "ranking": "0",
        "name": "darwin"
    },
    {
        "value": "OOL",
        "label": "gold coast (OOL)",
        "destinations": [
            "193666",
            "193671",
            "193672"
        ],
        "id": "193664",
        "selected": False,
        "url": "flights/gold-coast",
        "is_redirect": "0",
        "exclude_from": "0",
        "ranking": "0",
        "name": "gold coast"
    },
    {
        "value": "HBA",
        "label": "hobart (HBA)",
        "destinations": [
            "193664",
            "193671"
        ],
        "id": "193666",
        "selected": False,
        "url": "flights/hobart",
        "is_redirect": "0",
        "exclude_from": "0",
        "ranking": "0",
        "name": "hobart"
    },
    {
        "value": "MEL",
        "label": "melbourne (MEL)",
        "destinations": [
            "193673",
            "213257",
            "193665",
            "193662",
            "193669",
            "193664",
            "193666",
            "193663",
            "193672"
        ],
        "id": "193671",
        "selected": False,
        "url": "flights/melbourne",
        "is_redirect": "0",
        "exclude_from": "0",
        "ranking": "0",
        "name": "melbourne"
    },
    {
        "value": "PER",
        "label": "perth (PER)",
        "destinations": [
            "193671",
            "193672"
        ],
        "id": "193663",
        "selected": False,
        "url": "flights/perth",
        "is_redirect": "0",
        "exclude_from": "0",
        "ranking": "0",
        "name": "perth"
    },
    {
        "value": "SYD",
        "label": "sydney (SYD)",
        "destinations": [
            "193673",
            "213257",
            "193665",
            "193669",
            "193664",
            "193671",
            "193663",
            "193670"
        ],
        "id": "193672",
        "selected": False,
        "url": "flights/sydney",
        "is_redirect": "0",
        "exclude_from": "0",
        "ranking": "0",
        "name": "sydney"
    },
    {
        "value": "PPP",
        "label": "whitsundays coast (PPP)",
        "destinations": [
            "193672"
        ],
        "id": "193670",
        "selected": False,
        "url": "flights/whitsunday",
        "is_redirect": "0",
        "exclude_from": "0",
        "ranking": "0",
        "name": "whitsundays coast"
    }
]
data = {}
for dep in a:
    data[dep.get('id')] = dep.get('value')


import csv



OutputFile = open('TT.csv', 'wb')
writer = csv.writer(OutputFile)
for dep_list in a:
    dep = dep_list.get('value')
    for arr_id in dep_list.get('destinations'):
        to = data.get(arr_id)
        writer.writerow([dep, to])
        print(dep, to)

OutputFile.close()