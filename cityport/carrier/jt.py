import requests

city_data = {
    'AEG',
    'AMD',
    'ARD',
    'AOR',
    'AMQ',
    'VPM',
    'ATQ',
    'LMU',
    'ABU',
    'BPN',
    'BJW',
    'BTJ',
    'TKG',
    'BDO',
    'DMK',
    'BDJ',
    'BWX',
    'BTH',
    'BTW',
    'BUW',
    'BKS',
    'BEJ',
    'BMU',
    'BNE',
    'WUB',
    'UOL',
    'CSX',
    'CTU',
    'MAA',
    'CNX',
    'CEI',
    'CGP',
    'CKG',
    'CXP',
    'CMB',
    'DPS',
    'DEX',
    'DEL',
    'DAC',
    'DOB',
    'DUM',
    'ENE',
    'FKQ',
    'GLX',
    'GTO',
    'CAN',
    'KWL',
    'GNS',
    'HFE',
    'HAK',
    'HGH',
    'HAN',
    'HDY',
    'HKG',
    'SGN',
    'IPH',
    'HLP',
    'CGK',
    'DJB',
    'DJJ',
    'JED',
    'JBB',
    'TNA',
    'JOG',
    'JHB',
    'KNG',
    'KWB',
    'KTM',
    'KDI',
    'KRC',
    'KTE',
    'KTG',
    'COK',
    'KBU',
    'KBR',
    'BKI',
    'KBV',
    'KUL',
    'TGG',
    'KCH',
    'KOE',
    'LBJ',
    'LAH',
    'LHE',
    'LGK',
    'LKA',
    'LTU',
    'LSW',
    'LOP',
    'LKI',
    'LUW',
    'MFM',
    'MED',
    'KJT',
    'MKZ',
    'MLG',
    'MWW',
    'MJU',
    'MDC',
    'MKW',
    'AMI',
    'MOF',
    'MES',
    'KNO',
    'MNA',
    'MEL',
    'MKQ',
    'MEQ',
    'MKF',
    'MYY',
    'OTI',
    'MOH',
    'MWS',
    'MPC',
    'BOM',
    'NBX',
    'NST',
    'NAM',
    'KHN',
    'NTX',
    'PDG',
    'PXA',
    'PKY',
    'PLM',
    'PLW',
    'LLO',
    'PGK',
    'PKN',
    'PKU',
    'PEN',
    'PER',
    'PNH',
    'HKT',
    'PUM',
    'PNK',
    'PSJ',
    'PSU',
    'RJM',
    'TXE',
    'RGT',
    'RTI',
    'SBG',
    'SMQ',
    'SQN',
    'SRI',
    'SXK',
    'SRG',
    'KSR',
    'YKR',
    'PVG',
    'SZX',
    'FLZ',
    'SMG',
    'DTB',
    'SIN',
    'SQG',
    'SOC',
    'SOQ',
    'SZB',
    'SWQ',
    'SUP',
    'SUB',
    'URT',
    'NAH',
    'TPE',
    'TMC',
    'TJQ',
    'TNJ',
    'TJS',
    'TJG',
    'TRK',
    'TWU',
    'TTE',
    'TSY',
    'TIM',
    'TRZ',
    'KAZ',
    'TLI',
    'TRV',
    'LUV',
    'UBP',
    'UTH',
    'UPG',
    'VTZ',
    'WGP',
    'WMX',
    'WNI',
    'WUH',
    'XIY',
    'RNG'
}

# 笛卡尔积
for i in city_data:
    for j in city_data:
        if i != j:
            print i + ',' + j
