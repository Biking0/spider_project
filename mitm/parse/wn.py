import zlib
import json
import time
import base64
import socket

from jsonpath import jsonpath
from mitmproxy.ctx import log as logging

from utils import pubUtil, dataUtil


class WnParser:
    buffer = []
    st_time = 0
    count = 0
    carrier = 'wn'
    version = 1.2
    push_url = 'http://stock.jiaoan100.com/br/newairline?'
    # push_url = 'http://test.jiaoan100.com/br_test/newairline?'  # 测试库
    headers = []

    def __init__(self, host_name='hyn-test', num=1):
        if not host_name:
            host_name = socket.gethostname()
        self.host_name = host_name
        self.num = num
        self.city_ports = dataUtil.get_port_city()

    # 解析页面数据
    def parse(self, flow):
        response = flow.response
        req = flow.request
        headers = dict(req.headers)
        info = json.loads(req.data.content).get('int')
        headers_lib = zlib.compress(json.dumps(headers).encode('utf-8'))
        self.headers.append(base64.b64encode(headers_lib).decode('utf-8'))
        if response.status_code != 200:
            return
        logging.info('# start parse ')
        try:
            content = json.loads(response.text)
        except Exception as e:
            logging.info(e)
            logging.info(response.text)
            return
        try:
            air_product = jsonpath(content, '$..airProducts')[0][0]
        except:
            if content.get('code') == 400521204:
                logging.info(str(content.get('infoList')))
                return
        dep = air_product.get('originationAirportCode')
        arr = air_product.get('destinationAirportCode')
        products = air_product.get('details')

        for product in products:

            flight_numbers = product.get('flightNumbers')
            if len(flight_numbers) > 1:
                continue
            dep_time = product.get('departureDateTime').split('.000')[0]
            arr_time = product.get('arrivalDateTime').split('.000')[0]
            dep_stamp = time.mktime(time.strptime(dep_time, '%Y-%m-%dT%H:%M:%S'))
            arr_stamp = time.mktime(time.strptime(arr_time, '%Y-%m-%dT%H:%M:%S'))

            carrier = jsonpath(product, '$..marketingCarrierCode')[0]
            flight_number = carrier + flight_numbers[0]

            fares = jsonpath(product, '$..ADULT')[0]
            segments = [[0, 0]]
            low_fare = None
            low_price = 0
            for k, v in fares.items():
                if 'AVAILABLE' != v.get('availabilityStatus'):
                    continue
                this_price = float(jsonpath(v, '$..totalFare')[0].get('value'))
                if not low_fare or this_price < low_price:
                    low_fare = v
                    low_price = this_price
                if 'ANY' == k:
                    seat = v.get('fare').get('seatsLeft', 9)
                    segments[0] = [this_price, seat, info]

            item = dict()
            stop_details = product.get('stopsDetails')
            l_stop_details = len(stop_details)
            if l_stop_details > 2:
                continue
            if len(stop_details) > 1:
                item.update(dict(
                    stopCities=stop_details[0].get('destinationAirportCode')
                ))
            if not low_fare:
                item.update(dict(
                    maxSeats=0
                ))
            else:
                netfare = jsonpath(low_fare, '$..baseFare')[0].get('value')
                adult_tax = jsonpath(low_fare, '$..totalTaxesAndFees')[0].get('value')
                currency = jsonpath(low_fare, '$..currencyCode')[0]
                seat = low_fare.get('fare').get('seatsLeft', 9)
                cabin = low_fare.get('classOfService')
                item.update(dict(
                    maxSeats=seat,
                    cabin=cabin,
                    currency=currency,
                    adultTax=float(adult_tax),
                    netFare=float(netfare),
                    adultPrice=float(low_price),
                ))

            item.update(dict(
                flightNumber=flight_number,
                depAirport=dep,
                arrAirport=arr,
                carrier=carrier,
                depTime=dep_stamp,
                arrTime=arr_stamp,
                segments=json.dumps(segments),
                isChange=1,
                getTime=time.time(),
                fromCity=self.city_ports.get(dep, dep),
                toCity=self.city_ports.get(arr, arr),
                info=info
            ))

            logging.info(json.dumps(item))
            self.process_item(item)

    def process_item(self, item):
        self.buffer.append(item)
        self.count += 1
        this_time = time.time()
        if this_time - self.st_time >= 60:
            self.st_time = this_time
            logging.info(pubUtil.heartbeat(self.host_name, self.carrier, self.num, self.count, self.version))
            self.count = 0

        if len(self.buffer) > 5:
            add_success = pubUtil.addData('add', self.buffer, self.push_url, self.host_name, carrier=self.carrier)
            if add_success:
                logging.info(add_success)
                self.buffer.clear()

        if len(self.headers) > 5:
            add_success = pubUtil.push_cookies(self.headers, self.carrier)
            if add_success:
                logging.info(add_success)
                self.headers.clear()
