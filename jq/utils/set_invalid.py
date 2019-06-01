
import logging, requests, time, json, sys
sys.path.append('..')
import settings
def set_invalid(carrier, depAirport, arrAirport, date):
    infos = {
        'date': date.replace('-', ''),
        'depAirport': depAirport.encode('ascii'),
        'arrAirport': arrAirport.encode('ascii'),
    }
    data = {
        'action': 'invalid',
        'data': [infos]
    }
    print(data)
    param = {'carrier': carrier}
    requests.adapters.DEFAULT_RETRIES = 5
    try:
        res = requests.post(settings.PUSH_DATA_URL, params=param, data=json.dumps(data), headers={'Connection': 'close'})
        print('pushData: ' + res.text + ' num: ' + str(len(infos)) + ' invalid')
        s = requests.session()
        s.keep_alive = False
    except:
        time.sleep(0.01)
        logging.error('set invalid error....')

if __name__ == '__main__':
    set_invalid('JX', 'HAN', 'SGN', '20181123')