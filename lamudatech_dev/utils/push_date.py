# coding=utf-8
import requests, json, traceback, random


def push_date(url, params, action, data_array, nodename=None):
    '''
    :param url: PUSH_DATA_URL
    :param params: {'carrier': carrier}
    :param action: 'add' or 'invalid'
    :param array: [item, item]
    :return: status_code
    '''
    data = {
        "action": action,
        "data": data_array,
        "name": nodename
    }
    if isinstance(url, dict):
        url = get_random_url(url)
    # print(url)
    try:
        response = requests.post(url, params=params,
                                 data=json.dumps(data),
                                 timeout=180)
        return response.content
    except:
        # traceback.print_exc()
        return None

def get_random_url(data_dict):
    start = 0
    prob = data_dict.values()
    randnum = random.randint(1, sum(prob))
    for k, v in data_dict.items():
        start += v
        if randnum <= start:
            return k


if __name__ == '__main__':
    task = [{
        'arrAirport': 'BHX',
        'date': '20180622',
        'depAirport': 'VIE',
    },{
        'arrAirport': 'BHX',
        'date': '20180612',
        'depAirport': 'VIE',
    },{
        'arrAirport': 'BHX',
        'date': '20180613',
        'depAirport': 'VIE',
    }]
    print(push_date('http://dx.spider2.jiaoan100.com/br/newairline?', {'carrier': 'EW'},  'invalid', task))
