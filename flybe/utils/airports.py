import json, sys
sys.path.append('..')
from utils.source import flybePorts
from flybe_spider import settings
import requests

def getFlybePorts():
    for i in flybePorts.getAirportsFromAll():
        yield i

def getCityPortsByJson():
    f = open('utils/source/cityPorts.json', 'r')
    cityPorts = json.load(f)
    return cityPorts

def getCityPortsByAPI(carrier='BE'):
    param = {'carrier': carrier}
    try:
        res = requests.get(settings.GET_CITYPORTS_URL, params=param)
    except:
        return getCityPortsByJson()
    data = json.loads(res.text)
    return data.get('data')

if __name__ == "__main__":
    print(getCityPortsByAPI())
