# encoding=utf-8


data = {
    'AGF',
    'AJA',
    'ANE',
    'AUR',
    'BIA',
    'BIQ',
    'BOD',
    'BES',
    'BVE',
    'CFR',
    'CLY',
    'DCM',
    'CFE',
    'FSC',
    'LRH',
    'LIL',
    'LRT',
    'LYS',
    'MRS',
    'ETZ',
    'MPL',
    'MLH',
    'NTE',
    'NCE',
    'CDG',
    'ORY',
    'PUF',
    'PGF',
    'PIS',
    'UIP',
    'RNS',
    'URO',
    'SXB',
    'LDE',
    'TLN',
    'TLS',
    'BLQ',
    'BRU',
    'DUS',
    'GVA',
    'HAM',
    'MXP',
    'NUE',
    'PRG',
    'FCO',
    'VCE'
}

#笛卡尔积
for i in data:
    for j in data:
        if i != j:
            print i+','+j
