import requests, json

url1 = 'https://www.tui.co.uk/searchpanel/departureairport/fo?when=&flexible=true&multiSelect=&isOneWay=true'

# response=requests.get(url1)
#
#
#
#
# for key,value in json.loads(response.text).items():
#     for i in value:
#         print i['id']


# print key

# print json.loads(response.text)

#国家代码
dep_list = [
    'ANU',
    'HRG',
    'RMF',
    'LAX',
    'EWR',
    'SFB',
    'LRM',
    'POP',
    'PUJ',
    'LIM',
    'CMB',
    'DPS',
    'BOJ',
    'VAR',
    'ABZ',
    'BHD',
    'BFS',
    'BHX',
    'BOH',
    'BRS',
    'CWL',
    'LDY',
    'DSA',
    'EMA',
    'EDI',
    'EXT',
    'GLA',
    'HUY',
    'INV',
    'JER',
    'LBA',
    'LPL',
    'LCY',
    'LGW',
    'LHR',
    'LTN',
    'SEN',
    'STN',
    'MAN',
    'NCL',
    'NWI',
    'SOU',
    'KEF',
    'BDS',
    'SUF',
    'MXP',
    'NAP',
    'OLB',
    'AHO',
    'CTA',
    'VCE',
    'VRN',
    'BVC',
    'SID',
    'CFU',
    'CHQ',
    'HER',
    'KLX',
    'KVA',
    'EFL',
    'KGS',
    'PVK',
    'RHO',
    'SMI',
    'JTR',
    'JSI',
    'SKG',
    'ZTH',
    'LCA',
    'PFO',
    'MRU',
    'PQC',
    'LIR',
    'ZNZ',
    'FAO',
    'FNC',
    'PXO',
    'KRK',
    'MLE',
    'TGD',
    'AJA',
    'ALC',
    'LEI',
    'FUE',
    'GRO',
    'LPA',
    'IBZ',
    'XRY',
    'SPC',
    'ACE',
    'AGP',
    'MAH',
    'PMI',
    'REU',
    'TFS',
    'DBV',
    'PUY',
    'RJK',
    'SPU',
    'PEK',
    'MBJ',
    'INN',
    'SZG',
    'MLA',
    'AUA',
    'KAO',
    'KBV',
    'HKT',
    'UTP',
    'AGA',
    'RAK',
    'BGI',
    'JNB',
    'ADB',
    'AYT',
    'DLM',
    'BJV',
    'MCT',
    'CUN',
    'PVR',
    'DWC',
    'NBE',
    'UVF',
    'COK',
    'GOI',
    'LGK',
    'HAV',
    'SNU',
    'VRA'

]

count_a = 0
count_b = 0

for i in dep_list:
    # print '############'+str(count_a)
    count_a += 1

    url2 = 'https://www.tui.co.uk/searchpanel/arrivalairport/fo?from[]='
    url3 = '&when=&flexible=true&multiSelect=&isOneWay=true'

    url = url2 + i + url3

    # print url
    response = requests.get(url)
    response.status_code
    # print response.text

    for key, value in json.loads(response.text).items():
        for j in value:
            # print j[1]
            # print count_b
            count_b += 1
            # print (j['available'])
            # print (type(j['available']))
            if j['available'] == True:

                print(i + ',' + j['id'])
