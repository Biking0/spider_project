import csv, requests, os

def refreshAirports():
    url = r'https://www.flybe.com/api/airports/airport'
    res = requests.get(url)
    text = res.text
    null = ''
    true = 'true'
    false = 'false'
    li = list(eval(text))
    city = []
    for i in li:
        city.append([i['code']])
    OutputFile = open(os.path.join(r'citiesOrAirports', 'flybe_ports.csv'), 'w')
    writer = csv.writer(OutputFile)
    writer.writerow(['port'])
    writer.writerows(city)
    OutputFile.close()

def getAirportsFromAll():
    inputFile = open(os.path.join('utils/source', 'all.csv'))
    read = csv.reader(inputFile)
    data = list(read)[1:]
    inputFile.close()
    return data

def getAirports():
    inputFile = open(os.path.join('utils/source', 'flybe_ports.csv'))
    read = csv.reader(inputFile)
    data = list(read)[1:]
    inputFile.close()
    return data

if __name__ == "__main__":
    refreshAirports()
    print(getAirports())
