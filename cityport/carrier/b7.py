import csv
AryDomThr3 = ["Sungsan(TSA)", "Taichung(RMQ)", "Chiayi(CYI)", "Tainan(TNN)", "Kaohsiung(KHH)", "Taitung(TTT)", "Kinmen(KNH)", "Makung(MZG)", "Nangan(LZN)", "Peigan(MFK)", "Hengchun(HCN)"]
AryDomDes3 = range(11)
AryDomDes3[0] = ["Taitung(TTT)", "Kinmen(KNH)", "Makung(MZG)", "Nangan(LZN)", "Peigan(MFK)", "Hengchun(HCN)"]
AryDomDes3[1] = ["Kinmen(KNH)", "Makung(MZG)", "Nangan(LZN)"]
AryDomDes3[2] = ["Kinmen(KNH)", "Makung(MZG)"]
AryDomDes3[3] = ["Kinmen(KNH)", "Makung(MZG)"]
AryDomDes3[4] = ["Kinmen(KNH)", "Makung(MZG)"]
AryDomDes3[5] = ["Sungsan(TSA)"]
AryDomDes3[6] = ["Sungsan(TSA)", "Taichung(RMQ)", "Chiayi(CYI)", "Tainan(TNN)", "Kaohsiung(KHH)"]
AryDomDes3[7] = ["Sungsan(TSA)", "Taichung(RMQ)", "Chiayi(CYI)", "Tainan(TNN)", "Kaohsiung(KHH)"]
AryDomDes3[8] = ["Sungsan(TSA)", "Taichung(RMQ)"]
AryDomDes3[9] = ["Sungsan(TSA)"]
AryDomDes3[10] = ["Sungsan(TSA)"]

OutputFile = open('B7.csv', 'wb')
writer = csv.writer(OutputFile)
for i in range(11):
    dep = AryDomThr3[i][-4:-1]
    for to in AryDomDes3[i]:
        to = to[-4:-1]
        writer.writerow([dep, to])
        print(dep, to)

OutputFile.close()

