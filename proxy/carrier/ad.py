#coding:utf-8
import random,traceback,re
import json,time,requests,logging
from datetime import datetime,timedelta
from lxml import etree


def is_ad_ok(proxies,timeout=15):
    return True
    dt = (datetime.now() + timedelta(days=random.randint(3, 10))).strftime('%Y-%m-%d')
    dep, to = 'CWB', 'VCP'
    url = "https://viajemais.voeazul.com.br/Availability.aspx"

    payload = {
        'SearchControlGroupAvailabilityView$SearchControlAvailabilityView$DropDownListPassengerType_ADT': '3',
        'hdfSearchCodeArrival1': '',
        'SearchControlGroupAvailabilityView$SearchControlAvailabilityView$TextBoxMarketOrigin1': dep,
        'SearchControlGroupAvailabilityView$SearchControlAvailabilityView$DropDownListMarketMonth1': re.sub(
            r'(\d{4})-(\d{2})-(\d{2})', r'\1-\2', dt),
        'SearchControlGroupAvailabilityView$SearchControlAvailabilityView$TextBoxMarketDestination1': to,
        'SearchControlGroupAvailabilityView$SearchControlAvailabilityView$DropDownListMarketDay1': re.sub(
            r'(\d{4})-(\d{2})-(\d{2})', r'\3', dt),
        'faretypes': 'R',
        '__EVENTTARGET': 'SearchControlGroupAvailabilityView$LinkButtonSubmit',
        'SearchControlGroupAvailabilityView$SearchControlAvailabilityView$DropDownListFareTypes': 'R',
        'pageToken': '',
        'loginDomain': 'AZUL_LOGIN',
        '_authkey_': '',
        'arrival': '',
        'SearchControlGroupAvailabilityView$SearchControlAvailabilityView$DropDownListPassengerType_CHD': '0',
        'SearchControlGroupAvailabilityView$SearchControlAvailabilityView$DropDownListPassengerType_INFANT': '0',
        'hdfSearchCodeArrival2': '',
        '__VIEWSTATE': '/wEPDwUBMGRkZ/qdcJAW2QnebbciaZoBYUGCuQI=', 'password-ta': '',
        'SearchControlGroupAvailabilityView$SearchControlAvailabilityView$RadioButtonMarketStructure': 'OneWay',
        'hdfSearchCodeDeparture2': '',
        '__EVENTARGUMENT': '',
        'departure2': '',
        'SearchControlGroupAvailabilityView$SearchControlAvailabilityView$CheckBoxUseMacOrigin2': '',
        'AvailabilityInputAvailabilityView$DropdownListOrderFlights': '0',
        'SearchControlGroupAvailabilityView$SearchControlAvailabilityView$CheckBoxUseMacDestination2': '',
        'hdfSearchCodeDeparture1': '',
        'login-ta': '',
    }
    headers = {
        'origin': "https://viajemais.voeazul.com.br",
        'upgrade-insecure-requests': "1",
        'content-type': "application/x-www-form-urlencoded",
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        'referer': "https://viajemais.voeazul.com.br/Availability.aspx",
        'accept-encoding': "gzip, deflate, br",
        'accept-language': "zh-CN,zh;q=0.9",
        'cookie': "ad_gdpr=0; sticky=two; VisitorIdAunica=undefined; cro_test=true;",
    }

    try:
        response = requests.request("POST", url, data=payload, headers=headers, proxies=proxies,verify=False,timeout=timeout,stream=True)

        res = etree.HTML(response.text)
        error = res.xpath('//table[@id="tbl-depart-flights"]/tbody/tr')
        if error:
            # print(error)
            return True


        return False
    except:
        traceback.print_exc()
        return False

def _get_proxy():
    proxy=''
    try:
        url = 'http://dx.proxy.jiaoan100.com/proxy/getproxy?carrier=be'
        li = json.loads(requests.get(url,timeout=60).text)
        logging.info('Proxy Num:' + str(len(li)))
        logging.info(str(li))
        proxy = random.choice(li) or ''

        print(proxy)
    except:
        # traceback.print_exc()
        logging.info('get proxy error....')
    finally:
        return proxy or ''




if __name__ == '__main__':
    while True:
        ip_port = _get_proxy()
        proxies = {
            'http':'http://%s'%ip_port,
            'https':'https://%s'%ip_port
        }
        print(is_ad_ok(proxies))
        time.sleep(5)