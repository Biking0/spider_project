import csv


all_list = """CKG
WUH
TSN
HRB
SHA
SHE
SZX
HGH
SJW
KMG
CAN
DLC
XMN
MIG
CGQ
CTU
ZUH
LHW
BHY
CSX
BAS
TAO
SIA
CGD
URC
NNG
ZYI
ZHA
KWE
HET
YTY
NGB
SWA
SYX
SPK
OSA
HSG
HIJ
HND
TYO
NRT
NGO
AKJ
TAK
SEL
CJU
BKK
CNX
HKT
KBV
REP
HKG
MFM
KHH
TPE
SIN
PNH
JHB
SGN
URT
BKI"""
foreign = """SPK
OSA
HSG
HIJ
HND
TYO
NRT
NGO
AKJ
TAK
SEL
CJU
BKK
CNX
HKT
KBV
REP
HKG
MFM
KHH
TPE
SIN
PNH
JHB
SGN
URT
BKI"""
l = []
k = []
OutputFile = open('9C.csv', 'wb')
writer = csv.writer(OutputFile)
for x in all_list.split('\n'):
    for y in foreign.split('\n'):
        if x == y:
            continue
        l.append([x, y])
        l.append([y, x])
print(len(l))
for m in l:
    if m in k:
        continue
    k.append(m)
print(len(k))
for x in k:

    writer.writerow(x)
    print(x)

OutputFile.close()
