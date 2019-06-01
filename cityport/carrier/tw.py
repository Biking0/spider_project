import requests
def get_data():
    url = "https://flights.ws.ctrip.com/Flight.Order.SupplierOpenAPI/OpenIssueOrderList.asmx"

    payload = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n\n<soap12:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:soap12=\"http://www.w3.org/2003/05/soap-envelope\">\n\n \n\n  <soap12:Body>\n\n    <Handle xmlns=\"http://tempuri.org/\">\n\n      <requestXML>\n\n       <![CDATA[ <Request UserName=\"green\" UserPassword=\"afcf173c482622b1cf520e1f4d29d72f\"> <OpenIssueOrderListRequest> <OrderBeginDateTime>2018-10-08T11:00:00</OrderBeginDateTime> <OrderEndDateTime>2018-10-08T14:16:00</OrderEndDateTime> </OpenIssueOrderListRequest> </Request>\n\n \n\n]]>\n\n</requestXML>\n\n    </Handle>\n\n  </soap12:Body>\n\n</soap12:Envelope>"
    headers = {
        'soapaction': "http://tempuri.org/Handle",
        'content-type': "text/xml; charset=utf-8",
        'cache-control': "no-cache",
        'postman-token': "0b8fff82-3daf-0032-cae4-ed6f2ac66330"
        }

    response = requests.request("POST", url, data=payload, headers=headers)

    print(response.text)

    return response.text

# def parse():

if __name__ == '__main__':
    get_data()