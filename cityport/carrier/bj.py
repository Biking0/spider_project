# -*- coding: utf-8 -*-
import csv,re,pprint



aaa = {
    'ALG':"""Tunis - Carthage (TUN)""",
    'DJE':"""Tunisia
Monastir - Habib Bourguiba (MIR)
France
Lille - Lesquin (LIL)
Lyon - Saint Exupéry (LYS)
Marseille - Provence (MRS)
Nantes - Atlantique (NTE)
Paris - Charles de Gaulle (CDG)
Toulouse - Blagnac (TLS)
Germany 
Berlin - Tegel (TXL)
Düsseldorf (DUS)
Frankfurt - am Main (FRA)
Hannover - Langenhagen (HAJ)
Leipzig - Halle (LEJ)
Munich - Franz Josef Strauß (MUC)
Stuttgart (STR)""",
    'MIR':"""Tunisia
Djerba - Zarzis (DJE)
Tunis - Carthage (TUN)
France
Lille - Lesquin (LIL)
Lyon - Saint Exupéry (LYS)
Marseille - Provence (MRS)
Nantes - Atlantique (NTE)
Nice - Cote d'Azur (NCE)
Paris - Charles de Gaulle (CDG)
Germany 
Berlin - Tegel (TXL)
Düsseldorf (DUS)
Frankfurt - am Main (FRA)
Hannover - Langenhagen (HAJ)
Leipzig - Halle (LEJ)
Munich - Franz Josef Strauß (MUC)
Stuttgart (STR)""",
    'TUN':"""Tunisia
Monastir - Habib Bourguiba (MIR)
Algeria 
Algiers - Houari Boumediene (ALG)
France
Lille - Lesquin (LIL)
Lyon - Saint Exupéry (LYS)
Marseille - Provence (MRS)
Nantes - Atlantique (NTE)
Nice - Cote d'Azur (NCE)
Paris - Charles de Gaulle (CDG)
Toulouse - Blagnac (TLS)""",
    'LIL':"""Tunisia
Djerba - Zarzis (DJE)
Monastir - Habib Bourguiba (MIR)
Tunis - Carthage (TUN)""",
    'LYS':"""Tunisia
Djerba - Zarzis (DJE)
Monastir - Habib Bourguiba (MIR)
Tunis - Carthage (TUN)""",
    'MRS':"""Tunisia
Djerba - Zarzis (DJE)
Monastir - Habib Bourguiba (MIR)
Tunis - Carthage (TUN)""",
    'NTE':"""Tunisia
Djerba - Zarzis (DJE)
Monastir - Habib Bourguiba (MIR)
Tunis - Carthage (TUN)""",
    'NCE':"""Tunisia
Monastir - Habib Bourguiba (MIR)
Tunis - Carthage (TUN)""",
    'CDG':"""Tunisia
Djerba - Zarzis (DJE)
Monastir - Habib Bourguiba (MIR)
Tunis - Carthage (TUN)""",
    'TLS':"""Tunisia
Djerba - Zarzis (DJE)
Tunis - Carthage (TUN)""",
    'TXL':"""Tunisia
Djerba - Zarzis (DJE)
Monastir - Habib Bourguiba (MIR)""",
    'DUS':"""Tunisia
Djerba - Zarzis (DJE)
Monastir - Habib Bourguiba (MIR)""",
    'FRA':"""Tunisia
Djerba - Zarzis (DJE)
Monastir - Habib Bourguiba (MIR)""",
    'HAJ':"""Tunisia
Djerba - Zarzis (DJE)
Monastir - Habib Bourguiba (MIR)""",
    'LEJ':"""Tunisia
Djerba - Zarzis (DJE)
Monastir - Habib Bourguiba (MIR)""",
    'MUC':"""Tunisia
Djerba - Zarzis (DJE)
Monastir - Habib Bourguiba (MIR)""",
    'STR':"""Tunisia
Djerba - Zarzis (DJE)
Monastir - Habib Bourguiba (MIR)""",
}

bbb_dict = {}
for k in aaa:
    # list = v.split('\n')
    s = re.compile('\((.{3})\)').findall(aaa.get(k))
    bbb_dict[k] = s

pprint.pprint(bbb_dict)
OutputFile = open('BJ.csv', 'wb')
writer = csv.writer(OutputFile)
vvv=[]
for bb in bbb_dict:
    dep = bb
    for to in bbb_dict.get(bb):
        if dep == to:
            continue
        vvv.append([dep, to])
vvv.sort()
for ss in vvv:
    writer.writerow([ss[0], ss[1]])
    print(ss[0], ss[1])

OutputFile.close()

