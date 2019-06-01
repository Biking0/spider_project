# -*- coding: utf-8 -*-
import re
import os
import csv
import json
import time
import logging
import traceback
import urllib as parse
from datetime import datetime, timedelta

import scrapy
from jsonpath import jsonpath

from utils.spe_util import vyUtil
from utils import dataUtil, pubUtil
from lmd_spiders.items import LmdSpidersItem


class A6eSpider(scrapy.Spider):
    name = '6e'
    allowed_domains = ['6eprodr4xdotrezapi.navitaire.com']
    start_urls = 'https://6eprodr4xdotrezapi.navitaire.com/api/v1/Graph'
    carrier = '6E'
    version = 2.0
    task = []
    seats = 3

    custom_settings = dict(
        DEFAULT_REQUEST_HEADERS={
            'host': "6eprodr4xdotrezapi.navitaire.com",
            'accept': "*/*",
            # 'authorization': session,
            'x-requested-with': "XMLHttpRequest",
            'accept-language': "zh-cn",
            'accept-encoding': "gzip, deflate",
            'content-type': "application/json",
            'origin': "file://",
            'user-agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML, like Gecko) "
                          "Mobile/14G60",
            'targetapiversion': "416",
            'targetapiplatform': "ios",
            'cache-control': "no-cache",
        },
        POST_DATA_FORMAT={
            "query": "mutation resetBooking{  bookingReset }  query Availability{  availabilityv2:indigoAvailability( request:{   passengers:{           types :[{type: \"ADT\", count: %s}]    },  fareFilters:{    types:[\"R\", \"Z\"]  },  criteria:[{stations:{destinationStationCodes:\"%s\",originStationCodes:\"%s\"},dates:{beginDate:\"%s\"}, filters:{ filter:Default, productClasses:[\"R\" , \"N\" , \"S\" , \"B\" , \"J\"] }, flightFilters:{type:All}, ssrCollectionsMode:Leg}],codes:{      currency:\"\", promotionCode:\"\"    },    taxesAndFees:TaxesAndFees  }  )  {  faresAvailable{    key    value {      classOfService      classType      downgradeAvailable      fareApplicationType      fareAvailabilityKey      fareClassOfService      fareCode      fareSequence      fareStatus      inboundOutBound      isAllotmentMarketFare      isGoverning      isSumOfSector      productClass      ruleNumber      ruleTariff      travelClassCode      passengerFares{        discountedFare        fareAmount        fareDiscountCode        loyaltyPoints        multiplier        passengerDiscountCode        passengerType        publishedFare        revenueFare        serviceCharges{          amount          code          collectType          currencyCode          detail          foreignAmount          foreignCurrencyCode          ticketCode          type        }      }    }  }  trips {      origin      destination      journeysAvailable {        flightType        designator{          arrival          departure          destination          origin        }        fares{          key          value{            availableCount            classOfService            fareAvailabilityKey            fareCode            isSumOfSector          }        }        notForGeneralUser    journeyKey    segments {          designator {            origin            destination            departure            arrival          }          cabinOfService          changeReasonCode          externalIdentifier{            carrierCode            identifier            opSuffix          }          identifier{            carrierCode            identifier            opSuffix          }          international          isBlocked          isChangeOfGauge          isHosted          isSeatmapViewable          segmentKey          segmentType          legs {            flightReference            legKey            seatmapReference            designator {              arrival              departure              destination              origin            }            flightReference            legInfo {              adjustedCapacity              arrivalTerminal              arrivalTime              arrivalTimeUtc              arrivalTimeVariant              backMoveDays              capacity              changeOfDirection              codeShareIndicator              departureTerminal              departureTime              departureTimeUtc              departureTimeVariant              equipmentType              equipmentTypeSuffix              eTicket              irop              lid              marketingCode              marketingOverride              onTime              operatedByText              operatingCarrier              operatingFlightNumber              operatingOpSuffix              outMoveDays              prbcCode              scheduleServiceType              sold              status              subjectToGovtApproval            }            nests{              adjustedCapacity              classNest            }            operationsInfo{              actualOffBlockTime            }            seatmapReference            ssrs{              available  lid sold ssrNestCode unitSold          }          }        }        stops        journeyKey              }    }  currencyCode  includeTaxesAndFees}}query lowfareAvailable{sevenDayCalendar:availabilityLowFarev2(request:{criteria:[{ destinationStationCodes:\"BLR\", originStationCodes:\"DEL\", beginDate:\"2018-11-16\", endDate:\"2018-11-16\" }],  includeTaxesAndFees:true,    codes:{      currency:\"INR\", promotionCode:\"\"    },  passengers:{           types :[{type: \"ADT\", count: 1}]    }}){ lowFareDateMarkets { lowestFareAmount { fareAmount, farePointAmount, taxesAndFeesAmount }, lowFares { passengers { key, value { discountCode, fareAmount, type, farePointAmount, taxesAndFeesAmount } }, bookingClasses , arrivalTime , departureTime , legs { arrivalTime , departureTime, destination, origin, flightNumber, carrierCode, equipmentType, operatingCarrier } , availableCount, productClass } , destination, origin, departureDate } , includeTaxesAndFees, currencyCode}}",
            "variables": "null",
            "operationName": "indigo"
        },

        GET_SESSION_HEADERS={
            'host': "6eprodr4xdotrezapi.navitaire.com",
            'accept': "*/*",
            'x-requested-with': "XMLHttpRequest",
            'accept-encoding': "gzip, deflate",
            'accept-language': "zh-cn",
            'content-type': "application/json",
            'user-agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML, like Gecko) Mobile/14G60",
            'targetapiversion': "416",
            'targetapiplatform': "ios",
        },
        GET_SESSION_DATA={
            "nskTokenRequest": {},
            "strToken": "",
            "subscriptionKey": "5468657365206172656E2774207468652064726F69647320796F75277265206C6F6F6B696E6720666F722E"
        },
        GET_SESSION_URL='https://6eprodr4xdotrezapi.navitaire.com/indigo/6esession',
        CONCURRENT_REQUESTS=8,

        LOG_LEVEL='INFO',

        DOWNLOADER_MIDDLEWARES={
            'lmd_spiders.middlewares.StatisticsItem': 200,
            'lmd_spiders.middlewares.A6eSessionMiddleware': 300,
        },

        # ITEM_PIPELINES={  # 往测试库添加数据
        #     'lmd_spiders.pipelines.LmdSpidersPipelineTest': 300,
        # },

    )

    def __init__(self, *args, **kwargs):
        cls = self.__class__
        super(cls, self).__init__(*args, **kwargs)
        self.port_citys = dataUtil.get_port_city()

    def start_requests(self):
        permins = 0
        print(pubUtil.heartbeat(self.host_name, self.name, self.num, permins, self.version))
        result_iter = None
        while True:
            if hasattr(self, 'local'):
                if not result_iter:
                    result_iter = pubUtil.get_task(self.name)
                result = next(result_iter)
            else:
                result = pubUtil.getUrl(self.carrier, 1)
            if not result:
                time.sleep(6)
                continue
            for data in result:
                (_dt, dep, to, days) = vyUtil.analysisData(data)
                for i in range(int(days)):
                    dt = (datetime.strptime(_dt, '%Y%m%d') + timedelta(days=i)).strftime('%Y-%m-%d')
                    # dt, dep, to = '2019-02-28', 'BLR', 'BKK'
                    post_data = self.custom_settings.get('POST_DATA_FORMAT').copy()
                    post_data['query'] = post_data.get('query') % (self.seats, to, dep, dt)
                    yield scrapy.Request(
                        url=self.start_urls,
                        method="POST",
                        body=json.dumps(post_data),
                        meta={'post_data': post_data},
                        dont_filter=True,
                    )

    def parse(self, response):
        # print(response.body)
        data_dict = json.loads(response.body)
        try:
            avail_data = jsonpath(data_dict, '$..availabilityv2')[0]
        except Exception as e:
            print(e)
            print(response.body)
            post_data = response.meta.get('post_data')
            yield scrapy.Request(
                url=self.start_urls,
                method="POST",
                body=json.dumps(post_data),
                meta={'post_data': post_data},
                dont_filter=True,
            )
            return
        if not avail_data:   # 当天无航班
            return
        currency = avail_data.get('currencyCode')

        fares = avail_data.get('faresAvailable')
        fare_temp = dict()
        if fares:
            for fare in fares:
                fare_temp[fare['key']] = fare['value']

        journeys = jsonpath(avail_data, '$..journeysAvailable')[0]
        for journey in journeys:
            flight_type = journey.get('flightType')
            if flight_type == 'Connect':  # 排除掉非直达航班
                continue
            legs = jsonpath(journey, '$..legs')[0]  # 排除掉多停航班
            if len(legs) > 2:
                continue
            s_cities = jsonpath(legs[1], '$..origin')[0] if len(legs) == 2 else ''
            is_change = 1

            designator = journey.get('designator')
            dep_time_str = designator.get('departure')  # %Y-%m-%dT%H:%M:%S
            arr_time_str = designator.get('arrival')  # %Y-%m-%dT%H:%M:%S
            dep_time = time.mktime(time.strptime(dep_time_str, '%Y-%m-%dT%H:%M:%S'))
            arr_time = time.mktime(time.strptime(arr_time_str, '%Y-%m-%dT%H:%M:%S'))
            dep = designator.get('origin')
            arr = designator.get('destination')

            identifier = journey.get('segments')[0].get('identifier')
            carrier = identifier.get('carrierCode')
            flight_number = carrier + identifier.get('identifier')
            is_inter = jsonpath(journey, '$..international')[0]
            fail_count = 0 if is_inter else 99
            if not fares or not journey.get('fares'):
                adult_price = 0
                net_fare = 0
                seats = 0
                cabin = ''
                segments = []
            else:
                fare_flag = journey.get('fares')
                low_fare = fare_flag[0]
                low_key = low_fare.get('key')
                low_prices = fare_temp.get(low_key)
                net_fare = jsonpath(low_prices, '$..discountedFare')[0]
                adult_price = jsonpath(low_prices, '$..fareAmount')[0]
                seats = jsonpath(low_fare, '$..availableCount')[0]
                cabin = jsonpath(low_fare, '$..fareCode')[0]

                # 国际线加350， 国内线加225
                adult_price += 350 if is_inter else 225

                # 套餐价格， 有问题。。。。。暂时未解决
                keys = ['0', 'U']
                segments = [[-1, -1]] * len(keys)
                for fare in fare_flag:
                    key = fare.get('key')
                    value = fare.get('value')
                    flag = value.get('fareCode')[1]
                    if flag in keys:
                        index = keys.index(flag)
                    else:
                        continue
                    seat_temp = value.get('availableCount')
                    if not seat_temp:
                        continue
                    price_temp = jsonpath(fare_temp.get(key), '$..fareAmount')[0]
                    price_temp += 350 if is_inter else 225
                    segments[index] = [price_temp, seat_temp]

            item = LmdSpidersItem()
            item.update(dict(
                flightNumber=flight_number,
                depAirport=dep,
                arrAirport=arr,
                carrier=carrier,
                depTime=dep_time,
                arrTime=arr_time,
                currency=currency,
                segments=json.dumps(segments),
                isChange=is_change,
                getTime=time.time(),
                fromCity=self.port_citys.get(dep, dep),
                toCity=self.port_citys.get(arr, arr),
                adultPrice=adult_price,
                netFare=net_fare,
                adultTax=adult_price - net_fare,
                maxSeats=seats,
                cabin=cabin,
                stopCities=s_cities,
                failCount=fail_count,
            ))
            yield item
