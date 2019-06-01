# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime, timedelta
import json, urllib, time, traceback, logging, requests
from jsonpath import jsonpath
from a7c_spider.pipelines import A7CSpiderPipeline
from a7c_spider.items import FlightsItem
from a7c_spider.settings import DEFAULT_REQUEST_HEADERS
from utils.process_airport_city.get_airport_city import get_airport_city
from utils.airports_rd import get_airports


class A7cSpider(scrapy.Spider):
    name = '7c'
    version = 2.0
    seats = 3
    is_ok = True

    start_urls = 'https://ibsearch.jejuair.net/jejuair/com/jeju/ibe/searchAvail.do?'
    tax_url = 'https://ibsearch.jejuair.net/jejuair/com/jeju/ibe/searchFareTax.do?'
    city_airport = get_airport_city()

    def start_requests(self):
        permins = 0
        print(A7CSpiderPipeline.heartbeat(self.host_name, '7C', self.num, permins, self.version))
        while True:
            for airports in get_airports():
                FROM = airports.get('DepartureAirportCode')
                TO = airports.get('ArrivalAirportCode')

                # 航线类型
                if 'CJU' in airports.values():
                    RouteType = 'D'
                else:
                    RouteType = 'I'

                # 日期加周索引
                dates = self._get_dates()
                first_date = dates[0][0].replace('-', '') + '0000'
                # 请求航线税费
                tax_params = urllib.urlencode(dict(
                    ReqType='Price',
                    RouteType=RouteType,
                    SystemType='IBE',
                    Language='EN',
                    DepStn=FROM,
                    ArrStn=TO,
                    SegType='DEP',
                    TripType='OW',
                    DepDate=first_date,
                    ArrDate=first_date,
                    FltNo=1,
                    RBD='M',
                ))

                total_url = self.tax_url + tax_params
                yield scrapy.Request(url=total_url,
                                     meta={
                                         'FROM': FROM, 'TO': TO,
                                         'RouteType': RouteType,
                                         'dates': dates
                                     },
                                     dont_filter=True,
                                     callback=self.transition,
                                     errback=self.err_back)

    def err_back(self, failure):
        self.log(failure.value, 40)
        self.log(failure.request.meta.get('proxy'))
        self.is_ok = False
        return failure.request

    def transition(self, response):
        result = jsonpath(json.loads(response.text), '$..data..taxAmount')
        self.is_ok = True
        meta = response.meta
        FROM = meta.get('FROM')
        TO = meta.get('TO')
        RouteType = meta.get('RouteType')
        dates = meta.get('dates')
        if not result:
            print(response)
            print(FROM, TO, ' got tax error')
            return
        tax = max(map(lambda x: float(x), result))

        for date in dates:
            params = urllib.urlencode(dict(
                AdultPaxCnt=self.seats,
                ChildPaxCnt=0,
                InfantPaxCnt=0,
                RouteType=RouteType,
                SystemType='IBE',
                Language='EN',
                DepStn=FROM,
                ArrStn=TO,
                SegType='DEP',
                TripType='OW',
                DepDate=date[0],
                Index=date[1]
            ))
            # print(date[0])

            total_url = self.start_urls + params
            yield scrapy.Request(url=total_url,
                                 meta={
                                     'FROM': FROM, 'TO': TO,
                                     'RouteType': RouteType,
                                     'tax': tax
                                 },
                                 dont_filter=True,
                                 callback=self.parse,
                                 errback=self.err_back)

    def parse(self, response):
        meta = response.meta
        FROM = meta.get('FROM')
        TO = meta.get('TO')
        RouteType = meta.get('RouteType')

        from_city = self.city_airport.get(FROM, FROM)
        to_city = self.city_airport.get(TO, TO)

        try:
            result = json.loads(response.body)
            self.is_ok = True

            if RouteType == 'I':
                datas = jsonpath(result, '$..availData.*')
            else:
                datas = jsonpath(result, '$..data.*')

            if not datas:
                # print('# get data error')
                return
            for availData in datas:
                # print(json.dumps(availData))
                carrier = availData.get('carrier')
                currency = availData.get('currency')
                depDate = availData.get('depDate')
                arrDate = availData.get('arrDate')
                depTime = depDate + availData.get('depTime')
                arrTime = arrDate + availData.get('arrTime')
                depStn = availData.get('depStn')
                arrStn = availData.get('arrStn')
                fltNo = availData.get('fltNo')

                # 特价客票
                specialEquivFare = availData.get('specialEquivFare')
                specialRBD = availData.get('specialRBD')
                specialSeatCount = availData.get('specialSeatCount')

                # 优惠客票
                discountEquivFare = availData.get('discountEquivFare')
                discountRBD = availData.get('discountRBD')
                discountSeatCount = availData.get('discountSeatCount')

                # FlyBag
                seatCount = availData.get('seatCount')
                RBD = availData.get('RBD')
                equivValueFare = availData.get('equivValueFare')

                # FlyBags+
                equivPremiumFare = availData.get('equivPremiumFare')

                # # 正常客票，页面不显示该票价
                # normalEquivFare = availData.get('normalEquivFare')
                # normalRBD = availData.get('normalRBD')
                # normalSeatCount = availData.get('normalSeatCount')

                # 添加套餐
                segments = []
                # 非套餐价，页面显示最低价
                # if discountEquivFare and discountSeatCount != '0':
                #     netFare = float(discountEquivFare)
                #     maxSeats = discountSeatCount
                #     tax = meta.get('tax')
                #     segments.append([netFare + tax, int(maxSeats)])
                # else:
                #     segments.append([0, 0])

                if availData.get('seatCount') != '0':
                    if equivValueFare:
                        netFare = float(equivValueFare)
                        tax = meta.get('tax')
                        segments.append([netFare + tax, int(seatCount)])
                    else:
                        segments.append([0, 0])
                    if equivPremiumFare:
                        netFare = float(equivPremiumFare)
                        tax = meta.get('tax')
                        segments.append([netFare + tax, int(seatCount)])
                    else:
                        segments.append([0, 0])
                else:
                    segments = [[0, 0], [0, 0]]

                # 这个价格通常在网页上不显示
                # if normalEquivFare and normalSeatCount != '0':
                #     netFare = float(normalEquivFare)
                #     maxSeats = normalSeatCount
                #     tax = meta.get('tax')
                #     segments.append([netFare + tax, int(maxSeats)])
                # else:
                #     segments.append([0, 0])

                # 取最低价
                if specialEquivFare and specialSeatCount != '0':
                    bundle = float(jsonpath(availData, '$..bundlePrice')[0])
                    netFare = float(specialEquivFare) + bundle
                    cabin = specialRBD
                    maxSeats = specialSeatCount
                    tax = meta.get('tax')

                elif discountEquivFare and discountSeatCount != '0':
                    netFare = float(discountEquivFare)
                    cabin = discountRBD
                    maxSeats = discountSeatCount
                    tax = meta.get('tax')

                elif equivValueFare and seatCount != '0':
                    netFare = float(equivValueFare)
                    cabin = RBD
                    maxSeats = seatCount
                    tax = meta.get('tax')

                elif equivPremiumFare and seatCount != '0':
                    netFare = float(equivPremiumFare)
                    cabin = RBD
                    maxSeats = seatCount
                    tax = meta.get('tax')

                # # 这个价格通常在网页上不显示
                # elif normalEquivFare and normalSeatCount != '0':
                #     netFare = float(normalEquivFare)
                #     cabin = normalRBD
                #     maxSeats = normalSeatCount
                #     tax = meta.get('tax')

                else:
                    netFare = 0.0
                    cabin = seatCount
                    maxSeats = 0
                    tax = 0.0

                item = FlightsItem()
                item.update(dict(
                    flightNumber=carrier + fltNo,  # 航班号
                    depTime=time.mktime(time.strptime(depTime, "%Y%m%d%H%M")).__int__(),  # 出发时间
                    arrTime=time.mktime(time.strptime(arrTime, "%Y%m%d%H%M")).__int__(),  # 达到时间
                    fromCity=from_city,  # 出发城市
                    toCity=to_city,  # 到达城市
                    depAirport=depStn,  # 出发机场
                    arrAirport=arrStn,  # 到达机场
                    currency=currency,  # 货币种类
                    adultPrice=netFare + tax,  # 成人票价
                    adultTax=tax,  # 税价
                    netFare=netFare,  # 净票价
                    maxSeats=maxSeats,  # 可预定座位数
                    cabin=cabin,  # 舱位
                    carrier=carrier,  # 航空公司
                    isChange=1,  # 是否为中转 1.直达2.中转
                    segments=json.dumps(segments),  # 中转时的各个航班信息
                    getTime=time.mktime(datetime.now().timetuple()).__int__(),
                ))
                yield item
        except:
            logging.error(traceback.format_exc())
            print(datas)
            pass

    @staticmethod
    def _get_dates():
        dates = []
        for _day in range(1, 46):
            date = datetime.utcnow() + timedelta(_day)
            dates.append((date.strftime('%Y-%m-%d'), date.weekday()))
        return dates


if __name__ == '__main__':
    a = A7cSpider()
    print(a._get_dates())
    print(DEFAULT_REQUEST_HEADERS)
