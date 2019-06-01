# coding=utf-8
import os, json, time
import requests


base_dir =  os.path.dirname(__file__)

def load_file(file_name):
    with open(file_name, 'r') as f:
        resp = json.loads(f.read())
    return resp


def write_file(file_name, content):
    with open(file_name, 'w') as f:
        f.write(content)


def get_airport_city():
    url = 'http://dx.jiaoan100.com/br/portcity?carrier=EW'
    file_name = os.path.join(base_dir, u'port_city.json')

    if os.path.exists(file_name) and \
            time.time() - os.stat(file_name).st_mtime < 60*60:
        resp = load_file(file_name)
    else:
        try:
            response = requests.get(url, timeout=180)
        except Exception as e:
            print(e)
            resp = load_file(file_name)
        else:
            write_file(file_name, response.content)
            resp = response.json()
    return resp.get('data')


if __name__ == '__main__':
    print(get_airport_city().get('STN'))
