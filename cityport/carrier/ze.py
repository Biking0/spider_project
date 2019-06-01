import requests, json, jsonpath

air_port = {
    'GMP',
    'ICN',
    'CJU',
    'CJJ',
    'KUV',
    'PUS',
    'KOJ',
    'NRT',
    'KMI',
    'CTS',
    'KIX',
    'OKA',
    'IBR',
    'FUK',
    'PVG',
    'SHE',
    'YNJ',
    'HKG',
    'TSA',
    'TPE',
    'BKK',
    'BKI',
    'HAN',
    'DAD',
    'PPS',
    'VVO'
}

url = 'https://www.eastarjet.com/json/dataService'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
    'Referer': 'https://www.eastarjet.com/newstar/PGWHC00001',
    'Cookie': 'selected_country_code=CN; JSESSIONID=48DEAA6F76A529F42838FAA09A0BA6BA.WAS_93.WAS_93'

}

for i in air_port:
    post_data = {
        "id": 10,
        "method": "DataService.service",
        "params": [{
            "javaClass": "com.jein.framework.connectivity.parameter.RequestParameter",
            "requestUniqueCode": "PGWHC00001",
            "requestExecuteType": "SQL",
            "DBTransaction": 'false',
            "sourceName": "EASTAR",
            "sourceExtension": 'null',
            "functionName": "QRWHC00005",
            "panelId": 'null',
            "methodType": 'null',
            "inParameters": {
                "javaClass": "java.util.List",
                "list": [{
                    "javaClass": "com.jein.framework.connectivity.parameter.InParameter",
                    "paramName": "in_dpt_sttn_cd",
                    "ioType": "IN",
                    "structureType": "FIELD",
                    "data": {
                        "javaClass": "java.util.List",
                        "list": [{
                            "map": {
                                "in_dpt_sttn_cd": i
                            },
                            "javaClass": "java.util.Map"
                        }]
                    }
                }]
            },
            "filterParameter": {
                "javaClass": "java.util.Map",
                "map": {}
            }
        }]
    }

    reponse = requests.post(url, data=json.dumps(post_data), headers=headers)
    result_dict = json.loads(reponse.text)
    data_list = jsonpath.jsonpath(result_dict, '$..resultData')
    # print data_list
    # print i
    for data in data_list[0]:
        # print i
        if data.get('country_cd') == '': continue
        # print i+',',data.get('sttn_cd')
        print data.get('sttn_cd') + ',', data.get('country_cd')

    # print reponse.text
