import json, jsonpath
import requests

url = 'https://dpel.elal.co.il:449/ElalAppWS/api/Search/GetSearchDestiationCities'

city = [
    'AAQ(2)',
    'ABA(2)',
    'ABQ(1)',
    'ABZ(2)',
    'ACE(2)',
    'AER(2)',
    'AGP(2)',
    'AGP(3)',
    'AKL(2)',
    'ALC(2)',
    'AMS(1)',
    'AOI(2)',
    'ATH(1)',
    'ATL(2)',
    'AUA(2)',
    'AUS(1)',
    'AXD(2)',
    'BAX(2)',
    'BCN(1)',
    'BCN(3)',
    'BDA(2)',
    'BDS(2)',
    'BER(1)',
    'BFS(2)',
    'BHX(2)',
    'BIO(2)',
    'BJS(1)',
    'BKK(1)',
    'BLQ(2)',
    'BLR(2)',
    'BNA(2)',
    'BNE(2)',
    'BOD(2)',
    'BOG(2)',
    'BOM(1)',
    'BOS(1)',
    'BRE(2)',
    'BRI(2)',
    'BRS(2)',
    'BRU(1)',
    'BTV(1)',
    'BUD(1)',
    'BUE(2)',
    'BUF(1)',
    'BUH(1)',
    'BUR(1)',
    'BWI(2)',
    'CAG(2)',
    'CAG(3)',
    'CAN(2)',
    'CCU(2)',
    'CGN(2)',
    'CHI(2)',
    'CHS(1)',
    'CLE(2)',
    'CLT(1)',
    'CMB(2)',
    'CMH(2)',
    'COK(2)',
    'CPH(2)',
    'CPT(2)',
    'CTA(2)',
    'CTU(2)',
    'CUN(2)',
    'CVG(2)',
    'DEL(2)',
    'DEN(1)',
    'DFW(2)',
    'DRS(2)',
    'DTT(2)',
    'DUB(2)',
    'DUR(2)',
    'DUS(2)',
    'EDI(2)',
    'FAT(2)',
    'FLL(1)',
    'FLR(2)',
    'FMO(2)',
    'FMY(2)',
    'FRA(1)',
    'FUE(2)',
    'GLA(2)',
    'GNB(2)',
    'GNB(3)',
    'GOA(2)',
    'GOI(2)',
    'GOJ(2)',
    'GSO(2)',
    'GVA(1)',
    'HAJ(2)',
    'HAM(2)',
    'HAN(2)',
    'HAR(2)',
    'HEL(2)',
    'HER(2)',
    'HER(3)',
    'HGH(2)',
    'HKG(1)',
    'HOU(1)',
    'IBZ(2)',
    'IBZ(3)',
    'IEV(1)',
    'IND(2)',
    'INN(2)',
    'IXE(2)',
    'JAX(1)',
    'JDH(2)',
    'JNB(1)',
    'KGD(2)',
    'KIX(2)',
    'KJA(2)',
    'KRK(2)',
    'KRK(3)',
    'KRR(2)',
    'KRS(2)',
    'KTM(2)',
    'KUF(2)',
    'KZN(2)',
    'LAS(1)',
    'LAX(1)',
    'LBA(2)',
    'LCA(1)',
    'LCG(2)',
    'LED(2)',
    'LEJ(2)',
    'LGB(1)',
    'LIS(2)',
    'LIS(3)',
    'LIT(2)',
    'LJU(2)',
    'LJU(3)',
    'LON(1)',
    'LPA(2)',
    'LYS(2)',
    'MAA(2)',
    'MAD(1)',
    'MAD(3)',
    'MAH(2)',
    'MAN(2)',
    'MEL(2)',
    'MEM(2)',
    'MHT(2)',
    'MIA(1)',
    'MIL(1)',
    'MKC(2)',
    'MLA(2)',
    'MOW(1)',
    'MPL(2)',
    'MRS(1)',
    'MRV(2)',
    'MSP(2)',
    'MSY(1)',
    'MUC(1)',
    'MUC(3)',
    'NAP(2)',
    'NAP(3)',
    'NCE(2)',
    'NCE(3)',
    'NCL(2)',
    'NKG(2)',
    'NOZ(2)',
    'NUE(2)',
    'NUX(2)',
    'NWI(2)',
    'NYC(1)',
    'NYM(2)',
    'OAK(1)',
    'ODS(3)',
    'OKC(2)',
    'OMS(2)',
    'OPO(2)',
    'OPO(3)',
    'ORF(2)',
    'ORL(1)',
    'OSL(2)',
    'OVB(2)',
    'OVD(2)',
    'PAR(1)',
    'PBI(1)',
    'PDX(1)',
    'PEE(2)',
    'PER(2)',
    'PHL(2)',
    'PHX(1)',
    'PIT(2)',
    'PLZ(2)',
    'PMI(2)',
    'PMO(2)',
    'PRG(1)',
    'PSA(2)',
    'PWM(1)',
    'RDU(1)',
    'REG(2)',
    'RHO(2)',
    'RHO(3)',
    'RIC(2)',
    'RNO(2)',
    'ROC(1)',
    'ROM(1)',
    'ROV(2)',
    'RSW(2)',
    'SAC(2)',
    'SAN(1)',
    'SAT(2)',
    'SAV(1)',
    'SBA(2)',
    'SCL(2)',
    'SCQ(2)',
    'SDF(2)',
    'SEA(1)',
    'SEL(2)',
    'SFO(1)',
    'SGN(2)',
    'SHA(2)',
    'SIP(2)',
    'SJC(1)',
    'SJO(2)',
    'SJU(2)',
    'SKG(2)',
    'SLC(1)',
    'SNA(2)',
    'SOF(1)',
    'SRQ(1)',
    'STL(2)',
    'STO(2)',
    'STR(2)',
    'STR(3)',
    'STW(2)',
    'SUF(2)',
    'SVQ(2)',
    'SVX(2)',
    'SXB(2)',
    'SYD(2)',
    'SYR(1)',
    'TAO(2)',
    'TBS(3)',
    'TCI(2)',
    'TJM(2)',
    'TLL(2)',
    'TLS(2)',
    'TLV(1)',
    'TLV(3)',
    'TOF(2)',
    'TPA(1)',
    'TPE(2)',
    'TRS(2)',
    'TYO(2)',
    'UFA(2)',
    'UUD(2)',
    'VCE(1)',
    'VDA(1)',
    'VGO(2)',
    'VIE(1)',
    'VLC(2)',
    'VLC(3)',
    'VRN(2)',
    'WAS(1)',
    'WAW(1)',
    'XRY(2)',
    'YEA(2)',
    'YHZ(2)',
    'YMQ(2)',
    'YOW(2)',
    'YQR(2)',
    'YTO(1)',
    'YVR(2)',
    'YWG(2)',
    'YYC(2)',
    'ZAG(2)',
    'ZAG(3)',
    'ZNZ(3)',
    'ZRH(1)',
]

for i in city:
    post_data = {
        "FlightType": "1",
        "CityCode": i,
        "LanguageCode": "EN",
        "UserId": 1569337
    }

    response = requests.post(url, data=post_data)

    arr = json.loads(response.text)

    city_list = jsonpath.jsonpath(arr, '$..DestinationCities')[0]

    for j in city_list:
        print i[:3] + ',' + j.get('CityCode')[:3]
