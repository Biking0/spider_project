import requests, json, time, csv, os

if __name__ == '__main__':
    url = 'https://be.wizzair.com/7.15.0/Api/asset/map?languageCode=en-gb&forceJavascriptOutput=true'
    text = requests.get(url, timeout=60).text
    st = text.index('[')
    end = text.rindex(';')
    data_dicts = json.loads(text[st: end])
    OutputFile = open(os.path.join('src', 'W6.csv'), 'w')
    writer = csv.writer(OutputFile)
    for data_dict in data_dicts:
        dep = data_dict.get('iata')
        cons = data_dict.get('connections')
        for con in cons:
            arr = con.get('iata')
            # print(con.get('operationStartDate'))
            # print(time.strptime(con.get('operationStartDate'), '%Y-%m-%dT%H:%M:%S'))
            try:
                st_time = time.mktime(time.strptime(con.get('operationStartDate'), '%Y-%m-%dT%H:%M:%S'))
                if st_time > time.time() + 24 * 60 * 60 * 30:
                    continue
            except:
                print(con.get('operationStartDate'))
                pass
            writer.writerow([dep, arr])
    OutputFile.close()